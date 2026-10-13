"""
Servicio de documentos · puerto 5107 · contrato v1

  POST /api/v1/documentos                  subir evidencia o archivo en Base64 (solo JSON)
  GET  /api/v1/documentos                  documentos visibles (referencia_tipo, referencia_id)
  GET  /api/v1/documentos/resumen          agregación ($group) por tipo de referencia
  GET  /api/v1/documentos/{id}             metadatos
  GET  /api/v1/documentos/{id}/contenido   metadatos + contenido en Base64
  DELETE /api/v1/documentos/{id}           eliminar (autor o administrador; no la evidencia de una entrega cerrada)

Almacén: MongoDB, colección `documentos` (id = ObjectId de 24 caracteres).
Se valida tipo MIME contra la firma real del archivo, tamaño máximo de
5 MB y que la referencia pertenezca a quien sube (un repartidor solo
adjunta evidencia a sus entregas). Se guarda el SHA-256 del contenido.
"""
import base64
import binascii
import hashlib

from bson import Binary, ObjectId
from flask import g, request

from comun import config
from comun.base import (crear_app, documentar, filtro_opcion, leer_cuerpo, leer_paginacion, lista, paginacion,
                        requiere, responder, tiene)
from comun.base_errores import ErrorApi, invalido, no_encontrado, prohibido
from comun.datos import ahora, consultar, mongo
from comun.formatos import fecha
from comun.validar import Campo, validar

app = crear_app("documentos", "Microhubs · Documentos", "Evidencias y archivos en MongoDB.", 5107,
                dependencias=("redis", "mongo", "postgres"))
P = config.PREFIJO
FIRMAS = {"image/jpeg": b"\xff\xd8\xff", "image/png": b"\x89PNG\r\n\x1a\n", "application/pdf": b"%PDF-"}
REFERENCIAS = ["entrega", "pedido", "usuario", "candidato"]
VEN_TODO = ("administrador", "auditor")


def coleccion():
    db = mongo()
    if db is None:
        raise ErrorApi(503, "SERVICIO_NO_DISPONIBLE", "El almacén de documentos (MongoDB) no está disponible.")
    return db.documentos


def metadatos(d):
    return {"id": str(d["_id"]), "nombre": d["nombre"], "tipo_mime": d["tipo_mime"], "tamano_bytes": int(d["tamano_bytes"]),
            "sha256": d["sha256"], "referencia": {"tipo": d["referencia"]["tipo"], "id": d["referencia"]["id"]},
            "subido_por": int(d["subido_por"]), "creado_en": fecha(d["creado_en"])}


def _filtro_visible():
    return {} if g.usuario["rol"] in VEN_TODO else {"subido_por": g.usuario["id"]}


def _uno(did):
    if not ObjectId.is_valid(did) or len(did) != 24:
        raise no_encontrado()
    d = coleccion().find_one({"_id": ObjectId(did), **_filtro_visible()})
    if not d:
        raise no_encontrado()
    return d


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
                                Campo("contenido_base64", min_len=4), Campo("referencia", "obj")])
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
    doc = {"nombre": d["nombre"], "tipo_mime": d["tipo_mime"], "tamano_bytes": len(contenido),
           "sha256": hashlib.sha256(contenido).hexdigest(), "referencia": ref, "subido_por": int(g.usuario["id"]),
           "creado_en": ahora(), "contenido": Binary(contenido)}
    doc["_id"] = coleccion().insert_one(doc).inserted_id
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
        {"$group": {"_id": "$referencia.tipo", "cantidad": {"$sum": 1}, "tamano_bytes": {"$sum": "$tamano_bytes"}}},
        {"$sort": {"_id": 1}}]))
    por_tipo = [{"referencia_tipo": x["_id"], "cantidad": int(x["cantidad"]), "tamano_bytes": int(x["tamano_bytes"])}
                for x in grupos if x["_id"] in REFERENCIAS]
    return responder({"total": sum(x["cantidad"] for x in por_tipo),
                      "tamano_total_bytes": sum(x["tamano_bytes"] for x in por_tipo), "por_tipo": por_tipo},
                     raiz="documentos_resumen")


@app.get(f"{P}/documentos/<did>")
@requiere("archivos.ver")
def documento(did):
    return responder(metadatos(_uno(did)), raiz="documento")


@app.get(f"{P}/documentos/<did>/contenido")
@requiere("archivos.ver")
def contenido(did):
    d = _uno(did)
    return responder({**metadatos(d), "contenido_base64": base64.b64encode(bytes(d["contenido"])).decode()},
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
    coleccion().delete_one({"_id": d["_id"]})
    return responder(None, 204)


documentar(app, "POST", f"{P}/documentos", "Subir documento", permisos=["archivos.crear"], cuerpo="DocumentoNuevo.ok",
           solo_json=True, descripcion="JPEG, PNG o PDF de hasta 5 MB en Base64. Se valida la firma del archivo, "
           "se calcula su SHA-256 y se guarda en MongoDB. Un repartidor solo adjunta evidencia a sus entregas.",
           respuestas={201: ("Documento guardado", "Documento.ok")}, errores=[400, 403, 413, 422])
documentar(app, "GET", f"{P}/documentos", "Mis documentos", permisos=["archivos.ver"],
           parametros=[("pagina", "query", "integer", "Página"), ("por_pagina", "query", "integer", "1 a 100"),
                       ("referencia_tipo", "query", "string", "entrega|pedido|usuario|candidato"),
                       ("referencia_id", "query", "string", "Id del registro")],
           descripcion="Cada persona ve lo que subió; administrador y auditor ven todo.",
           respuestas={200: ("Página de documentos", "DocumentoLista.ok")}, errores=[400, 403])
documentar(app, "GET", f"{P}/documentos/resumen", "Resumen por tipo (agregación MongoDB)",
           permisos=["reportes.ver", "bitacora.ver"], respuestas={200: ("Totales por tipo", "DocumentosResumen.ok")},
           errores=[403])
documentar(app, "GET", f"{P}/documentos/{{id}}", "Metadatos de un documento", permisos=["archivos.ver"],
           parametros=[("id", "path", "string", "ObjectId de 24 caracteres")],
           respuestas={200: ("Documento", "Documento.ok")}, errores=[403, 404])
documentar(app, "GET", f"{P}/documentos/{{id}}/contenido", "Contenido de un documento", permisos=["archivos.ver"],
           parametros=[("id", "path", "string", "ObjectId")],
           respuestas={200: ("Documento con Base64", "DocumentoContenido.ok")}, errores=[403, 404])
documentar(app, "DELETE", f"{P}/documentos/{{id}}", "Eliminar documento", permisos=["archivos.crear"],
           parametros=[("id", "path", "string", "ObjectId")],
           descripcion="Solo quien lo subió o el administrador. La evidencia de una entrega cerrada no se borra (409).",
           respuestas={204: ("Eliminado, sin cuerpo", None)}, errores=[403, 404, 409])
