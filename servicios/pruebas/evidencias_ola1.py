"""
evidencias_ola1.py — Casos de petición y respuesta de la Ola 1 (inventario, precios, proveedores,
abastecimiento y notificaciones). Los llama evidencias.py con las mismas herramientas (ev.caso, pg, rd, mg),
así que salen en el mismo informe, con lo que quedó en PostgreSQL después de cada petición.

Dejan la base como la encontraron en lo que se puede deshacer (existencias, mínimos, preferencias, listas y
proveedores de prueba); las solicitudes y órdenes de compra quedan como historia.
"""
import math
import uuid
from decimal import Decimal


def ejecutar_ola1(ev, h):
    pg, bd, NS = h.pg, h.bd, h.NS
    print("11. Inventario, precios, proveedores, abastecimiento y notificaciones (5111 a 5114 y 5124)")
    t_adm, t_plan, t_aud = ev.entrar("admin@codex.mx"), ev.entrar("planeador@codex.mx"), ev.entrar("auditor@codex.mx")
    t_op1, t_op2, t_cli = ev.entrar("operador.mh01@codex.mx"), ev.entrar("operador.mh02@codex.mx"), ev.entrar("juan.chapa1@correo.mx")

    def uno(sql, args=()):
        return bd.consultar(sql, args, una=True)

    def prod(clave):
        return uno("SELECT id, precio, categoria_id FROM producto WHERE clave_interna = %s", (clave,))

    hub1 = uno("SELECT id FROM microhub WHERE clave = 'MH-01'")["id"]
    hub2 = uno("SELECT id FROM microhub WHERE clave = 'MH-02'")["id"]
    zona1 = uno("SELECT id FROM zona WHERE clave = 'ZN-SB01'")["id"]
    op1_id = uno("SELECT id FROM usuario WHERE correo = 'operador.mh01@codex.mx'")["id"]

    def existencia(hub, pid, token=t_adm):
        r, _ = ev.http("inventario", "GET", f"inventario/{hub}/{pid}", token=token)
        return r.json if r.status == 200 else {"existencia": 0, "reservado": 0, "disponible": 0, "minimo": 0}

    def silencioso(servicio, metodo, ruta, cuerpo=None, token=None):
        """Un paso de preparación o limpieza que no se muestra como caso."""
        return ev.http(servicio, metodo, ruta, cuerpo, token=token)[0]

    # ================= INVENTARIO =================
    print("  Inventario (5111)")
    ab6, ab7, ab8, ab9 = prod("AB-006"), prod("AB-007"), prod("AB-008"), prod("AB-009")
    ev.caso("INV-01", "inventario", "Existencias por microhub", "Existencia física, reservada y disponible de cada producto.", "GET",
            "inventario?por_pagina=5", token=t_adm, verificar=lambda r: r.json["paginacion"]["total"] > 50 and r.json["datos"][0]["producto"]["nombre"],
            explicacion="Lee la vista v_inventario_disponible (existencia − reservas activas y vigentes). Los nombres de producto y microhub los "
                        "pide a los servicios de productos y microhubs, no los lee de sus tablas.",
            evidencia=lambda r: [pg("SELECT count(*) AS filas, sum(existencia) AS unidades, sum(reservado) AS reservado FROM v_inventario_disponible")])
    ev.caso("INV-02", "inventario", "Existencias (XML)", "La app de escritorio recibe XML que cumple inventario.xsd.", "GET",
            "inventario?por_pagina=3", token=t_adm, formato="xml", verificar=lambda r: "<existencias" in r.texto)
    ev.caso("INV-03", "inventario", "Filtro de estado inválido", "Un filtro desconocido se rechaza.", "GET", "inventario?estado=inventado",
            token=t_adm, esperado=400, verificar=lambda r: r.json["error"]["codigo"] == "FILTRO_INVALIDO")
    ev.caso("INV-04", "inventario", "El operador ve solo su microhub", "Ámbito por microhub del perfil operador.", "GET", "inventario?por_pagina=100",
            token=t_op1, verificar=lambda r: {e["microhub"]["id"] for e in r.json["datos"]} == {hub1})
    ev.caso("INV-05", "inventario", "El operador pide otro microhub", "No puede consultar el inventario de otro microhub.", "GET",
            f"inventario?microhub_id={hub2}", token=t_op1, esperado=403)
    ev.caso("INV-06", "inventario", "Una existencia", "Existencia, apartado y disponible de un producto en un microhub.", "GET",
            f"inventario/{hub1}/{ab6['id']}", token=t_op1, verificar=lambda r: r.json["disponible"] == r.json["existencia"] - r.json["reservado"])

    antes = existencia(hub1, ab6["id"])["existencia"]
    uid = str(uuid.uuid4())
    recepcion = {"microhub_id": hub1, "producto_id": ab6["id"], "tipo": "recepcion", "cantidad": 5, "motivo": "Llegada de mercancía",
                 "operacion_uuid": uid, "referencia": {"tipo": "orden_compra", "id": "1"}}
    ev.caso("INV-07", "inventario", "Recibir mercancía", "Suma al inventario y deja el movimiento con la referencia.", "POST", "inventario/movimientos",
            cuerpo=recepcion, token=t_op1, esperado=201, verificar=lambda r: r.json["movimiento"]["existencia_resultante"] == antes + 5,
            explicacion="Bloquea la fila del inventario, suma, y guarda el movimiento con la existencia resultante. La operacion_uuid hace el "
                        "movimiento idempotente.",
            evidencia=lambda r: [pg("SELECT id, tipo, cantidad, existencia_resultante, referencia_tipo, referencia_id, operacion_uuid FROM "
                                    "movimiento_inventario WHERE operacion_uuid = %s", (uid,)),
                                 pg("SELECT existencia FROM inventario WHERE microhub_id = %s AND producto_id = %s", (hub1, ab6["id"]))])
    ev.caso("INV-08", "inventario", "Reintento con la misma operación", "Idempotencia: la misma entrada no se aplica dos veces.", "POST",
            "inventario/movimientos", cuerpo=recepcion, token=t_op1, esperado=200, verificar=lambda r: r.json["duplicado"] is True,
            evidencia=lambda r: [pg("SELECT count(*) AS movimientos FROM movimiento_inventario WHERE operacion_uuid = %s", (uid,)),
                                 pg("SELECT existencia FROM inventario WHERE microhub_id = %s AND producto_id = %s", (hub1, ab6["id"]))])
    ev.caso("INV-09", "inventario", "Ajuste sin motivo", "Un ajuste, merma o conteo necesita el motivo.", "POST", "inventario/movimientos",
            cuerpo={"microhub_id": hub1, "producto_id": ab6["id"], "tipo": "ajuste", "cantidad": 1}, token=t_op1, esperado=422,
            verificar=lambda r: r.json["error"]["detalles"][0]["campo"] == "motivo")
    umbral = int(bd.parametro("umbral_ajuste_inventario", 25))
    grande = {"microhub_id": hub1, "producto_id": ab6["id"], "tipo": "ajuste", "cantidad": umbral + 5, "motivo": "Ajuste grande de prueba"}
    ev.caso("INV-10", "inventario", "Ajuste grande por un operador", f"Más de {umbral} unidades lo autoriza un administrador.", "POST",
            "inventario/movimientos", cuerpo=grande, token=t_op1, esperado=403,
            explicacion="El umbral viene de configuracion.umbral_ajuste_inventario, no de una constante en el código.")
    ev.caso("INV-11", "inventario", "Ajuste grande por un administrador", "El administrador sí puede.", "POST", "inventario/movimientos",
            cuerpo=grande, token=t_adm, esperado=201,
            evidencia=lambda r: [pg("SELECT tipo, cantidad, existencia_resultante, motivo, usuario_id FROM movimiento_inventario WHERE id = %s",
                                    (r.json["movimiento"]["id"],))])
    silencioso("inventario", "POST", "inventario/movimientos", {**grande, "cantidad": -(umbral + 5), "motivo": "Se regresa el ajuste de prueba"}, t_adm)
    silencioso("inventario", "POST", "inventario/movimientos", {**recepcion, "tipo": "merma", "operacion_uuid": None, "referencia": None,
                                                                "motivo": "Se regresa la recepción de prueba"}, t_adm)

    ao, ad = existencia(hub1, ab7["id"])["existencia"], existencia(hub2, ab7["id"])["existencia"]
    ut = str(uuid.uuid4())
    trans = {"origen_microhub_id": hub1, "destino_microhub_id": hub2, "producto_id": ab7["id"], "cantidad": 2,
             "motivo": "El microhub 2 se quedó sin producto", "operacion_uuid": ut}
    ev.caso("INV-12", "inventario", "Transferencia entre microhubs", "Resta del origen y suma al destino en una sola transacción.", "POST",
            "inventario/transferencias", cuerpo=trans, token=t_adm, esperado=201,
            verificar=lambda r: (r.json["origen"]["existencia"], r.json["destino"]["existencia"]) == (ao - 2, ad + 2),
            explicacion="Bloquea las dos filas en orden de microhub (sin interbloqueos) y escribe dos movimientos enlazados.",
            evidencia=lambda r: [pg("SELECT microhub_id, tipo, cantidad, existencia_resultante, referencia_tipo, referencia_id FROM "
                                    "movimiento_inventario WHERE operacion_uuid LIKE %s ORDER BY id", (ut + ":%",))])
    ev.caso("INV-13", "inventario", "Transferir más de lo disponible", "No se puede mandar lo que no hay.", "POST", "inventario/transferencias",
            cuerpo={**trans, "cantidad": ao + 1000, "operacion_uuid": str(uuid.uuid4())}, token=t_adm, esperado=409)
    silencioso("inventario", "POST", "inventario/transferencias",
               {**trans, "origen_microhub_id": hub2, "destino_microhub_id": hub1, "operacion_uuid": str(uuid.uuid4()),
                "motivo": "Se regresa la transferencia de prueba"}, t_adm)

    base = existencia(hub1, ab8["id"])
    ref = {"tipo": "manual", "id": "evidencia-" + uuid.uuid4().hex[:6]}
    r = ev.caso("INV-14", "inventario", "Apartar existencia", "Una reserva resta de lo disponible sin tocar la existencia física.", "POST",
                "inventario/reservas", cuerpo={"microhub_id": hub1, "producto_id": ab8["id"], "cantidad": 3, "referencia": ref}, token=t_op1,
                esperado=201, verificar=lambda r: r.json["estado"] == "activa" and r.json["vigente"] is True,
                evidencia=lambda r: [pg("SELECT existencia, reservado, disponible FROM v_inventario_disponible WHERE microhub_id = %s AND producto_id = %s",
                                        (hub1, ab8["id"]))])
    ev.caso("INV-15", "inventario", "Reservar más de lo disponible", "Responde 409 si no alcanza.", "POST", "inventario/reservas",
            cuerpo={"microhub_id": hub1, "producto_id": ab8["id"], "cantidad": base["disponible"] + 100, "referencia": ref}, token=t_op1, esperado=409)
    ev.caso("INV-16", "inventario", "Reservas activas", "Filtro por producto, estado y referencia.", "GET",
            f"inventario/reservas?producto_id={ab8['id']}&estado=activa&referencia_id={ref['id']}", token=t_adm,
            verificar=lambda r: r.json["paginacion"]["total"] == 1)
    if r is not None and r.status == 201:
        ev.caso("INV-17", "inventario", "Liberar una reserva", "Lo apartado vuelve a estar disponible.", "POST",
                f"inventario/reservas/{r.json['id']}/liberar", token=t_op1, verificar=lambda x: x.json["estado"] == "liberada",
                evidencia=lambda x: [pg("SELECT estado, cerrada_en IS NOT NULL AS cerrada FROM inventario_reserva WHERE id = %s", (r.json["id"],)),
                                     pg("SELECT existencia, reservado, disponible FROM v_inventario_disponible WHERE microhub_id = %s AND producto_id = %s",
                                        (hub1, ab8["id"]))])

    e9 = existencia(hub1, ab9["id"])
    r = ev.caso("INV-18", "inventario", "Cambiar el mínimo", "Solo un administrador cambia el mínimo de un producto.", "PATCH",
                f"inventario/{hub1}/{ab9['id']}/minimo", cuerpo={"minimo": e9["existencia"] - 1}, token=t_adm,
                verificar=lambda x: x.json["minimo"] == e9["existencia"] - 1,
                evidencia=lambda x: [pg("SELECT existencia, minimo FROM inventario WHERE microhub_id = %s AND producto_id = %s", (hub1, ab9["id"]))])
    ev.caso("INV-23", "inventario", "Cambiar el mínimo con PUT", "PUT es alias de PATCH: lo usa la app Android cuando la JVM no admite PATCH.", "PUT",
            f"inventario/{hub1}/{ab9['id']}/minimo", cuerpo={"minimo": e9["existencia"] - 1}, token=t_adm,
            verificar=lambda x: x.json["minimo"] == e9["existencia"] - 1,
            explicacion="Misma validación y misma auditoría que PATCH; el trigger registra quién cambió el mínimo.",
            evidencia=lambda x: [pg("SELECT modulo, accion, entidad, valores_nuevos FROM auditoria WHERE entidad = 'inventario' ORDER BY id DESC LIMIT 1")])
    ev.caso("INV-19", "inventario", "El operador intenta cambiar el mínimo", "Sin inventario.ajuste.", "PATCH",
            f"inventario/{hub1}/{ab9['id']}/minimo", cuerpo={"minimo": 1}, token=t_op1, esperado=403)
    ev.caso("INV-20", "inventario", "Una merma cruza el mínimo", "El trigger avisa del faltante al operador y al administrador.", "POST",
            "inventario/movimientos", cuerpo={"microhub_id": hub1, "producto_id": ab9["id"], "tipo": "merma", "cantidad": 2, "motivo": "Se rompieron dos"},
            token=t_adm, esperado=201,
            explicacion="fn_notificar_faltante se dispara cuando la existencia pasa de arriba a abajo del mínimo; el aviso respeta las preferencias.",
            evidencia=lambda x: [pg("SELECT destinatario_id, tipo, titulo, mensaje, referencia_tipo, referencia_id FROM web_notificacion "
                                    "WHERE tipo = 'inventario' AND referencia_id = %s ORDER BY id DESC LIMIT 2", (str(ab9["id"]),))])
    ev.caso("INV-21", "inventario", "Alertas de faltantes", "Productos agotados o bajo su mínimo, los más graves primero.", "GET",
            f"inventario/alertas?microhub_id={hub1}&por_pagina=100", token=t_adm,
            verificar=lambda x: any(a["producto"]["id"] == ab9["id"] and a["faltante"] == 1 for a in x.json["datos"]))
    ev.caso("INV-22", "inventario", "Movimientos de un producto", "Bitácora del producto con sus referencias.", "GET",
            f"inventario/movimientos?microhub_id={hub1}&producto_id={ab6['id']}&tipo=recepcion", token=t_adm,
            verificar=lambda x: x.json["paginacion"]["total"] >= 1)
    silencioso("inventario", "PATCH", f"inventario/{hub1}/{ab9['id']}/minimo", {"minimo": e9["minimo"]}, t_adm)
    silencioso("inventario", "POST", "inventario/movimientos",
               {"microhub_id": hub1, "producto_id": ab9["id"], "tipo": "recepcion", "cantidad": 2, "motivo": "Se regresa la merma de prueba"}, t_adm)

    # ================= NOTIFICACIONES =================
    print("  Notificaciones (5124)")
    marca = "Evidencia " + uuid.uuid4().hex[:6]
    r = ev.caso("NOT-01", "notificaciones", "Enviar un aviso a todo un rol", "El administrador avisa a los operadores de un microhub.", "POST",
                "notificaciones", cuerpo={"rol": "operador", "microhub_id": hub1, "tipo": "sistema", "titulo": marca,
                                          "mensaje": "Aviso de prueba para el microhub 1", "referencia": {"tipo": "sistema", "id": "evidencia"}},
                token=t_adm, esperado=201, verificar=lambda x: x.json["enviadas"] == 1 and x.json["omitidas"] == 0,
                evidencia=lambda x: [pg("SELECT destinatario_id, emisor_id, tipo, titulo, referencia_tipo, referencia_id FROM web_notificacion "
                                        "WHERE titulo = %s", (marca,))])
    ev.caso("NOT-02", "notificaciones", "Operador intenta enviar un aviso", "Sin notificaciones.crear.", "POST", "notificaciones",
            cuerpo={"rol": "operador", "tipo": "sistema", "titulo": "x", "mensaje": "x"}, token=t_op1, esperado=403)
    ev.caso("NOT-03", "notificaciones", "Destino inexistente", "Un rol sin personas activas se rechaza.", "POST", "notificaciones",
            cuerpo={"rol": "no_existe", "tipo": "sistema", "titulo": "x", "mensaje": "x"}, token=t_adm, esperado=422)
    ev.caso("NOT-04", "notificaciones", "Mi bandeja", "Los avisos de la persona, el más reciente primero.", "GET",
            "notificaciones?solo_no_leidas=true&por_pagina=20", token=t_op1, verificar=lambda x: any(a["titulo"] == marca for a in x.json["datos"]))
    ev.caso("NOT-05", "notificaciones", "Mi bandeja (XML)", "Respuesta XML que cumple notificaciones.xsd.", "GET", "notificaciones?por_pagina=3",
            token=t_op1, formato="xml", verificar=lambda x: "<notificaciones" in x.texto)
    ev.caso("NOT-06", "notificaciones", "Avisos sin leer", "Conteo para la insignia de la app.", "GET", "notificaciones/conteo", token=t_op1,
            verificar=lambda x: x.json["no_leidas"] >= 1)
    aviso = None
    if r is not None and r.status == 201:
        bandeja = ev.http("notificaciones", "GET", "notificaciones?por_pagina=50", token=t_op1)[0].json["datos"]
        aviso = next((a for a in bandeja if a["titulo"] == marca), None)
    if aviso:
        ev.caso("NOT-07", "notificaciones", "Confirmar la lectura", "El aviso queda leído.", "POST", f"notificaciones/{aviso['id']}/leer", token=t_op1,
                verificar=lambda x: x.json["leida"] is True,
                evidencia=lambda x: [pg("SELECT id, leido_en IS NOT NULL AS leido FROM web_notificacion WHERE id = %s", (aviso["id"],))])
        ev.caso("NOT-08", "notificaciones", "Leído por otra persona", "Un aviso ajeno no se puede marcar.", "POST", f"notificaciones/{aviso['id']}/leer",
                token=t_op2, esperado=404)
    ev.caso("NOT-09", "notificaciones", "Marcar todos como leídos", "Confirma la lectura de todos los pendientes.", "POST", "notificaciones/leer-todas",
            token=t_op1, verificar=lambda x: "marcadas" in x.json)
    ev.caso("NOT-10", "notificaciones", "Mis preferencias", "Qué tipos de aviso recibe la persona.", "GET", "notificaciones/preferencias", token=t_op1,
            verificar=lambda x: len(x.json["datos"]) == 5)
    ev.caso("NOT-11", "notificaciones", "Apagar un tipo de aviso", "El operador deja de recibir avisos de inventario.", "PUT",
            "notificaciones/preferencias/inventario", cuerpo={"activa": False}, token=t_op1, verificar=lambda x: x.json["activa"] is False,
            evidencia=lambda x: [pg("SELECT usuario_id, tipo, activa FROM notificacion_preferencia WHERE usuario_id = %s", (op1_id,))])
    ev.caso("NOT-12", "notificaciones", "Aviso omitido por preferencia", "Quien apagó el tipo no lo recibe y se cuenta como omitido.", "POST",
            "notificaciones", cuerpo={"rol": "operador", "microhub_id": hub1, "tipo": "inventario", "titulo": marca, "mensaje": "Faltante de prueba"},
            token=t_adm, esperado=200, verificar=lambda x: (x.json["enviadas"], x.json["omitidas"]) == (0, 1))
    ev.caso("NOT-13", "notificaciones", "Los avisos del sistema no se apagan", "El tipo sistema siempre llega.", "PUT",
            "notificaciones/preferencias/sistema", cuerpo={"activa": False}, token=t_op1, esperado=409)
    silencioso("notificaciones", "PUT", "notificaciones/preferencias/inventario", {"activa": True}, t_op1)
    if aviso:
        ev.caso("NOT-14", "notificaciones", "Borrar un aviso", "Quita el aviso de la bandeja propia.", "DELETE", f"notificaciones/{aviso['id']}",
                token=t_op1, esperado=204)

    # ================= PROVEEDORES =================
    print("  Proveedores (5113)")
    ev.caso("PRV-01", "proveedores", "Proveedores", "Lista con cobertura y calificación.", "GET", "proveedores?por_pagina=10", token=t_plan,
            verificar=lambda x: x.json["paginacion"]["total"] >= 3)
    ev.caso("PRV-02", "proveedores", "Proveedores (XML)", "Respuesta XML que cumple proveedores.xsd.", "GET", "proveedores?por_pagina=3",
            token=t_adm, formato="xml", verificar=lambda x: "<proveedores" in x.texto)
    ev.caso("PRV-03", "proveedores", "Un cliente intenta ver proveedores", "El perfil cliente no tiene proveedores.ver.", "GET", "proveedores",
            token=t_cli, esperado=403)
    regia = ev.http("proveedores", "GET", "proveedores?q=regia", token=t_adm)[0].json["datos"][0]
    ev.caso("PRV-04", "proveedores", "Un proveedor", "Con las zonas que cubre y su calificación.", "GET", f"proveedores/{regia['id']}", token=t_op1,
            verificar=lambda x: x.json["clave"] == "PV-02" and x.json["calificacion"] is not None)
    clave = "EV-" + uuid.uuid4().hex[:6].upper()
    nuevo = {"clave": clave, "nombre": "Proveedor de evidencias", "contacto": "Ana Prueba", "correo": "ana@prueba.example", "telefono": "8180000000",
             "dias_entrega": 3, "pedido_minimo": 250.0, "condiciones_pago": "Contado", "zonas": [1, 2]}
    r = ev.caso("PRV-05", "proveedores", "Dar de alta un proveedor", "Alta con su cobertura por zonas.", "POST", "proveedores", cuerpo=nuevo,
                token=t_adm, esperado=201, verificar=lambda x: x.json["zonas"] == [1, 2],
                evidencia=lambda x: [pg("SELECT p.id, p.clave, p.dias_entrega, p.pedido_minimo, array_agg(z.zona_id ORDER BY z.zona_id) AS zonas FROM proveedor p "
                                        "JOIN proveedor_zona z ON z.proveedor_id = p.id WHERE p.clave = %s GROUP BY p.id", (clave,)),
                                     pg("SELECT modulo, accion, entidad FROM auditoria WHERE entidad = 'proveedor' ORDER BY id DESC LIMIT 1")])
    ev.caso("PRV-06", "proveedores", "Clave repetida", "Dos proveedores no comparten clave.", "POST", "proveedores", cuerpo=nuevo, token=t_adm, esperado=409)
    ev.caso("PRV-07", "proveedores", "Correo inválido", "Validación con detalle por campo.", "POST", "proveedores",
            cuerpo={**nuevo, "clave": clave + "1", "correo": "sin-arroba"}, token=t_adm, esperado=422,
            verificar=lambda x: x.json["error"]["detalles"][0]["campo"] == "correo")
    ev.caso("PRV-08", "proveedores", "Un planeador intenta dar de alta", "Sin proveedores.editar.", "POST", "proveedores",
            cuerpo={**nuevo, "clave": clave + "2"}, token=t_plan, esperado=403)
    if r is not None and r.status == 201:
        sid = r.json["id"]
        ev.caso("PRV-09", "proveedores", "Modificar un proveedor", "Cambia el plazo y la cobertura; la clave no se toca.", "PUT", f"proveedores/{sid}",
                cuerpo={"dias_entrega": 5, "zonas": [3]}, token=t_adm, verificar=lambda x: x.json["dias_entrega"] == 5 and x.json["zonas"] == [3])
        ev.caso("PRV-21", "proveedores", "Corregir un dato con PATCH", "PATCH cambia solo los campos enviados; también acepta PUT.", "PATCH",
                f"proveedores/{sid}", cuerpo={"contacto": "Luis Prueba"}, token=t_adm,
                verificar=lambda x: x.json["contacto"] == "Luis Prueba" and x.json["dias_entrega"] == 5,
                evidencia=lambda x: [pg("SELECT clave, contacto, dias_entrega FROM proveedor WHERE id = %s", (sid,))])
        ev.caso("PRV-10", "proveedores", "Fijar una oferta", "Alta del precio de compra de un producto.", "PUT",
                f"proveedores/{sid}/catalogo/{ab6['id']}", cuerpo={"precio_compra": 0.05, "capacidad_semanal": 100, "minimo_compra": 5, "unidad_compra": "caja"},
                token=t_adm, verificar=lambda x: x.json["precio_compra"] == 0.05,
                evidencia=lambda x: [pg("SELECT proveedor_id, producto_id, precio_compra, capacidad_semanal, minimo_compra FROM proveedor_producto "
                                        "WHERE proveedor_id = %s", (sid,))])
        ev.caso("PRV-11", "proveedores", "Producto inexistente en la oferta", "La llave foránea rechaza el producto.", "PUT",
                f"proveedores/{sid}/catalogo/999999", cuerpo={"precio_compra": 1, "capacidad_semanal": 10}, token=t_adm, esperado=422)
        ev.caso("PRV-12", "proveedores", "Catálogo del proveedor", "Sus ofertas, con el nombre del producto.", "GET", f"proveedores/{sid}/catalogo",
                token=t_adm, verificar=lambda x: x.json["datos"][0]["producto"]["nombre"])
        ev.caso("PRV-13", "proveedores", "Evaluar al proveedor", "Un operador califica puntualidad, calidad y precio.", "POST",
                f"proveedores/{sid}/evaluaciones", cuerpo={"puntualidad": 5, "calidad": 4, "precio": 3, "comentario": "Llegó a tiempo"},
                token=t_op1, esperado=201,
                evidencia=lambda x: [pg("SELECT proveedor_id, puntualidad, calidad, precio, evaluado_por FROM proveedor_evaluacion WHERE proveedor_id = %s", (sid,))])
        ev.caso("PRV-14", "proveedores", "Evaluaciones y promedio", "Calificaciones recibidas y su promedio.", "GET", f"proveedores/{sid}/evaluaciones",
                token=t_adm, verificar=lambda x: x.json["promedio"]["general"] == 4.0)
        ev.caso("PRV-15", "proveedores", "Un auditor intenta evaluar", "El auditor solo consulta.", "POST", f"proveedores/{sid}/evaluaciones",
                cuerpo={"puntualidad": 5, "calidad": 5, "precio": 5}, token=t_aud, esperado=403)
    ev.caso("PRV-16", "proveedores", "Ofertas de un producto", "De la más barata a la más cara.", "GET", f"proveedores/ofertas?producto_id={ab6['id']}",
            token=t_op1, verificar=lambda x: [o["precio_compra"] for o in x.json["datos"]] == sorted(o["precio_compra"] for o in x.json["datos"]))
    ev.caso("PRV-17", "proveedores", "Mejor oferta de varios productos", "Una oferta, la más barata, por producto.", "GET",
            f"proveedores/ofertas?producto_ids={ab6['id']},{ab7['id']}&mejor=true", token=t_op1, verificar=lambda x: len(x.json["datos"]) == 2)
    ev.caso("PRV-18", "proveedores", "Ofertas sin indicar producto", "Falta producto_id o producto_ids.", "GET", "proveedores/ofertas", token=t_op1, esperado=400)
    if r is not None and r.status == 201:
        ev.caso("PRV-19", "proveedores", "Dar de baja un proveedor", "Baja lógica: ya no aparece en las ofertas.", "DELETE", f"proveedores/{sid}", token=t_adm,
                esperado=204, evidencia=lambda x: [pg("SELECT clave, estatus FROM proveedor WHERE id = %s", (sid,))])
        ev.caso("PRV-20", "proveedores", "Ofertas sin el proveedor de baja", "El proveedor dado de baja no ofrece.", "GET",
                f"proveedores/ofertas?producto_id={ab6['id']}", token=t_op1, verificar=lambda x: sid not in [o["proveedor"]["id"] for o in x.json["datos"]])
        for tabla in ("proveedor_zona", "proveedor_producto", "proveedor_evaluacion"):
            bd.consultar(f"DELETE FROM {tabla} WHERE proveedor_id = %s RETURNING 1", (sid,))
        bd.consultar("DELETE FROM proveedor WHERE id = %s RETURNING id", (sid,))

    # ================= PRECIOS =================
    print("  Precios (5112)")
    ab1, be1, ab2 = prod("AB-001"), prod("BE-001"), prod("AB-002")
    ev.caso("PRE-01", "precios", "Listas de precios", "Listas por zona y su vigencia.", "GET", "precios/listas", token=t_plan,
            verificar=lambda x: x.json["paginacion"]["total"] >= 1)
    ev.caso("PRE-02", "precios", "Listas (XML)", "Respuesta XML que cumple precios.xsd.", "GET", "precios/listas", token=t_adm, formato="xml",
            verificar=lambda x: "<listas" in x.texto)
    ev.caso("PRE-03", "precios", "Un cliente intenta ver las listas", "Sin precios.ver.", "GET", "precios/listas", token=t_cli, esperado=403)
    nombre = "Lista de evidencias " + uuid.uuid4().hex[:6]
    lista = {"nombre": nombre, "zona_id": 3, "vigente_desde": "2027-01-01", "vigente_hasta": "2027-01-31",
             "items": [{"producto_id": ab2["id"], "precio": 50.0, "costo": 30.0}]}
    r = ev.caso("PRE-04", "precios", "Crear una lista", "Lista de una zona con un precio y su costo.", "POST", "precios/listas", cuerpo=lista, token=t_adm,
                esperado=201, verificar=lambda x: x.json["items"][0]["margen_pct"] == 40.0,
                explicacion="Margen = (precio − costo) / precio = (50 − 30) / 50 = 40 %.",
                evidencia=lambda x: [pg("SELECT l.id, l.nombre, l.zona_id, l.vigente_desde, l.vigente_hasta, i.producto_id, i.precio, i.costo FROM lista_precio l "
                                        "JOIN lista_precio_item i ON i.lista_id = l.id WHERE l.nombre = %s", (nombre,))])
    ev.caso("PRE-05", "precios", "Listas que se traslapan", "Una zona no tiene dos listas vigentes a la vez.", "POST", "precios/listas",
            cuerpo={**lista, "nombre": nombre + " bis", "vigente_desde": "2027-01-15", "vigente_hasta": "2027-02-15"}, token=t_adm, esperado=409)
    if r is not None and r.status == 201:
        lid = r.json["id"]
        ev.caso("PRE-06", "precios", "Cambiar el precio de un producto", "Sube el precio de 50 a 52; el costo se conserva.", "PUT",
                f"precios/listas/{lid}/items/{ab2['id']}", cuerpo={"precio": 52.0}, token=t_adm,
                verificar=lambda x: x.json["precio"] == 52.0 and x.json["costo"] == 30.0,
                evidencia=lambda x: [pg("SELECT precio_anterior, precio_nuevo, usuario_id FROM lista_precio_historico WHERE lista_id = %s ORDER BY id", (lid,))])
        ev.caso("PRE-07", "precios", "Historial de cambios", "Cada cambio de precio queda registrado por un trigger.", "GET",
                f"precios/historial?lista_id={lid}&producto_id={ab2['id']}", token=t_aud,
                verificar=lambda x: [(c["precio_anterior"], c["precio_nuevo"]) for c in x.json["datos"]] == [(50.0, 52.0), (None, 50.0)])
        ev.caso("PRE-08", "precios", "Una lista con sus márgenes", "Precios, costos y margen de cada renglón.", "GET", f"precios/listas/{lid}", token=t_plan,
                verificar=lambda x: x.json["items"][0]["margen_pct"] == 42.3)
        ev.caso("PRE-09", "precios", "Precio dentro de la vigencia", "Rige el precio de la lista de la zona.", "GET",
                f"precios/vigente?producto_id={ab2['id']}&zona_id=3&fecha=2027-01-15", token=t_cli,
                verificar=lambda x: x.json["precio_vigente"] == 52.0 and x.json["lista"]["id"] == lid)
        ev.caso("PRE-10", "precios", "Precio fuera de la vigencia", "Sin lista vigente rige el precio base del catálogo.", "GET",
                f"precios/vigente?producto_id={ab2['id']}&zona_id=3&fecha=2026-10-19", token=t_cli,
                verificar=lambda x: x.json["lista"] is None and x.json["precio_vigente"] == x.json["precio_base"])
        bd.consultar("UPDATE lista_precio SET estatus = 'inactivo' WHERE id = %s RETURNING id", (lid,))
    ev.caso("PRE-11", "precios", "Precio con lista de la zona", "Precio base, lista, promoción y margen de un producto.", "GET",
            f"precios/vigente?producto_id={ab1['id']}&zona_id={zona1}", token=t_cli,
            verificar=lambda x: x.json["lista"]["nombre"] == "Lista San Bernabé Centro",
            explicacion="Lista de la zona sobre el precio base, luego una sola promoción (la de mayor descuento), luego el margen si hay costo.")
    ev.caso("PRE-12", "precios", "Precio con promoción", "Bebidas con 10 % de descuento.", "GET",
            f"precios/vigente?producto_id={be1['id']}&zona_id={zona1}", token=t_cli,
            verificar=lambda x: x.json["promocion"]["nombre"] == "Bebidas -10 %" and x.json["descuento"] > 0)
    ev.caso("PRE-13", "precios", "Calcular un pedido", "Precio final, descuento e importe de cada línea.", "POST", "precios/calcular",
            cuerpo={"zona_id": zona1, "lineas": [{"producto_id": ab1["id"], "cantidad": 2}, {"producto_id": be1["id"], "cantidad": 3}]}, token=t_cli,
            verificar=lambda x: abs(sum(l["importe"] for l in x.json["lineas"]) - x.json["total"]) < 0.01)
    ev.caso("PRE-14", "precios", "Calcular un producto inexistente", "Validación con detalle por línea.", "POST", "precios/calcular",
            cuerpo={"lineas": [{"producto_id": 999999, "cantidad": 1}]}, token=t_cli, esperado=422)
    ev.caso("PRE-15", "precios", "Promoción que pasa del descuento máximo", "Un porcentaje mayor al tope de la configuración se rechaza.", "POST",
            "precios/promociones", cuerpo={"nombre": "Promoción excesiva", "tipo": "porcentaje", "valor": 31.0, "producto_id": ab1["id"],
                                          "vigente_hasta": "2030-12-31"}, token=t_adm, esperado=422)
    r = ev.caso("PRE-16", "precios", "Crear una promoción", "Descuento de $2 en un producto.", "POST", "precios/promociones",
                cuerpo={"nombre": "Promoción de evidencias " + uuid.uuid4().hex[:4], "tipo": "monto", "valor": 2.0, "producto_id": ab1["id"],
                        "vigente_hasta": "2030-12-31"}, token=t_adm, esperado=201,
                evidencia=lambda x: [pg("SELECT id, nombre, tipo, valor, producto_id, vigente_hasta, estatus FROM promocion WHERE id = %s", (x.json["id"],))])
    if r is not None and r.status == 201:
        ev.caso("PRE-17", "precios", "Promociones vigentes", "Filtro por producto.", "GET", f"precios/promociones?vigente=true&producto_id={ab1['id']}",
                token=t_plan, verificar=lambda x: r.json["id"] in [p["id"] for p in x.json["datos"]])
        ev.caso("PRE-18", "precios", "Dar de baja la promoción", "Baja lógica.", "DELETE", f"precios/promociones/{r.json['id']}", token=t_adm, esperado=204,
                evidencia=lambda x: [pg("SELECT id, estatus FROM promocion WHERE id = %s", (r.json["id"],))])
    ev.caso("PRE-19", "precios", "Márgenes", "Renglones con costo, del margen más bajo al más alto.", "GET", "precios/margenes?por_pagina=5", token=t_plan,
            verificar=lambda x: x.json["datos"] and x.json["datos"][0]["margen_pct"] <= x.json["datos"][-1]["margen_pct"])
    ev.caso("PRE-20", "precios", "Sensibilidad al precio", "Qué pasa con ingreso y margen si el precio sube o baja.", "GET",
            f"precios/sensibilidad?producto_id={ab1['id']}&zona_id={zona1}&volumen_base=100&elasticidad=-1.2", token=t_plan,
            verificar=lambda x: next(e for e in x.json["escenarios"] if e["variacion_pct"] == 10)["volumen_estimado"] == 88.0,
            explicacion="volumen = base × (1 + elasticidad × variación). Con elasticidad −1.2, un precio 10 % más alto baja el volumen 12 % (100 → 88). "
                        "La elasticidad es un supuesto; la respuesta lo dice en el campo `supuestos`.")
    ev.caso("PRE-21", "precios", "Elasticidad fuera de rango", "La elasticidad va de −10 a 0.", "GET",
            f"precios/sensibilidad?producto_id={ab1['id']}&elasticidad=1", token=t_plan, esperado=400)

    # ================= ABASTECIMIENTO =================
    print("  Abastecimiento (5114)")
    pv01 = uno("SELECT id FROM proveedor WHERE clave = 'PV-01'")["id"]
    ab10, ab15 = prod("AB-010"), prod("AB-015")
    unitario = Decimal(str(ab10["precio"])) * Decimal("0.70")
    qty = max(12, math.ceil(Decimal(850) / unitario))
    e15 = existencia(hub1, ab15["id"])
    silencioso("inventario", "PATCH", f"inventario/{hub1}/{ab15['id']}/minimo", {"minimo": e15["disponible"] + 20}, t_adm)
    ev.caso("ABA-01", "abastecimiento", "Necesidades de reposición", "Productos bajo su mínimo, con la mejor oferta.", "GET",
            "abastecimiento/necesidades?por_pagina=100", token=t_op1,
            verificar=lambda x: any(n["producto"]["id"] == ab15["id"] and n["mejor_oferta"] for n in x.json["datos"]),
            explicacion="Pide las alertas al servicio de inventario y la mejor oferta al de proveedores (HTTP con el mismo JWT). "
                        "Sugiere llegar a 3 × el mínimo, sin contar lo que ya viene en camino ni lo ya solicitado.")
    silencioso("inventario", "PATCH", f"inventario/{hub1}/{ab15['id']}/minimo", {"minimo": e15["minimo"]}, t_adm)
    ev.caso("ABA-02", "abastecimiento", "Necesidades sin indicar el microhub", "El administrador debe elegir un microhub.", "GET",
            "abastecimiento/necesidades", token=t_adm, esperado=400)
    r = ev.caso("ABA-03", "abastecimiento", "Pedir mercancía", "El operador pide reposición de su microhub.", "POST", "abastecimiento/solicitudes",
                cuerpo={"microhub_id": hub1, "motivo": "Se acabó el producto el fin de semana", "lineas": [{"producto_id": ab10["id"], "cantidad": qty}]},
                token=t_op1, esperado=201, verificar=lambda x: x.json["estado"] == "pendiente",
                evidencia=lambda x: [pg("SELECT id, folio, microhub_id, estado, solicitada_por FROM solicitud_compra WHERE id = %s", (x.json["id"],)),
                                     pg("SELECT destinatario_id, tipo, titulo, referencia_tipo FROM web_notificacion WHERE tipo = 'abastecimiento' "
                                        "AND referencia_tipo = 'solicitud' AND referencia_id = %s", (str(x.json["id"]),))])
    ev.caso("ABA-04", "abastecimiento", "Pedir para otro microhub", "El operador solo trabaja con el suyo.", "POST", "abastecimiento/solicitudes",
            cuerpo={"microhub_id": hub2, "lineas": [{"producto_id": ab10["id"], "cantidad": 12}]}, token=t_op1, esperado=403)
    ev.caso("ABA-05", "abastecimiento", "Producto repetido en la solicitud", "Un producto aparece una sola vez.", "POST", "abastecimiento/solicitudes",
            cuerpo={"microhub_id": hub1, "lineas": [{"producto_id": ab10["id"], "cantidad": 1}, {"producto_id": ab10["id"], "cantidad": 2}]},
            token=t_op1, esperado=422)
    if r is not None and r.status == 201:
        sid = r.json["id"]
        ev.caso("ABA-06", "abastecimiento", "Solicitud de otro microhub", "Otro operador no la ve.", "GET", f"abastecimiento/solicitudes/{sid}", token=t_op2,
                esperado=404)
        ev.caso("ABA-07", "abastecimiento", "Aprobar sin permiso", "Solo el administrador decide.", "POST", f"abastecimiento/solicitudes/{sid}/decision",
                cuerpo={"decision": "aprobada"}, token=t_op1, esperado=403)
        ev.caso("ABA-08", "abastecimiento", "Rechazar sin motivo", "Rechazar exige el motivo.", "POST", f"abastecimiento/solicitudes/{sid}/decision",
                cuerpo={"decision": "rechazada"}, token=t_adm, esperado=422)
        ev.caso("ABA-09", "abastecimiento", "Ordenar antes de aprobar", "Solo se ordena una solicitud aprobada.", "POST",
                f"abastecimiento/solicitudes/{sid}/ordenar", cuerpo={"proveedor_id": pv01}, token=t_adm, esperado=409)
        ev.caso("ABA-10", "abastecimiento", "Aprobar la solicitud", "El administrador aprueba y quien pidió recibe el aviso.", "POST",
                f"abastecimiento/solicitudes/{sid}/decision", cuerpo={"decision": "aprobada", "motivo": "Hay presupuesto"}, token=t_adm,
                verificar=lambda x: x.json["estado"] == "aprobada",
                evidencia=lambda x: [pg("SELECT estado, decidida_por, decision_motivo FROM solicitud_compra WHERE id = %s", (sid,)),
                                     pg("SELECT destinatario_id, titulo, mensaje FROM web_notificacion WHERE referencia_tipo = 'solicitud' "
                                        "AND referencia_id = %s AND destinatario_id = %s", (str(sid), op1_id))])
        r2 = ev.caso("ABA-11", "abastecimiento", "Emitir la orden de compra", "Cada línea va al proveedor indicado; el total es piezas × precio de compra.", "POST",
                     f"abastecimiento/solicitudes/{sid}/ordenar", cuerpo={"proveedor_id": pv01}, token=t_adm, esperado=201,
                     verificar=lambda x: len(x.json["ordenes"]) == 1 and x.json["ordenes"][0]["estado"] == "emitida",
                     evidencia=lambda x: [pg("SELECT o.id, o.folio, o.estado, o.fecha_esperada, o.total, l.producto_id, l.cantidad, l.precio_compra FROM orden_compra o "
                                             "JOIN orden_compra_linea l ON l.orden_id = o.id WHERE o.solicitud_id = %s", (sid,)),
                                          pg("SELECT estado FROM solicitud_compra WHERE id = %s", (sid,))])
        ev.caso("ABA-12", "abastecimiento", "Ordenar dos veces", "La solicitud ya quedó ordenada.", "POST", f"abastecimiento/solicitudes/{sid}/ordenar",
                cuerpo={"proveedor_id": pv01}, token=t_adm, esperado=409)
        if r2 is not None and r2.status == 201:
            oid = r2.json["ordenes"][0]["id"]
            antes = existencia(hub1, ab10["id"])["existencia"]
            mitad = qty // 2
            lote = str(uuid.uuid4())
            recep = {"operacion_uuid": lote, "nota": "Llegó la primera caja", "lineas": [{"producto_id": ab10["id"], "cantidad": mitad}]}
            ev.caso("ABA-13", "abastecimiento", "Recepción parcial", "La mercancía que llegó entra al inventario.", "POST",
                    f"abastecimiento/ordenes/{oid}/recepcion", cuerpo=recep, token=t_op1, esperado=201,
                    verificar=lambda x: x.json["orden"]["estado"] == "parcial" and x.json["aplicadas"] == 1,
                    explicacion="Guarda la recepción, llama a POST /inventario/movimientos con la operacion_uuid del lote y marca la entrada como aplicada.",
                    evidencia=lambda x: [pg("SELECT producto_id, cantidad, operacion_uuid, aplicada FROM orden_compra_recepcion WHERE orden_id = %s", (oid,)),
                                         pg("SELECT tipo, cantidad, existencia_resultante, referencia_tipo, referencia_id FROM movimiento_inventario "
                                            "WHERE operacion_uuid = %s", (f"{lote}:{ab10['id']}",)),
                                         pg("SELECT estado FROM orden_compra WHERE id = %s", (oid,))])
            ev.caso("ABA-14", "abastecimiento", "Repetir la misma recepción", "No entra dos veces al inventario.", "POST",
                    f"abastecimiento/ordenes/{oid}/recepcion", cuerpo=recep, token=t_op1, esperado=201, verificar=lambda x: x.json["aplicadas"] == 0,
                    evidencia=lambda x: [pg("SELECT existencia FROM inventario WHERE microhub_id = %s AND producto_id = %s", (hub1, ab10["id"]))])
            ev.caso("ABA-15", "abastecimiento", "Recibir más de lo pedido", "Solo falta lo que no ha llegado.", "POST",
                    f"abastecimiento/ordenes/{oid}/recepcion", cuerpo={"lineas": [{"producto_id": ab10["id"], "cantidad": qty - mitad + 1}]},
                    token=t_op1, esperado=422)
            ev.caso("ABA-16", "abastecimiento", "Cancelar una orden con mercancía recibida", "Solo se cancela una orden sin recepciones.", "POST",
                    f"abastecimiento/ordenes/{oid}/cancelar", cuerpo={"motivo": "Ya llegó"}, token=t_adm, esperado=409)
            ev.caso("ABA-17", "abastecimiento", "Recepción final", "Llega el resto: la orden queda recibida y avisa.", "POST",
                    f"abastecimiento/ordenes/{oid}/recepcion", cuerpo={"lineas": [{"producto_id": ab10["id"], "cantidad": qty - mitad}]}, token=t_op1,
                    esperado=201, verificar=lambda x: x.json["orden"]["estado"] == "recibida" and x.json["pendientes"] == 0,
                    evidencia=lambda x: [pg("SELECT estado, cerrada_en IS NOT NULL AS cerrada FROM orden_compra WHERE id = %s", (oid,)),
                                         pg("SELECT existencia FROM inventario WHERE microhub_id = %s AND producto_id = %s", (hub1, ab10["id"])),
                                         pg("SELECT destinatario_id, titulo, mensaje FROM web_notificacion WHERE referencia_tipo = 'orden' AND referencia_id = %s",
                                            (str(oid),))])
            ev.caso("ABA-18", "abastecimiento", "Recibir en una orden ya recibida", "Una orden recibida no admite más mercancía.", "POST",
                    f"abastecimiento/ordenes/{oid}/recepcion", cuerpo={"lineas": [{"producto_id": ab10["id"], "cantidad": 1}]}, token=t_op1, esperado=409)
            ev.caso("ABA-19", "abastecimiento", "Una orden", "Con lo recibido de cada línea.", "GET", f"abastecimiento/ordenes/{oid}", token=t_op1,
                    verificar=lambda x: x.json["lineas"][0]["cantidad_recibida"] == qty)
            ev.caso("ABA-20", "abastecimiento", "Órdenes recibidas (XML)", "Respuesta XML que cumple abastecimiento.xsd.", "GET",
                    "abastecimiento/ordenes?estado=recibida", token=t_op1, formato="xml", verificar=lambda x: "<ordenes" in x.texto)
    ev.caso("ABA-21", "abastecimiento", "Tablero de abastecimiento", "Solicitudes y órdenes por estado.", "GET", "abastecimiento/seguimiento", token=t_op1,
            verificar=lambda x: x.json["microhub_id"] == hub1 and x.json["ordenes"]["recibida"] >= 1)

    # una orden que se cancela
    s2 = ev.http("abastecimiento", "POST", "abastecimiento/solicitudes",
                 {"microhub_id": hub1, "motivo": "Compra para cancelar", "lineas": [{"producto_id": ab10["id"], "cantidad": qty}]}, token=t_op1)[0]
    if s2.status == 201:
        silencioso("abastecimiento", "POST", f"abastecimiento/solicitudes/{s2.json['id']}/decision", {"decision": "aprobada", "motivo": "Hay presupuesto"}, t_adm)
        o2 = ev.http("abastecimiento", "POST", f"abastecimiento/solicitudes/{s2.json['id']}/ordenar", {"proveedor_id": pv01}, token=t_adm)[0]
        if o2.status == 201:
            oid2 = o2.json["ordenes"][0]["id"]
            ev.caso("ABA-22", "abastecimiento", "Cancelar sin permiso", "Cancelar una orden es del administrador.", "POST",
                    f"abastecimiento/ordenes/{oid2}/cancelar", cuerpo={"motivo": "No hace falta"}, token=t_op1, esperado=403)
            ev.caso("ABA-23", "abastecimiento", "Cancelar una orden emitida", "Una orden sin recepciones se puede cancelar con motivo.", "POST",
                    f"abastecimiento/ordenes/{oid2}/cancelar", cuerpo={"motivo": "El proveedor ya no surte"}, token=t_adm,
                    verificar=lambda x: x.json["estado"] == "cancelada",
                    evidencia=lambda x: [pg("SELECT estado, motivo_cancelacion, cerrada_en IS NOT NULL AS cerrada FROM orden_compra WHERE id = %s", (oid2,))])
            ev.caso("ABA-24", "abastecimiento", "Recibir en una orden cancelada", "No recibe mercancía.", "POST", f"abastecimiento/ordenes/{oid2}/recepcion",
                    cuerpo={"lineas": [{"producto_id": ab10["id"], "cantidad": 1}]}, token=t_op1, esperado=409)
    ev.caso("ABA-25", "abastecimiento", "Solicitudes (XML)", "Respuesta XML que cumple abastecimiento.xsd.", "GET", "abastecimiento/solicitudes?por_pagina=3",
            token=t_adm, formato="xml", verificar=lambda x: "<solicitudes" in x.texto)
    ev.caso("ABA-26", "abastecimiento", "Un auditor consulta", "El auditor ve las solicitudes sin poder crear.", "GET", "abastecimiento/solicitudes", token=t_aud)
    ev.caso("ABA-27", "abastecimiento", "Un cliente consulta", "El cliente no tiene abastecimiento.ver.", "GET", "abastecimiento/solicitudes", token=t_cli, esperado=403)
