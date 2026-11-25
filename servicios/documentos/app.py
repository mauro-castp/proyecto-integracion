"""
Servicio de documentos · puerto 5107 · contrato v1

  POST /api/v1/documentos                  subir evidencia o archivo en Base64 (solo JSON)
  GET  /api/v1/documentos                  documentos visibles (referencia_tipo, referencia_id)
  GET  /api/v1/documentos/resumen          agregación ($group) por tipo de referencia
  GET  /api/v1/documentos/{id}             metadatos
  GET  /api/v1/documentos/{id}/enlace      URL FIRMADA y con caducidad para descargar el archivo (recomendado)
  GET  /api/v1/documentos/{id}/contenido   metadatos + contenido en Base64 (clientes sin descarga directa)
  DELETE /api/v1/documentos/{id}           eliminar (autor o administrador; no la evidencia de una entrega cerrada)

El archivo NO vive en la base de datos. Se guarda en el almacén de objetos (Google Cloud Storage en la nube, carpeta local
en desarrollo: ver comun/almacen.py) y MongoDB conserva solo sus datos: id (ObjectId de 24 caracteres), ruta del objeto,
tipo, tamaño, propietario (subido_por), fecha, SHA-256, privacidad, estado y metadatos.

Se valida el tipo MIME contra la firma real del archivo, el tamaño máximo (5 MB) y que la referencia pertenezca a quien
sube (un repartidor solo adjunta evidencia a sus entregas).

Privacidad:  privado (por omisión) = solo quien lo subió, administrador y auditor;  interno = cualquier persona con archivos.ver.
Estado:      activo | eliminado (el borrado quita el objeto del almacén y deja el registro para la auditoría).
Si el archivo se sube pero MongoDB falla, el objeto se borra: no quedan archivos huérfanos ni registros sin archivo.
"""
import base64
import binascii
import hashlib
import hmac as _hmac
import datetime as dt

from bson import ObjectId
from flask import Response, g, request

from comun import almacen, config
from comun.base import (crear_app, documentar, filtro_opcion, leer_cuerpo, leer_paginacion, lista, paginacion,
                        requiere, responder, tiene)
from comun.base_errores import ErrorApi, invalido, no_encontrado, prohibido
from comun.datos import ahora, auditar, consultar, mongo
from comun.formatos import fecha
from comun.validar import Campo, validar

app = crear_app("documentos", "Microhubs · Documentos", "Evidencias y archivos en un almacén de objetos (Google Cloud Storage).",
                5107, dependencias=("redis", "mongo", "postgres", "bucket"))
P = config.PREFIJO
FIRMAS = {"image/jpeg": b"\xff\xd8\xff", "image/png": b"\x89PNG\r\n\x1a\n", "application/pdf": b"%PDF-"}
REFERENCIAS = ["entrega", "pedido", "usuario", "candidato"]
PRIVACIDADES = ["privado", "interno"]
ORIGENES = ["api", "web", "movil", "escritorio"]
VEN_TODO = ("administrador", "auditor")


def coleccion():
    db = mongo()
    if db is None:
        raise ErrorApi(503, "SERVICIO_NO_DISPONIBLE", "El almacén de documentos (MongoDB) no está disponible.")
    return db.documentos


def metadatos(d):
    """Datos del archivo. Los documentos anteriores a la nube (con el contenido dentro de MongoDB) se muestran igual."""
    return {"id": str(d["_id"]), "nombre": d["nombre"], "tipo_mime": d["tipo_mime"], "tamano_bytes": int(d["tamano_bytes"]),
            "sha256": d["sha256"], "referencia": {"tipo": d["referencia"]["tipo"], "id": d["referencia"]["id"]},
            "subido_por": int(d["subido_por"]), "creado_en": fecha(d["creado_en"]),
            "ruta": d.get("ruta") or "", "privacidad": d.get("privacidad", "privado"), "estado": d.get("estado", "activo"),
            "metadatos": {"almacen": (d.get("metadatos") or {}).get("almacen", "mongodb"),
                          "origen": (d.get("metadatos") or {}).get("origen", "api")}}


def _filtro_visible():
    f = {"estado": {"$ne": "eliminado"}}
    if g.usuario["rol"] not in VEN_TODO:
        f["$or"] = [{"subido_por": g.usuario["id"]}, {"privacidad": "interno"}]
    return f


