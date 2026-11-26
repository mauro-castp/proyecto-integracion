"""
evidencias_ola3.py — Casos de petición y respuesta de la Ola 3: auditoría y monitoreo (5126), reportes (5123) y sincronización (5125). Los llama
evidencias.py con las mismas herramientas (ev.caso, pg, rd, mg), así que salen en el mismo informe, con lo que quedó en PostgreSQL y MongoDB.

Dejan la base como la encontraron en lo que se puede deshacer: el umbral de latencia vuelve a su valor y las alertas que la prueba abre se
cierran con una verificación. La entrega que usa la sincronización se cierra como fallida (el inventario regresa).
"""
import base64
import datetime as dt
import uuid

JPEG = bytes([0xFF, 0xD8, 0xFF, 0xE0, 0, 16, 74, 70, 73, 70, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0]) + bytes(range(256))


def ejecutar_ola3(ev, h):
    pg, bd, xml = h.pg, h.bd, h.xml
    from pruebas.preparar_entregas import preparar
    print("14. Ola 3: auditoría y monitoreo, reportes y sincronización (5123, 5125 y 5126)")
    t_adm, t_aud, t_plan = ev.entrar("admin@codex.mx"), ev.entrar("auditor@codex.mx"), ev.entrar("planeador@codex.mx")
    t_op1, t_rep, t_cli = ev.entrar("operador.mh01@codex.mx"), ev.entrar("repartidor1@codex.mx"), ev.entrar("juan.chapa1@correo.mx")

    def uno(sql, args=()):
        return bd.consultar(sql, args, una=True)

    def ejecutar(sql, args=()):
        with bd.conexion() as con, con.cursor() as cur:
            cur.execute(sql, args)

    def silencioso(servicio, metodo, ruta, cuerpo=None, token=None):
        return ev.http(servicio, metodo, ruta, cuerpo, token=token)[0]

    def hace(minutos):
        return (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=minutos)).isoformat()

    am, rp, sy = "auditoria-monitoreo", "reportes", "sincronizacion"
    # ================= ARCHIVOS CON ENLACE FIRMADO (documentos, 5107) =================
    print("  Enlaces firmados de documentos (5107)")
    pdf = b"%PDF-1.4 evidencia de enlace firmado %%EOF"
    did = silencioso("documentos", "POST", "documentos", {"nombre": "evidencia-enlace.pdf", "tipo_mime": "application/pdf",
                     "contenido_base64": base64.b64encode(pdf).decode(), "referencia": {"tipo": "usuario", "id": "7"}}, token=t_rep).json["id"]
    r = ev.caso("ENL-01", "documentos", "Pedir un enlace de descarga firmado", "URL de un solo método y con caducidad para bajar el archivo del almacén.", "GET",
                f"documentos/{did}/enlace", token=t_rep, verificar=lambda r: r.json["segundos"] > 0 and r.json["metodo"] == "GET",
                explicacion="En la nube la URL es una firmada V4 de Cloud Storage; en local apunta al propio servicio. La base de datos no guarda el archivo.",
                evidencia=lambda r: [pg("SELECT fecha, modulo, accion, detalle FROM auditoria WHERE entidad = 'documento' AND entidad_id = %s ORDER BY id", (did,))])
    if r is not None and r.status == 200 and "/api/v1/documentos/descarga" in r.json["url_firmada"]:
        ruta = r.json["url_firmada"].split("/api/v1/", 1)[1]
        ev.caso("ENL-02", "documentos", "Descargar con el enlace firmado", "El enlace funciona sin token: la firma es el permiso.", "GET", ruta,
                verificar=lambda x: x.texto.startswith("%PDF"))
        ev.caso("ENL-03", "documentos", "Enlace manipulado", "Cambiar un carácter de la firma lo invalida.", "GET", ruta[:-2] + ("AA" if ruta[-2:] != "AA" else "BB"),
                esperado=403, verificar=lambda x: x.json["error"]["codigo"] == "PROHIBIDO")
    silencioso("documentos", "DELETE", f"documentos/{did}", token=t_rep)

    # ================= MONITOREO =================
    print("  Monitoreo (5126)")
    ev.caso("MNT-01", am, "Forzar una verificación de todos los servicios", "Pregunta la salud de cada servicio y guarda el resultado.", "POST",
            "monitoreo/verificaciones", cuerpo={}, token=t_adm, esperado=201,
            verificar=lambda r: r.json["caidos"] == 0 and r.json["verificados"] >= 26,
            explicacion="Cada 30 s se hace sola; con dos procesos, un candado en Redis deja que solo uno verifique.",
            evidencia=lambda r: [pg("SELECT estado, count(*) AS verificaciones, round(avg(tiempo_ms), 1) AS ms_promedio FROM monitoreo_verificacion "
                                    "WHERE verificado_en > now() - interval '1 minute' GROUP BY estado")])
    ev.caso("MNT-02", am, "Panel de monitoreo", "Estado, última verificación, tiempo, versión, dependencias, errores y disponibilidad de cada servicio.", "GET",
            "monitoreo/estado", token=t_aud, verificar=lambda r: r.json["resumen"]["total"] >= 26 and r.json["resumen"]["monitor_activo"])
    ev.caso("MNT-03", am, "Panel en XML", "El mismo panel validado contra auditoria_monitoreo.xsd.", "GET", "monitoreo/estado", token=t_adm, formato="xml",
            verificar=lambda r: "<monitoreo_estado" in r.texto)
    ev.caso("MNT-04", am, "Historial de un servicio", "Serie de verificaciones, la más reciente primero.", "GET", "monitoreo/servicios/pedidos/historial?por_pagina=3",
            token=t_adm, verificar=lambda r: r.json["datos"] and r.json["datos"][0]["estado"] == "ok")
    ev.caso("MNT-05", am, "Disponibilidad de las últimas 24 horas", "Porcentaje disponible, salud plena y percentiles p50 y p95.", "GET",
            "monitoreo/disponibilidad?horas=24", token=t_adm, verificar=lambda r: r.json["objetivo_pct"] == 99.0)
    ev.caso("MNT-06", am, "Tráfico y errores", "Peticiones, errores y percentiles de duración por servicio, desde MongoDB.", "GET", "monitoreo/metricas?minutos=60",
            token=t_adm, verificar=lambda r: r.json["peticiones_total"] > 0)
    ev.caso("MNT-07", am, "Umbrales y su justificación", "Cada umbral con su origen y cómo se calibra.", "GET", "monitoreo/supuestos", token=t_plan,
            verificar=lambda r: any(s["clave"] == "mon_latencia_ms" for s in r.json["datos"]))
    # una alerta real: se baja el umbral de latencia, se verifica un servicio y después se restaura
    antes = uno("SELECT valor FROM configuracion WHERE clave = 'mon_latencia_ms' AND ambito = 'global'")["valor"]
    try:
        ejecutar("UPDATE configuracion SET valor = '0' WHERE clave = 'mon_latencia_ms' AND ambito = 'global'")
        silencioso(am, "POST", "monitoreo/verificaciones", {"servicio": "zonas"}, token=t_adm)
        r = ev.caso("MNT-08", am, "Alertas abiertas", "Con el umbral de latencia en 0 ms, la verificación abre una alerta real.", "GET",
                    "monitoreo/alertas?estado=abiertas&servicio=zonas", token=t_adm, verificar=lambda r: r.json["paginacion"]["total"] >= 1,
                    evidencia=lambda r: [pg("SELECT servicio, tipo, severidad, detalle FROM monitoreo_alerta WHERE cerrada_en IS NULL AND servicio = 'zonas'")])
        if r is not None and r.status == 200 and r.json["datos"]:
            aid = r.json["datos"][0]["id"]
            ev.caso("MNT-09", am, "Reconocer una alerta", "Queda quién se hizo cargo y cuándo.", "POST", f"monitoreo/alertas/{aid}/reconocer", cuerpo={}, token=t_adm,
                    verificar=lambda r: r.json["reconocida"]["por"]["id"] == 1,
                    evidencia=lambda r: [pg("SELECT fecha, accion, detalle, usuario_id FROM auditoria WHERE entidad = 'monitoreo_alerta' AND entidad_id = %s ORDER BY id", (str(aid),))])
            ev.caso("MNT-10", am, "Reconocer sin permiso", "El auditor ve el monitoreo pero no lo opera.", "POST", f"monitoreo/alertas/{aid}/reconocer", cuerpo={},
                    token=t_aud, esperado=403)
    finally:
        ejecutar("UPDATE configuracion SET valor = %s WHERE clave = 'mon_latencia_ms' AND ambito = 'global'", (antes,))
        silencioso(am, "POST", "monitoreo/verificaciones", {}, token=t_adm)
    ev.caso("MNT-11", am, "El operador no ve el monitoreo", "Sin monitoreo.ver.", "GET", "monitoreo/estado", token=t_op1, esperado=403)

    # ================= AUDITORÍA =================
    print("  Auditoría (5126)")
    ev.caso("AUD-01", am, "Bitácora con filtros", "Quién cambió qué, cuándo y desde dónde.", "GET", "auditoria?modulo=pedidos&por_pagina=3", token=t_aud,
            verificar=lambda r: r.json["paginacion"]["total"] > 0,
            explicacion="La bitácora es de solo escritura (RN31); los valores de contraseñas nunca aparecen.")
    ev.caso("AUD-02", am, "Accesos al sistema", "Inicios, fallos, bloqueos y accesos denegados del periodo.", "GET", "auditoria/accesos", token=t_aud,
            verificar=lambda r: r.json["totales"]["login_exitoso"] > 0)
    pid = uno("SELECT pedido_id FROM historial_estatus GROUP BY pedido_id ORDER BY count(*) DESC, pedido_id LIMIT 1")["pedido_id"]
    ev.caso("AUD-03", am, "Línea de tiempo de un pedido", "Une bitácora, cambios de estado, inventario y archivos del pedido.", "GET",
            f"auditoria/trazabilidad/pedido/{pid}", token=t_aud, verificar=lambda r: any(e["origen"] == "estados" for e in r.json["eventos"]),
            evidencia=lambda r: [pg("SELECT estado_anterior, estado_nuevo, fecha FROM historial_estatus WHERE pedido_id = %s ORDER BY fecha", (pid,))])
    eid = uno("SELECT id FROM entrega ORDER BY id LIMIT 1")["id"]
    ev.caso("AUD-04", am, "Línea de tiempo de una entrega", "Bitácora y archivos de la entrega.", "GET", f"auditoria/trazabilidad/entrega/{eid}", token=t_aud,
            verificar=lambda r: r.json["objeto"]["tipo"] == "entrega")
    m = uno("SELECT microhub_id, producto_id FROM movimiento_inventario ORDER BY id LIMIT 1")
    ev.caso("AUD-05", am, "Movimientos de un producto en un microhub", "Trazabilidad del inventario.", "GET",
            f"auditoria/trazabilidad/inventario?microhub_id={m['microhub_id']}&producto_id={m['producto_id']}", token=t_aud,
            verificar=lambda r: r.json["total"] >= 1)
    ev.caso("AUD-06", am, "La bitácora está restringida", "El planeador no tiene auditoria.ver; el intento queda registrado.", "GET", "auditoria", token=t_plan,
            esperado=403, evidencia=lambda r: [pg("SELECT fecha, accion, detalle, exitoso FROM auditoria WHERE accion = 'acceso_denegado' ORDER BY id DESC LIMIT 1")])

    # ================= REPORTES =================
    print("  Reportes (5123)")
    periodo = f"desde={(dt.date.today() - dt.timedelta(days=90)).isoformat()}"
    ev.caso("REP-01", rp, "Catálogo de reportes", "Cuatro familias y los filtros que admite cada uno.", "GET", "reportes", token=t_plan,
            verificar=lambda r: len(r.json["datos"]) == 8)
    ev.caso("REP-02", rp, "Indicadores del periodo", "Pedidos, venta, ticket, alertas, repartidores y microhubs no viables.", "GET", f"reportes/indicadores?{periodo}",
            token=t_plan, verificar=lambda r: r.json["indicadores"] and r.json["fuentes_no_disponibles"] == [],
            explicacion="Cada cifra la entrega el servicio dueño; si uno no responde, solo falta su indicador.")
    ev.caso("REP-03", rp, "Comparación entre microhubs", "Pedidos, venta y participación de cada microhub.", "GET", f"reportes/comparacion_microhubs?{periodo}",
            token=t_adm, verificar=lambda r: r.json["total_filas"] >= 2,
            evidencia=lambda r: [pg("SELECT m.nombre, count(*) AS pedidos, round(sum(p.subtotal), 2) AS venta FROM pedido p JOIN microhub m ON m.id = p.microhub_id "
                                    "WHERE p.estado <> 'cancelado' AND p.creado_en > now() - interval '90 days' GROUP BY m.nombre ORDER BY venta DESC")])
    ev.caso("REP-04", rp, "Reporte en XML", "El reporte financiero validado contra reportes.xsd.", "GET", "reportes/equilibrio_microhubs", token=t_adm, formato="xml",
            verificar=lambda r: "<reporte " in r.texto)
    ev.caso("REP-05", rp, "Datos para Highcharts", "Categorías y series listas para graficar.", "GET", f"reportes/pedidos_por_zona/grafica?{periodo}", token=t_adm,
            verificar=lambda r: r.json["series"] and len(r.json["series"][0]["datos"]) == len(r.json["categorias"]))
    ev.caso("REP-06", rp, "Exportar a CSV", "Descarga con SHA-256 y registro en la bitácora de exportaciones.", "GET",
            f"reportes/pedidos_por_zona/exportar?formato=csv&{periodo}", token=t_adm, verificar=lambda r: "Zona" in r.texto,
            explicacion="Excel (xlsx) y PDF usan la misma ruta con formato=xlsx|pdf. El archivo se genera al momento; no se guarda.",
            evidencia=lambda r: [pg("SELECT reporte, formato, filas, bytes, left(sha256, 16) AS sha256, creado_por FROM reporte_exportacion ORDER BY id DESC LIMIT 1")])
    ev.caso("REP-07", rp, "Bitácora de exportaciones", "Quién exportó qué, con qué filtros.", "GET", "reportes/exportaciones?por_pagina=3", token=t_aud,
            verificar=lambda r: r.json["paginacion"]["total"] >= 1)
    ev.caso("REP-08", rp, "Filtro que el reporte no admite", "Se rechaza en lugar de ignorarse.", "GET", "reportes/carga_repartidores?zona_id=1", token=t_adm,
            esperado=400, verificar=lambda r: r.json["error"]["codigo"] == "FILTRO_INVALIDO")
    ev.caso("REP-09", rp, "El cliente no ve reportes", "Sin reportes.ver.", "GET", "reportes", token=t_cli, esperado=403)

    # ================= SINCRONIZACIÓN =================
    print("  Sincronización (5125)")
    entrega = preparar("repartidor1@codex.mx", 1)[0]["entrega_id"]
    doc = silencioso("documentos", "POST", "documentos", {
        "nombre": f"evidencia-sync-{entrega}.jpg", "tipo_mime": "image/jpeg", "contenido_base64": base64.b64encode(JPEG).decode(),
        "referencia": {"tipo": "entrega", "id": str(entrega)}}, token=t_rep).json["id"]
    disp = f"android-evidencia-{uuid.uuid4().hex[:6]}"
    cierre = {"entrega_id": entrega, "resultado": "fallida", "monto_cobrado": 0, "cambio_entregado": 0, "incidencia": "Cliente ausente",
              "ubicacion": {"latitud": 25.7491, "longitud": -100.3611}, "evidencia_ids": [doc], "capturado_en": hace(3)}
    lote = {"lote_uuid": str(uuid.uuid4()), "dispositivo": disp, "cliente": "android", "operaciones": [
        {"operacion_uuid": str(uuid.uuid4()), "tipo": "entrega_resultado", "creada_en": hace(3), "datos": cierre},
        {"operacion_uuid": str(uuid.uuid4()), "tipo": "ubicaciones", "creada_en": hace(12),
         "datos": {"entrega_id": entrega, "puntos": [{"latitud": 25.7488, "longitud": -100.3608, "capturado_en": hace(12)}]}}]}
    r = ev.caso("SYN-01", sy, "Enviar lo hecho sin conexión", "La app manda el cierre y el recorrido; se aplican en el orden en que ocurrieron.", "POST",
                "sincronizacion/lotes", cuerpo=lote, token=t_rep, esperado=201, verificar=lambda r: r.json["aplicadas"] == 2,
                explicacion="Cada operación llama al servicio dueño con el JWT del repartidor.",
                evidencia=lambda r: [pg("SELECT e.id, e.resultado, e.id_cliente_local, p.estado FROM entrega e JOIN pedido p ON p.id = e.pedido_id WHERE e.id = %s", (entrega,)),
                                     pg("SELECT operacion_uuid, tipo, estado, intentos FROM sync_operacion WHERE dispositivo = %s ORDER BY creada_en", (disp,))])
    ev.caso("SYN-02", sy, "Reenviar el mismo lote", "Idempotencia: nada se repite.", "POST", "sincronizacion/lotes", cuerpo=lote, token=t_rep,
            verificar=lambda r: r.json["duplicadas"] == 2)
    otro = {"lote_uuid": str(uuid.uuid4()), "dispositivo": disp, "cliente": "android",
            "operaciones": [{"operacion_uuid": str(uuid.uuid4()), "tipo": "entrega_resultado", "creada_en": hace(1), "datos": cierre}]}
    ev.caso("SYN-03", sy, "Conflicto: la entrega ya estaba cerrada", "Gana el servidor y queda para revisión.", "POST", "sincronizacion/lotes", cuerpo=otro,
            token=t_rep, verificar=lambda r: r.json["conflictos"] == 1)
    ev.caso("SYN-04", sy, "Conflictos por revisar", "Los ve quien tiene sincronizacion.ver.", "GET", "sincronizacion/conflictos?por_pagina=3", token=t_aud,
            verificar=lambda r: r.json["paginacion"]["total"] >= 1)
    ev.caso("SYN-05", sy, "Mis lotes", "El repartidor ve solo los suyos.", "GET", "sincronizacion/lotes?por_pagina=3", token=t_rep,
            verificar=lambda r: all(x["usuario"]["id"] == 7 for x in r.json["datos"]))
    if r is not None and r.status == 201:
        lid = r.json["id"]
        ev.caso("SYN-06", sy, "Un lote con sus operaciones", "Cada operación con su resultado.", "GET", f"sincronizacion/lotes/{lid}", token=t_rep,
                verificar=lambda x: len(x.json["operaciones"]) == 2)
    ev.caso("SYN-07", sy, "Pendientes por reintentar", "Lo que no se pudo aplicar porque un servicio no respondió.", "GET", "sincronizacion/pendientes", token=t_rep,
            verificar=lambda x: "datos" in x.json)
    ev.caso("SYN-08", sy, "Estado del dispositivo", "Última sincronización y pendientes.", "GET", f"sincronizacion/estado?dispositivo={disp}", token=t_rep,
            verificar=lambda x: x.json["conflictos"] == 1 and x.json["pendientes"] == 0)
    ev.caso("SYN-09", sy, "Límites de la sincronización", "Tamaño de lote, antigüedad y reloj.", "GET", "sincronizacion/supuestos", token=t_rep,
            verificar=lambda x: any(s["clave"] == "sync_lote_max" for s in x.json["datos"]))
    ev.caso("SYN-10", sy, "El cliente no sincroniza", "Sin sincronizacion.usar.", "POST", "sincronizacion/lotes", cuerpo=lote, token=t_cli, esperado=403)
    ev.caso("SYN-11", sy, "Lote mal formado", "operaciones debe ser una lista.", "POST", "sincronizacion/lotes",
            cuerpo={**lote, "operaciones": "x"}, token=t_rep, esperado=422, verificar=lambda x: x.json["error"]["codigo"] == "VALIDACION")
    # el XML del contrato: las consultas responden en XML
    ev.caso("SYN-12", sy, "Estado en XML", "Validado contra sincronizacion.xsd.", "GET", f"sincronizacion/estado?dispositivo={disp}", token=t_rep, formato="xml",
            verificar=lambda x: "<sync_estado" in x.texto)
