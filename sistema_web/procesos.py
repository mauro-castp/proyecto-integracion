"""
procesos.py — Procesos integrales de punta a punta desde el portal web, a través de los microservicios (entrega final).

Cada pantalla es una aplicación cliente de los servicios: llama por HTTP con el JWT de la sesión (Redis valida la sesión en cada
servicio), los servicios aplican sus permisos y reglas, escriben en PostgreSQL o MongoDB, los triggers dejan la auditoría y los
avisos, y los archivos van al almacén de objetos (bucket). La página muestra cada llamada con su código, tiempo y traza.

  /web/servicios/abastecimiento   P2 · Reabastecimiento: alerta de inventario → necesidad con la mejor oferta → solicitud → aprobación
                                  → orden de compra al proveedor → recepción (entrada a inventario) + comprobante al bucket → avisos
  /web/servicios/rutas            P3 · Despacho: pedidos listos → plan de rutas (TSP exacto o vecino + 2-opt) → confirmar → la entrega
                                  le llega al repartidor en la app Android (aviso por trigger)
  /web/servicios/reportes         P3 · Reportes: el reporte armado por el servicio de reportes (con datos de los servicios dueños),
                                  exportado a CSV/Excel/PDF, archivado en el bucket y descargable con una URL firmada

El P1 (cierre de entrega) lo hace la app Android y se ve en /web/servicios/pedido/<id>.
"""
import base64
import uuid

from flask import abort, flash, g, redirect, render_template, request, Response, url_for

from integracion import _csrf_valido, _requiere_sesion, llamar, servicios_bp


def _permisos():
    from web_ampliado import permisos_usuario
    return permisos_usuario()


def _microhub():
    mh = request.values.get("microhub_id", "")
    if mh.isdigit():
        return int(mh)
    return (g.usuario or {}).get("microhub_id") or 1


def _datos(ll, defecto=None):
    if ll.ok and isinstance(ll.datos, dict):
        return ll.datos.get("datos", ll.datos)
    return defecto if defecto is not None else []


def _ir_a(url_firmada):
    """En la nube la URL firmada es de Cloud Storage: el navegador baja el archivo directo del bucket. Con el almacén local
    (desarrollo) la URL apunta al servicio dentro de la red de Docker, que el navegador no alcanza: el web la sigue por él."""
    if url_firmada.startswith("https://storage.googleapis.com/"):
        return redirect(url_firmada)
    import urllib.request
    with urllib.request.urlopen(url_firmada, timeout=10) as r:
        resp = Response(r.read(), content_type=r.headers.get("Content-Type", "application/octet-stream"))
        resp.headers["Content-Disposition"] = r.headers.get("Content-Disposition", "attachment")
    resp.headers["Cache-Control"] = "private, no-store"
    return resp


def _avisar(ll, ok, mal="No se pudo"):
    if ll.ok:
        flash(f"{ok} (HTTP {ll.status}, {ll.servicio}, traza {ll.traza[:8]}).", "ok")
    else:
        detalle = ""
        if isinstance(ll.datos, dict) and (ll.datos.get("error") or {}).get("detalles"):
            detalle = " · " + "; ".join(f"{d.get('campo')}: {d.get('mensaje')}" for d in ll.datos["error"]["detalles"])
        flash(f"{mal}: {ll.status or 'sin conexión'} {ll.mensaje}{detalle} (traza {ll.traza[:8]}).", "alto")