def _uno(did):
    if not ObjectId.is_valid(did) or len(did) != 24:
        raise no_encontrado()
    d = coleccion().find_one({"_id": ObjectId(did), **_filtro_visible()})
    if not d:
        raise no_encontrado()
    return d


def _bytes_de(d):
    """Contenido del archivo: del almacén de objetos o, en documentos antiguos, del propio registro."""
    if d.get("contenido") is not None:
        return bytes(d["contenido"])
    if not d.get("ruta"):
        raise ErrorApi(404, "NO_ENCONTRADO", "El documento no tiene archivo asociado.")
    return almacen.obtener().leer(d["ruta"])


def _verificar_referencia(tipo, rid):
    """La evidencia solo se adjunta a algo que la persona puede tocar."""
    u = g.usuario
    if not rid.isdigit():
        raise invalido("referencia.id", "Debe ser el id numérico del registro.")
    if tipo == "entrega":
        f = consultar("SELECT e.repartidor_id, p.microhub_id FROM entrega e JOIN pedido p ON p.id = e.pedido_id "
                      "WHERE e.id = %s", (int(rid),), una=True)
        if not f:
            raise invalido("referencia.id", "No existe esa entrega.")
        if u["rol"] == "repartidor" and f["repartidor_id"] != u["id"]:
            raise prohibido("Solo puedes adjuntar evidencia a tus entregas.")
        if u["rol"] == "operador" and f["microhub_id"] != u.get("microhub_id"):
            raise prohibido("La entrega no pertenece a tu microhub.")
    elif tipo == "pedido":
        if not consultar("SELECT 1 FROM fn_pedidos_visibles(%s) WHERE id = %s", (u["id"], int(rid)), una=True) \
                and u["rol"] not in ("administrador",):
            raise prohibido("El pedido no está en tu ámbito.")
    elif tipo == "usuario" and int(rid) != u["id"] and u["rol"] != "administrador":
        raise prohibido("Solo puedes adjuntar documentos a tu propio usuario.")
    elif tipo == "candidato" and not tiene("planeacion.editar"):
        raise prohibido("Adjuntar a un candidato requiere planeacion.editar.")


@app.post(f"{P}/documentos")
@requiere("archivos.crear")
def subir():
    d = validar(leer_cuerpo(), [Campo("nombre", min_len=1, max_len=160), Campo("tipo_mime", opciones=list(FIRMAS)),
                                Campo("contenido_base64", min_len=4), Campo("referencia", "obj"),
                                Campo("privacidad", req=False, opciones=PRIVACIDADES)])
    ref = validar(d["referencia"], [Campo("tipo", opciones=REFERENCIAS), Campo("id", min_len=1, max_len=40)],
                  prefijo="referencia.")
    try:
        contenido = base64.b64decode(d["contenido_base64"], validate=True)
    except (binascii.Error, ValueError):
        raise invalido("contenido_base64", "No es Base64 válido (sin saltos de línea).")
    if not contenido or len(contenido) > config.MAX_ARCHIVO_BYTES:
        raise invalido("contenido_base64", "El archivo debe pesar entre 1 byte y 5 MB.")
    if not contenido.startswith(FIRMAS[d["tipo_mime"]]):
        raise invalido("tipo_mime", "El contenido no corresponde al tipo declarado.")
    _verificar_referencia(ref["tipo"], ref["id"])

    sha = hashlib.sha256(contenido).hexdigest()
    oid = ObjectId()
    ruta = almacen.clave_objeto(str(oid), d["tipo_mime"])
    alm = almacen.obtener()
    origen = (request.headers.get("X-Cliente") or "api").strip().lower()
    doc = {"_id": oid, "nombre": d["nombre"], "tipo_mime": d["tipo_mime"], "tamano_bytes": len(contenido), "sha256": sha,
           "referencia": ref, "subido_por": int(g.usuario["id"]), "creado_en": ahora(), "ruta": ruta,
           "privacidad": d.get("privacidad") or "privado", "estado": "activo",
           "metadatos": {"almacen": alm.nombre, "origen": origen if origen in ORIGENES else "api"}}
    alm.guardar(ruta, contenido, d["tipo_mime"], sha)                       # 1) el archivo al almacén
    try:
        coleccion().insert_one(doc)                                          # 2) sus datos a MongoDB
    except Exception:
        try:
            alm.borrar(ruta)                                                 # sin registro no debe quedar el archivo
        except almacen.ErrorAlmacen:
            pass
        raise
    auditar("documentos", "subir", f"{d['nombre']} ({len(contenido)} bytes) a {ref['tipo']} {ref['id']}.",
            entidad="documento", entidad_id=None)
    return responder(metadatos(doc), 201, raiz="documento")


