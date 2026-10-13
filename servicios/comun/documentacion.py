"""
documentacion.py — OpenAPI 3.0 y Swagger UI de cada microservicio.

Cada ruta se describe con documentar(): descripción, método, parámetros,
encabezados, autenticación Bearer, cuerpo y respuestas. Los ejemplos JSON y
XML son los archivos OFICIALES del contrato v1 (los mismos con los que se
prueban las apps), así que la documentación no puede divergir del contrato.
"""
import json
from functools import lru_cache

from . import config
from .formatos import NS

ERRORES = {400: ("Solicitud o filtro mal formado (JSON/XML inválido, DTD rechazado, filtro desconocido).", None),
           401: ("Sin token, token vencido o revocado, o sesión inactiva en Redis.", "Error.token_invalido"),
           403: ("El perfil no tiene el permiso requerido.", None),
           404: ("El recurso no existe o está fuera del ámbito del usuario.", "Error.no_encontrado"),
           409: ("Conflicto con el estado actual (duplicado o ya cerrado).", None),
           413: ("El cuerpo excede 8 MB.", None),
           415: ("Content-Type distinto de application/json o application/xml.", None),
           422: ("Validación de datos (o del XSD) o regla de negocio rechazada por PostgreSQL.", "Error.validacion"),
           423: ("Cuenta bloqueada temporalmente por intentos fallidos.", None),
           429: ("Límite de solicitudes por minuto excedido. Encabezado Retry-After con los segundos.", None),
           503: ("PostgreSQL, Redis o MongoDB no responden.", None)}


@lru_cache(maxsize=None)
def ejemplo_json(nombre):
    ruta = config.EJEMPLOS_JSON / f"{nombre}.json"
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else None


@lru_cache(maxsize=None)
def ejemplo_xml(nombre):
    ruta = config.EJEMPLOS_XML / f"{nombre}.xml"
    return ruta.read_text(encoding="utf-8") if ruta.exists() else None


def _contenido(nombre, solo_json=False):
    c = {}
    js, xml = ejemplo_json(nombre), None if solo_json else ejemplo_xml(nombre)
    if js is not None:
        c["application/json"] = {"schema": {"type": "object"}, "example": js}
    if xml is not None:
        c["application/xml"] = {"schema": {"type": "object", "xml": {"namespace": NS}}, "example": xml}
    return c


def _error(status):
    desc, ej = ERRORES.get(status, ("Error", None))
    contenido = _contenido(ej) if ej else {
        "application/json": {"schema": {"type": "object"},
                             "example": {"error": {"codigo": "...", "mensaje": desc, "traza_id": "uuid"}}}}
    return {"description": desc, "content": contenido}


def especificacion(app):
    doc = app.config["DOC"]
    rutas = {}
    for r in doc["rutas"]:
        op = {"summary": r["resumen"], "tags": [app.config["SERVICIO"]], "description": r.get("descripcion", "")}
        if r.get("permisos"):
            op["description"] += "\n\n**Permiso requerido (cualquiera):** " + ", ".join(f"`{p}`" for p in r["permisos"])
        if r.get("solo_json"):
            op["description"] += "\n\n**Solo JSON** (app móvil), como indica el contrato."
        op["security"] = [] if r.get("publico") else [{"bearer": []}]
        params = [{"name": n, "in": en, "required": en == "path", "description": d,
                   "schema": {"type": t}} for (n, en, t, d) in r.get("parametros", [])]
        params += [{"name": "Accept", "in": "header", "required": False,
                    "description": "application/json (Android) o application/xml (escritorio).",
                    "schema": {"type": "string", "enum": ["application/json", "application/xml"]}},
                   {"name": "X-Traza-Id", "in": "header", "required": False,
                    "description": "Id de correlación; si falta, el servicio genera uno y lo devuelve.",
                    "schema": {"type": "string"}}]
        op["parameters"] = params
        if r.get("cuerpo"):
            op["requestBody"] = {"required": True, "content": _contenido(r["cuerpo"], r.get("solo_json"))}
        resp = {}
        for status, (desc, ejemplo) in (r.get("respuestas") or {}).items():
            resp[str(status)] = {"description": desc}
            if ejemplo:
                resp[str(status)]["content"] = _contenido(ejemplo)
        errores = set(r.get("errores", [])) | {429, 503}
        if not r.get("publico"):
            errores |= {401}
        for e in sorted(errores):
            resp[str(e)] = _error(e)
        op["responses"] = resp
        rutas.setdefault(r["ruta"], {})[r["metodo"].lower()] = op
    rutas[f"{config.PREFIJO}/salud"] = {"get": {
        "summary": "Estado del servicio y de sus dependencias", "tags": ["operación"], "security": [],
        "responses": {"200": {"description": "Dependencias en orden", "content": _contenido("Salud.ok")},
                      "503": {"description": "Alguna dependencia no responde (estado degradado)"}}}}
    return {
        "openapi": "3.0.3",
        "info": {"title": doc["titulo"], "version": config.VERSION,
                 "description": doc["descripcion"] + "\n\nPlataforma de Microhubs · Codex Innovations · Equipo 04 · "
                 f"contrato v1. Puerto: {doc['puerto']}. Respuesta JSON o XML (urn:microhubs:v1) según `Accept`. "
                 "Errores: `{codigo, mensaje, detalles, traza_id}`."},
        "servers": [{"url": "/", "description": "Este servicio"}],
        "components": {"securitySchemes": {"bearer": {
            "type": "http", "scheme": "bearer", "bearerFormat": "JWT",
            "description": "Token de acceso del servicio de autenticación (5101). Se valida la firma, la vigencia "
                           "y que la sesión siga activa en Redis."}}},
        "paths": rutas,
    }


def pagina_swagger(titulo):
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><title>{titulo} · Swagger</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.14/swagger-ui.css">
</head><body><div id="swagger"></div>
<script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.14/swagger-ui-bundle.js"></script>
<script>SwaggerUIBundle({{url: "{config.PREFIJO}/openapi.json", dom_id: "#swagger", persistAuthorization: true}});</script>
</body></html>"""