# ------------------------------------------------------------------------------------------------------------------------------
# P2 · Reabastecimiento
# ------------------------------------------------------------------------------------------------------------------------------
@servicios_bp.route("/abastecimiento", methods=["GET", "POST"])
def abastecimiento():
    if (r := _requiere_sesion()):
        return r
    permisos = _permisos()
    if "abastecimiento.ver" not in permisos:
        abort(403)
    mh = _microhub()
    if request.method == "POST":
        if not _csrf_valido():
            abort(400, "Formulario vencido; recarga la página.")
        accion = request.form.get("accion")
        if accion == "solicitar":
            lineas = []
            for pid in request.form.getlist("producto"):
                cant = request.form.get(f"cantidad_{pid}", "")
                if pid.isdigit() and cant.isdigit() and int(cant) > 0:
                    lineas.append({"producto_id": int(pid), "cantidad": int(cant)})
            if not lineas:
                flash("Marca al menos un producto con su cantidad.", "alto")
            else:
                ll = llamar("abastecimiento", "POST", "abastecimiento/solicitudes",
                            {"microhub_id": mh, "motivo": request.form.get("motivo") or "Reposición desde el portal", "lineas": lineas})
                _avisar(ll, f"Solicitud {(ll.datos or {}).get('folio', '')} creada; el planeador recibe el aviso")
        elif accion == "decidir" and (request.form.get("solicitud") or "").isdigit():
            ll = llamar("abastecimiento", "POST", f"abastecimiento/solicitudes/{int(request.form['solicitud'])}/decision",
                        {"decision": request.form.get("decision"), "motivo": request.form.get("motivo") or ""})
            _avisar(ll, f"Solicitud {request.form.get('decision')}")
        elif accion == "ordenar" and (request.form.get("solicitud") or "").isdigit():
            prov = request.form.get("proveedor_id", "")
            ll = llamar("abastecimiento", "POST", f"abastecimiento/solicitudes/{int(request.form['solicitud'])}/ordenar",
                        {"proveedor_id": int(prov)} if prov.isdigit() else {})
            _avisar(ll, "Orden de compra emitida al proveedor")
        elif accion == "recibir" and (request.form.get("orden") or "").isdigit():
            _recibir(int(request.form["orden"]))
        return redirect(url_for("servicios.abastecimiento", microhub_id=mh))

    llamadas = [
        llamar("inventario", "GET", f"inventario/alertas?microhub_id={mh}&por_pagina=50"),
        llamar("abastecimiento", "GET", f"abastecimiento/necesidades?microhub_id={mh}&por_pagina=50"),
        llamar("abastecimiento", "GET", f"abastecimiento/solicitudes?microhub_id={mh}&por_pagina=15"),
        llamar("abastecimiento", "GET", f"abastecimiento/ordenes?microhub_id={mh}&por_pagina=15"),
        llamar("abastecimiento", "GET", f"abastecimiento/seguimiento?microhub_id={mh}"),
        llamar("documentos", "GET", "documentos?referencia_tipo=orden_compra&por_pagina=50"),
        llamar("notificaciones", "GET", "notificaciones?por_pagina=5"),
    ]
    alertas, necesidades, solicitudes, ordenes, seguimiento, comprobantes, avisos = llamadas
    por_orden = {}
    for d in _datos(comprobantes):
        por_orden.setdefault(d["referencia"]["id"], []).append(d)
    return render_template("web_abastecimiento.html", mh=mh, alertas=alertas, necesidades=necesidades, solicitudes=solicitudes,
                           ordenes=ordenes, seguimiento=seguimiento, por_orden=por_orden, avisos=avisos, llamadas=llamadas,
                           datos=_datos, puede_solicitar="abastecimiento.solicitar" in permisos,
                           puede_aprobar="abastecimiento.aprobar" in permisos, puede_recibir="abastecimiento.recibir" in permisos)


def _recibir(oid):
    """Recibe lo pendiente de la orden (una operacion_uuid: repetir no duplica) y sube el comprobante al bucket."""
    orden = llamar("abastecimiento", "GET", f"abastecimiento/ordenes/{oid}")
    if not orden.ok:
        return _avisar(orden, "", "No se pudo leer la orden")
    lineas = [{"producto_id": l["producto"]["id"], "cantidad": l["cantidad"] - l["cantidad_recibida"]}
              for l in orden.datos["lineas"] if l["cantidad"] > l["cantidad_recibida"]]
    if lineas:
        ll = llamar("abastecimiento", "POST", f"abastecimiento/ordenes/{oid}/recepcion",
                    {"operacion_uuid": str(uuid.uuid4()), "nota": request.form.get("nota") or "Recibido desde el portal", "lineas": lineas})
        _avisar(ll, f"Mercancía de {orden.datos['folio']} recibida: entra a inventario"
                    + (" (inventario no respondió: queda pendiente y se reintenta)" if ll.status == 202 else ""))
        if not ll.ok:
            return None
    archivo = request.files.get("comprobante")
    if archivo and archivo.filename:
        contenido = archivo.read(5 * 1024 * 1024 + 1)
        from web_ampliado import validar_archivo
        nombre, tipo = validar_archivo(archivo.filename, contenido)
        doc = llamar("documentos", "POST", "documentos", {
            "nombre": nombre, "tipo_mime": tipo, "contenido_base64": base64.b64encode(contenido).decode(), "privacidad": "interno",
            "referencia": {"tipo": "orden_compra", "id": str(oid)}})
        _avisar(doc, f"Comprobante guardado en el almacén de objetos (id {(doc.datos or {}).get('id', '')}, ruta {(doc.datos or {}).get('ruta', '')})",
                "No se guardó el comprobante")
    return None


@servicios_bp.get("/documento/<did>/enlace")
def documento_enlace(did):
    """Pide al servicio de documentos una URL firmada y redirige a ella (el archivo baja directo del bucket)."""
    if (r := _requiere_sesion()):
        return r
    if not (len(did) == 24 and all(c in "0123456789abcdef" for c in did)):
        abort(404)
    ll = llamar("documentos", "GET", f"documentos/{did}/enlace")
    if not ll.ok:
        abort(ll.status if ll.status in (403, 404, 409) else 502)
    return _ir_a(ll.datos["url_firmada"])