@app.get(f"{P}/documentos")
@requiere("archivos.ver")
def documentos():
    pagina, por, desde = leer_paginacion()
    filtro = _filtro_visible()
    tipo = filtro_opcion("referencia_tipo", REFERENCIAS)
    if tipo:
        filtro["referencia.tipo"] = tipo
    rid = (request.args.get("referencia_id") or "").strip()
    if rid:
        filtro["referencia.id"] = rid[:40]
    col = coleccion()
    total = col.count_documents(filtro)
    docs = col.find(filtro, {"contenido": 0}).sort("creado_en", -1).skip(desde).limit(por)
    return lista(list(docs), paginacion(pagina, por, total), "documento", "documentos", metadatos)


@app.get(f"{P}/documentos/resumen")
@requiere("reportes.ver", "bitacora.ver")
def resumen():
    grupos = list(coleccion().aggregate([
        {"$match": {"estado": {"$ne": "eliminado"}}},
        {"$group": {"_id": "$referencia.tipo", "cantidad": {"$sum": 1}, "tamano_bytes": {"$sum": "$tamano_bytes"}}},
        {"$sort": {"_id": 1}}]))
    por_tipo = [{"referencia_tipo": x["_id"], "cantidad": int(x["cantidad"]), "tamano_bytes": int(x["tamano_bytes"])}
                for x in grupos if x["_id"] in REFERENCIAS]
    return responder({"total": sum(x["cantidad"] for x in por_tipo),
                      "tamano_total_bytes": sum(x["tamano_bytes"] for x in por_tipo), "por_tipo": por_tipo},
                     raiz="documentos_resumen")


@app.get(f"{P}/documentos/descarga")
def descarga():
    """Solo con ALMACEN=local: la 'URL firmada' que emite este mismo servicio (HMAC + caducidad). Con GCS no se usa:
    la descarga la sirve Google Cloud Storage directamente."""
    alm = almacen.obtener()
    if alm.nombre != "local":
        raise no_encontrado()
    k, e, n, t, s = (request.args.get(x, "") for x in ("k", "e", "n", "t", "s"))
    if not alm.firma_valida(k, e, n, t, s):
        raise ErrorApi(403, "PROHIBIDO", "El enlace de descarga no es válido o ya caducó.")
    resp = Response(alm.leer(k), content_type=t or "application/octet-stream")
    resp.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{n}"
    return resp


@app.get(f"{P}/documentos/<did>")
@requiere("archivos.ver")
def documento(did):
    return responder(metadatos(_uno(did)), raiz="documento")


@app.get(f"{P}/documentos/<did>/enlace")
@requiere("archivos.ver")
def enlace(did):
    """URL firmada y con caducidad: el cliente descarga directo del bucket, sin pasar por el servicio ni por la base."""
    d = _uno(did)
    if not d.get("ruta"):
        raise ErrorApi(409, "CONFLICTO", "El documento aún está en la base de datos; ejecuta documentos/migrar_a_almacen.py.")
    segundos = config.URL_FIRMADA_SEGUNDOS
    url, expira = almacen.obtener().url_firmada(d["ruta"], segundos, d["nombre"], d["tipo_mime"])
    if url.startswith("/"):                                                  # almacén local: la URL es de este servicio
        url = request.host_url.rstrip("/") + url
    auditar("documentos", "enlace", f"Enlace de descarga de {d['nombre']} (caduca en {segundos} s).",
            entidad="documento", entidad_id=None)
    return responder({"id": str(d["_id"]), "nombre": d["nombre"], "url_firmada": url, "metodo": "GET",
                      "segundos": segundos, "expira_en": fecha(dt.datetime.fromtimestamp(expira, tz=dt.timezone.utc))},
                     raiz="documento_enlace")


@app.get(f"{P}/documentos/<did>/contenido")
@requiere("archivos.ver")
def contenido(did):
    d = _uno(did)
    contenido_bytes = _bytes_de(d)
    if not _hmac.compare_digest(hashlib.sha256(contenido_bytes).hexdigest(), d["sha256"]):
        raise ErrorApi(409, "CONFLICTO", "El archivo guardado no coincide con su SHA-256: puede estar dañado.")
    return responder({**metadatos(d), "contenido_base64": base64.b64encode(contenido_bytes).decode()},
                     raiz="documento_contenido")


@app.delete(f"{P}/documentos/<did>")
@requiere("archivos.crear")
def borrar(did):
    """Solo quien lo subió (o el administrador) y solo si no es evidencia de una entrega ya cerrada."""
    d = _uno(did)
    if d["subido_por"] != g.usuario["id"] and g.usuario["rol"] != "administrador":
        raise prohibido("Solo quien subió el documento puede eliminarlo.")
    if consultar("SELECT 1 FROM entrega WHERE %s = ANY(evidencia_ids)", (did,), una=True):
        raise ErrorApi(409, "CONFLICTO", "El documento es evidencia de una entrega cerrada y no se puede eliminar.")
    if d.get("ruta"):
        almacen.obtener().borrar(d["ruta"])                                  # primero el objeto; si falla, el registro queda activo
    coleccion().update_one({"_id": d["_id"]}, {"$set": {"estado": "eliminado", "eliminado_en": ahora()},
                                               "$unset": {"contenido": ""}})
    auditar("documentos", "eliminar", f"{d['nombre']} eliminado.", entidad="documento", entidad_id=None)
    return responder(None, 204)


documentar(app, "POST", f"{P}/documentos", "Subir documento", permisos=["archivos.crear"], cuerpo="DocumentoNuevo.ok",
           solo_json=True, descripcion="JPEG, PNG o PDF de hasta 5 MB en Base64. Se valida la firma del archivo, "
           "se calcula su SHA-256 y el archivo se guarda en el bucket (Google Cloud Storage); MongoDB conserva solo sus "
           "datos. Un repartidor solo adjunta evidencia a sus entregas. `privacidad` opcional: privado (por omisión) o interno.",
           respuestas={201: ("Documento guardado", "Documento.ok")}, errores=[400, 403, 413, 422, 503])
documentar(app, "GET", f"{P}/documentos", "Mis documentos", permisos=["archivos.ver"],
           parametros=[("pagina", "query", "integer", "Página"), ("por_pagina", "query", "integer", "1 a 100"),
                       ("referencia_tipo", "query", "string", "entrega|pedido|usuario|candidato"),
                       ("referencia_id", "query", "string", "Id del registro")],
           descripcion="Cada persona ve lo que subió y lo marcado como interno; administrador y auditor ven todo. "
           "No se listan los documentos eliminados.",
           respuestas={200: ("Página de documentos", "DocumentoLista.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/documentos/resumen", "Resumen por tipo (agregación MongoDB)",
           permisos=["reportes.ver", "bitacora.ver"], respuestas={200: ("Totales por tipo", "DocumentosResumen.ok")},
           errores=[403])
documentar(app, "GET", f"{P}/documentos/{{id}}", "Metadatos de un documento", permisos=["archivos.ver"],
           parametros=[("id", "path", "string", "ObjectId de 24 caracteres")],
           respuestas={200: ("Documento", "Documento.ok")}, errores=[403, 404])
documentar(app, "GET", f"{P}/documentos/{{id}}/enlace", "URL firmada para descargar el archivo",
           permisos=["archivos.ver"], parametros=[("id", "path", "string", "ObjectId")],
           descripcion="Devuelve una URL firmada (V4) que caduca en `segundos`; el cliente descarga directo del bucket. "
           "Quedan registradas en la auditoría.",
           respuestas={200: ("Enlace de descarga", "DocumentoEnlace.ok")}, errores=[403, 404, 503])
documentar(app, "GET", f"{P}/documentos/{{id}}/contenido", "Contenido de un documento (Base64)", permisos=["archivos.ver"],
           parametros=[("id", "path", "string", "ObjectId")],
           descripcion="Para clientes que no pueden usar la URL firmada. Se verifica el SHA-256 antes de entregarlo.",
           respuestas={200: ("Documento con Base64", "DocumentoContenido.ok")}, errores=[403, 404, 409, 503])
documentar(app, "DELETE", f"{P}/documentos/{{id}}", "Eliminar documento", permisos=["archivos.crear"],
           parametros=[("id", "path", "string", "ObjectId")],
           descripcion="Solo quien lo subió o el administrador. Borra el objeto del bucket y marca el registro como "
           "eliminado. La evidencia de una entrega cerrada no se borra (409).",
           respuestas={204: ("Eliminado, sin cuerpo", None)}, errores=[403, 404, 409, 503])