# ------------------------------------------------------------------------------------------------------------------------------
# P3 · Despacho con rutas
# ------------------------------------------------------------------------------------------------------------------------------
@servicios_bp.route("/rutas", methods=["GET", "POST"])
def rutas():
    if (r := _requiere_sesion()):
        return r
    permisos = _permisos()
    if "rutas.planear" not in permisos:
        abort(403)
    mh = _microhub()
    plan = comparacion = None
    llamadas = []
    if request.method == "POST":
        if not _csrf_valido():
            abort(400, "Formulario vencido; recarga la página.")
        accion = request.form.get("accion")
        if accion == "proponer":
            ll = llamar("rutas", "POST", "rutas/planes", {"microhub_id": mh, "metodo": request.form.get("metodo") or "automatico", "guardar": True})
            _avisar(ll, "Plan propuesto y guardado")
            llamadas.append(ll)
            if ll.ok:
                return redirect(url_for("servicios.rutas", microhub_id=mh, plan=ll.datos["id"]))
        elif accion == "confirmar" and (request.form.get("plan") or "").isdigit():
            despachar = "entregas.asignar" in permisos
            ll = llamar("rutas", "POST", f"rutas/planes/{int(request.form['plan'])}/confirmar", {"despachar": despachar})
            _avisar(ll, "Plan confirmado y despachado: cada repartidor recibe el aviso y ve sus paradas en la app" if despachar
                    else "Plan confirmado; el operador del microhub lo despacha a los repartidores")
            return redirect(url_for("servicios.rutas", microhub_id=mh, plan=request.form["plan"]))
    listos = llamar("pedidos", "GET", f"pedidos/listos?microhub_id={mh}&por_pagina=100")
    planes = llamar("rutas", "GET", f"rutas/planes?microhub_id={mh}&por_pagina=10")
    llamadas += [listos, planes]
    pid = request.args.get("plan", "")
    if pid.isdigit():
        plan = llamar("rutas", "GET", f"rutas/planes/{int(pid)}")
        llamadas.append(plan)
    return render_template("web_rutas.html", mh=mh, listos=listos, planes=planes, plan=plan, llamadas=llamadas, datos=_datos,
                           puede_despachar="entregas.asignar" in permisos)


# ------------------------------------------------------------------------------------------------------------------------------
# Reportes del servicio de reportes, archivados en el bucket
# ------------------------------------------------------------------------------------------------------------------------------
@servicios_bp.route("/reportes", methods=["GET", "POST"])
def reportes():
    if (r := _requiere_sesion()):
        return r
    if "reportes.ver" not in _permisos():
        abort(403)
    if request.method == "POST":
        if not _csrf_valido():
            abort(400, "Formulario vencido; recarga la página.")
        clave = request.form.get("clave", "")
        formato = request.form.get("formato", "csv")
        if not clave.replace("_", "").isalnum() or formato not in ("csv", "xlsx", "pdf"):
            abort(400)
        q = "&".join(f"{k}={request.form[k]}" for k in ("desde", "hasta") if request.form.get(k))
        ll = llamar("reportes", "GET", f"reportes/{clave}/exportar?formato={formato}" + (f"&{q}" if q else ""))
        if not ll.ok:
            _avisar(ll, "", "No se pudo exportar")
            return redirect(url_for("servicios.reportes", clave=clave))
        resp = Response(ll.crudo, content_type={"csv": "text/csv; charset=utf-8", "pdf": "application/pdf"}.get(
            formato, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
        resp.headers["Content-Disposition"] = f'attachment; filename="{clave}.{formato}"'
        return resp
    catalogo = llamar("reportes", "GET", "reportes")
    clave = request.args.get("clave") or "pedidos_por_dia"
    q = "&".join(f"{k}={request.args[k]}" for k in ("desde", "hasta") if request.args.get(k))
    reporte = llamar("reportes", "GET", f"reportes/{clave}" + (f"?{q}" if q else ""))
    exportaciones = llamar("reportes", "GET", "reportes/exportaciones?por_pagina=10")
    llamadas = [catalogo, reporte, exportaciones]
    return render_template("web_reportes_servicio.html", catalogo=catalogo, clave=clave, reporte=reporte, exportaciones=exportaciones,
                           llamadas=llamadas, datos=_datos, desde=request.args.get("desde", ""), hasta=request.args.get("hasta", ""))


@servicios_bp.get("/reportes/exportacion/<int:eid>")
def reporte_enlace(eid):
    if (r := _requiere_sesion()):
        return r
    ll = llamar("reportes", "GET", f"reportes/exportaciones/{eid}/enlace")
    if not ll.ok:
        flash(f"No hay archivo: {ll.mensaje or ll.status}", "alto")
        return redirect(url_for("servicios.reportes"))
    return _ir_a(ll.datos["url_firmada"])
