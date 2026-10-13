"""
evidencias.py — Evidencias REALES de petición y respuesta de los 8 microservicios.

Ejecuta contra los servicios levantados (docker-compose.integrado.yml) un
recorrido completo de casos por endpoint: operaciones correctas, parámetros
inválidos, registros inexistentes, acceso sin permiso, token inválido, sesión
revocada y errores de negocio. De cada caso guarda:

  · URL, método, encabezados (el token se recorta) y cuerpo JSON o XML.
  · Código HTTP, encabezados relevantes y respuesta completa.
  · Lo que quedó en PostgreSQL, MongoDB o Redis después de la petición.
  · Resultado esperado contra obtenido (PASA / FALLA).

Uso (desde la raíz del repositorio, con el backend arriba):

  docker compose -f docker-compose.integrado.yml exec entregas python pruebas/evidencias.py
  docker compose -f docker-compose.integrado.yml cp entregas:/tmp/evidencias ./evidencias

Genera en ./evidencias: evidencias.html (para capturas), evidencias.md (para
el reporte), pruebas.md (tabla de casos) y evidencias.json (datos crudos).
Cambia datos (cierra entregas, crea candidatos): úsese en la base de demostración.
"""
import argparse
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("LOG_STDOUT", "0")

from comun import datos as bd  # noqa: E402
from pruebas.preparar_entregas import preparar  # noqa: E402

PUERTOS = {"auth": 5101, "usuarios": 5102, "productos": 5103, "pedidos": 5104, "entregas": 5105,
           "planeacion": 5106, "documentos": 5107, "zonas": 5108, "microhubs": 5109, "seguimiento": 5110}
CLAVE = os.environ.get("MICROHUBS_CLAVE", "Codex#2026")
NS = "urn:microhubs:v1"
JPEG = bytes([0xFF, 0xD8, 0xFF, 0xE0, 0, 16, 74, 70, 73, 70, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0]) + bytes(range(256))
B64 = __import__("base64").b64encode(JPEG).decode()


def recortar(texto, limite=140):
    return texto if len(texto) <= limite else texto[:60] + f"…({len(texto)} caracteres)"


def limpiar(v):
    """Recorta tokens y Base64 largos y oculta las claves, para que la evidencia se pueda leer y publicar."""
    if isinstance(v, dict):
        return {k: ("********" if k == "clave" else limpiar(x)) for k, x in v.items()}
    if isinstance(v, list):
        return [limpiar(x) for x in v]
    if isinstance(v, str):
        return recortar(v)
    return v


def limpiar_xml(texto):
    return re.sub(r">([^<]{140,})<", lambda m: ">" + recortar(m.group(1)) + "<", texto)


def xml(raiz, campos):
    def el(k, v):
        if isinstance(v, dict):
            return f"<{k}>" + "".join(el(a, b) for a, b in v.items()) + f"</{k}>"
        return f"<{k}>{v}</{k}>"
    return f'<?xml version="1.0" encoding="UTF-8"?><{raiz} xmlns="{NS}">' + "".join(el(k, v) for k, v in campos.items()) + f"</{raiz}>"


class Respuesta:
    def __init__(self, status, encabezados, texto, ms, traza):
        self.status, self.encabezados, self.texto, self.ms, self.traza = status, encabezados, texto, ms, traza
        try:
            self.json = json.loads(texto) if texto and texto.lstrip().startswith(("{", "[")) else None
        except ValueError:
            self.json = None


class Evidencias:
    def __init__(self, plantilla):
        self.plantilla, self.casos, self.tokens = plantilla, [], {}

    # ---------------- HTTP ----------------
    def url(self, servicio, ruta):
        return self.plantilla.format(servicio=servicio, puerto=PUERTOS[servicio]) + "/api/v1/" + ruta

    def http(self, servicio, metodo, ruta, cuerpo=None, formato="json", token=None, encabezados=None):
        traza = str(uuid.uuid4())
        enc = {"Accept": "application/xml" if formato == "xml" else "application/json", "X-Traza-Id": traza}
        if token:
            enc["Authorization"] = f"Bearer {token}"
        datos_envio = None
        if cuerpo is not None:
            if isinstance(cuerpo, str):
                datos_envio, enc["Content-Type"] = cuerpo.encode("utf-8"), "application/xml"
            else:
                datos_envio, enc["Content-Type"] = json.dumps(cuerpo, ensure_ascii=False).encode("utf-8"), "application/json"
        enc.update(encabezados or {})
        req = urllib.request.Request(self.url(servicio, ruta), data=datos_envio, headers=enc, method=metodo)
        inicio = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                status, hdr, texto = r.status, dict(r.headers), r.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            status, hdr, texto = e.code, dict(e.headers), e.read().decode("utf-8")
        return Respuesta(status, hdr, texto, int((time.perf_counter() - inicio) * 1000), traza), enc

    def entrar(self, correo, formato="json"):
        r, _ = self.http("auth", "POST", "auth/login", {"correo": correo, "clave": CLAVE, "dispositivo": "evidencias"})
        if r.status != 200:
            raise SystemExit(f"No se pudo iniciar sesión con {correo}: {r.status} {r.texto}")
        self.tokens[correo] = r.json
        return r.json["token_acceso"]

    # ---------------- caso ----------------
    def caso(self, cid, servicio, titulo, objetivo, metodo, ruta, *, cuerpo=None, formato="json", token=None,
             esperado=200, explicacion="", evidencia=None, verificar=None, encabezados=None):
        try:
            r, enc = self.http(servicio, metodo, ruta, cuerpo, formato, token, encabezados)
        except Exception as e:                                         # el servicio no respondió
            self.casos.append({"id": cid, "servicio": servicio, "titulo": titulo, "objetivo": objetivo,
                               "metodo": metodo, "url": self.url(servicio, ruta), "estado": "FALLA",
                               "esperado": esperado, "obtenido": f"sin conexión: {e}"})
            print(f"  FALLA {cid} {titulo}: {e}")
            return None
        ok = r.status == esperado
        nota = ""
        if ok and verificar:
            try:
                ok = bool(verificar(r))
                nota = "" if ok else "La respuesta no tiene el contenido esperado."
            except Exception as e:
                ok, nota = False, f"Verificación: {e}"
        ev = []
        if evidencia:
            try:
                ev = evidencia(r) or []
            except Exception as e:
                ev = [{"motor": "—", "consulta": "evidencia", "resultado": f"No se pudo consultar: {e}"}]
        enc_mostrar = {k: (recortar(v, 40) if k == "Authorization" else v) for k, v in enc.items()}
        if r.json is not None:
            respuesta = json.dumps(limpiar(r.json), ensure_ascii=False, indent=2)
        else:
            respuesta = limpiar_xml(r.texto) if r.texto else "(sin cuerpo)"
        if isinstance(cuerpo, str):
            cuerpo_txt = re.sub(r"<clave>[^<]*</clave>", "<clave>********</clave>", cuerpo)
        elif cuerpo is not None:
            cuerpo_txt = json.dumps(limpiar(cuerpo), ensure_ascii=False, indent=2)
        else:
            cuerpo_txt = ""
        relevantes = {k: v for k, v in r.encabezados.items()
                      if k.lower() in ("content-type", "x-traza-id", "x-cache", "retry-after", "www-authenticate")}
        self.casos.append({"id": cid, "servicio": servicio, "puerto": PUERTOS[servicio], "titulo": titulo,
                           "objetivo": objetivo, "metodo": metodo, "url": self.url(servicio, ruta),
                           "encabezados": enc_mostrar, "cuerpo": cuerpo_txt, "status": r.status,
                           "encabezados_respuesta": relevantes, "respuesta": respuesta, "ms": r.ms, "traza": r.traza,
                           "esperado": esperado, "obtenido": r.status, "estado": "PASA" if ok else "FALLA",
                           "nota": nota, "explicacion": explicacion, "evidencia": ev})
        print(f"  {'PASA ' if ok else 'FALLA'} {cid} {metodo} {ruta} → {r.status} (esperado {esperado})")
        return r


# --------------------------------------------------------------------
# Consultas de evidencia
# --------------------------------------------------------------------
def pg(sql, args=()):
    with bd.conexion(autocommit=True) as con, con.cursor() as cur:
        cur.execute(sql, args)
        filas = cur.fetchall()
    return {"motor": "PostgreSQL", "consulta": sql, "resultado": json.loads(json.dumps(filas, default=str))}


def rd(*comandos):
    out = []
    for c in comandos:
        cliente = bd.r_cache if c[0] == 1 else bd.r_sesion
        nombre, *args = c[1:]
        valor = getattr(cliente, nombre.lower())(*args)
        out.append({"comando": f"{'db1 ' if c[0] == 1 else ''}{nombre} {' '.join(map(str, args))}",
                    "valor": sorted(valor) if isinstance(valor, set) else valor})
    return {"motor": "Redis", "consulta": "; ".join(o["comando"] for o in out), "resultado": out}


def mg(descripcion, fn):
    db = bd.mongo()
    if db is None:
        return {"motor": "MongoDB", "consulta": descripcion, "resultado": "MongoDB no configurado"}
    return {"motor": "MongoDB", "consulta": descripcion, "resultado": json.loads(json.dumps(fn(db), default=str))}


def sin_contenido(doc):
    return {k: v for k, v in doc.items() if k != "contenido"} if doc else doc


# --------------------------------------------------------------------
# Recorrido
# --------------------------------------------------------------------
def ejecutar(ev):
    print("Preparando datos de demostración (2 entregas en ruta para repartidor1)…")
    prep = preparar("repartidor1@codex.mx", 2)
    e1, e2 = prep[0]["entrega_id"], prep[1]["entrega_id"]

    # ---------- 1. AUTENTICACIÓN ----------
    print("1. Autenticación (5101)")
    r = ev.caso("AUTH-01", "auth", "Iniciar sesión (JSON)", "Emitir el JWT de acceso y el token de renovación del repartidor.",
                "POST", "auth/login", cuerpo={"correo": "repartidor1@codex.mx", "clave": CLAVE, "dispositivo": "Pixel 7"},
                explicacion="bcrypt valida la clave; el jti del acceso se agrega a la sesión activa en Redis y la renovación "
                            "se guarda como hash con TTL de 7 días. El login queda en la bitácora.",
                evidencia=lambda r: [rd((0, "SMEMBERS", "auth:sesion:7"), (0, "TTL", "auth:sesion:7"),
                                        (0, "TTL", "auth:refresh:" + hashlib.sha256(r.json["token_renovacion"].encode()).hexdigest())),
                                     pg("SELECT fecha, modulo, accion, detalle FROM auditoria WHERE correo_intento IS NULL "
                                        "AND usuario_id = 7 AND modulo = 'auth' ORDER BY id DESC LIMIT 1")],
                verificar=lambda r: r.json["tipo"] == "Bearer" and "entregas.cerrar" in r.json["usuario"]["permisos"])
    rep = r.json
    ev.tokens["repartidor1@codex.mx"] = rep
    t_rep = rep["token_acceso"]
    ev.caso("AUTH-02", "auth", "Iniciar sesión (XML)", "La app de escritorio entra con XML validado por auth.xsd.",
            "POST", "auth/login", cuerpo=xml("login", {"correo": "planeador@codex.mx", "clave": CLAVE}), formato="xml",
            explicacion="El cuerpo XML se valida contra los XSD antes de procesarse; la respuesta <sesion> también cumple el XSD.",
            verificar=lambda r: "<sesion" in r.texto and "<rol>planeador</rol>" in r.texto)
    ev.caso("AUTH-03", "auth", "Clave incorrecta", "Rechazar credenciales y contar el intento.", "POST", "auth/login",
            cuerpo={"correo": "auditor@codex.mx", "clave": "incorrecta"}, esperado=401,
            explicacion="Cada intento fallido incrementa un contador en Redis; al quinto la cuenta se bloquea 15 minutos (423).",
            evidencia=lambda r: [rd((0, "GET", "auth:intentos:auditor@codex.mx"), (0, "TTL", "auth:intentos:auditor@codex.mx"))],
            verificar=lambda r: "Intento" in r.json["error"]["mensaje"])
    ev.caso("AUTH-04", "auth", "Correo con formato inválido", "Validación de entrada con detalle por campo.", "POST",
            "auth/login", cuerpo={"correo": "sin-arroba", "clave": ""}, esperado=422,
            verificar=lambda r: {d["campo"] for d in r.json["error"]["detalles"]} == {"correo", "clave"})
    ev.caso("AUTH-05", "auth", "XML con DTD (ataque XXE)", "Rechazar entidades externas y DTD.", "POST", "auth/login",
            cuerpo='<?xml version="1.0"?><!DOCTYPE x [<!ENTITY e SYSTEM "file:///etc/passwd">]>'
                   f'<login xmlns="{NS}"><correo>&e;</correo><clave>x</clave></login>', formato="xml", esperado=400,
            explicacion="El lector XML (defusedxml) prohíbe DTD y entidades; el error también llega en XML.")
    ev.caso("AUTH-06", "auth", "Validar token", "Comprobar firma, vigencia y sesión activa en Redis.", "GET",
            "auth/validar", token=t_rep, verificar=lambda r: r.json["valido"] is True)
    ev.caso("AUTH-07", "auth", "Token alterado", "Un token con la firma modificada no pasa.", "GET", "auth/validar",
            token=t_rep[:-4] + "abcd", esperado=401, verificar=lambda r: r.json["error"]["codigo"] == "TOKEN_INVALIDO")
    otra = ev.http("auth", "POST", "auth/login", {"correo": "repartidor1@codex.mx", "clave": CLAVE})[0].json
    r = ev.caso("AUTH-08", "auth", "Renovar sesión", "Obtener tokens nuevos con el token de renovación (rotación).",
                "POST", "auth/renovar", cuerpo={"token_renovacion": otra["token_renovacion"]},
                explicacion="El token de renovación usado se borra de Redis y su acceso anterior queda revocado.",
                evidencia=lambda r: [rd((0, "EXISTS", "auth:refresh:" + hashlib.sha256(otra["token_renovacion"].encode()).hexdigest()))])
    ev.caso("AUTH-09", "auth", "Reusar un token de renovación", "Un token de renovación sirve una sola vez.", "POST",
            "auth/renovar", cuerpo={"token_renovacion": otra["token_renovacion"]}, esperado=401)
    nueva = r.json if r is not None and r.status == 200 else None
    if nueva:
        jti = json.loads(__import__("base64").urlsafe_b64decode(nueva["token_acceso"].split(".")[1] + "==")).get("jti")
        ev.caso("AUTH-10", "auth", "Cerrar sesión", "Revocar el acceso del encabezado y la renovación del cuerpo.", "POST",
                "auth/salir", cuerpo={"token_renovacion": nueva["token_renovacion"]}, token=nueva["token_acceso"], esperado=204,
                explicacion="El jti se agrega a la lista de revocados con TTL igual a su vida restante y sale del conjunto de sesión.",
                evidencia=lambda r: [rd((0, "TTL", f"auth:jti:revocado:{jti}"), (0, "SISMEMBER", "auth:sesion:7", jti))])
        ev.caso("AUTH-11", "usuarios", "Usar un token revocado", "Una sesión cerrada ya no entra a ningún servicio.", "GET",
                "usuarios/yo", token=nueva["token_acceso"], esperado=401,
                explicacion="El servicio de usuarios consulta auth:jti:revocado en Redis: la revocación es común a todos.")

    # ---------- 2. USUARIOS ----------
    print("2. Usuarios (5102)")
    t_adm = ev.entrar("admin@codex.mx")
    t_plan = ev.entrar("planeador@codex.mx")
    t_aud = ev.entrar("auditor@codex.mx")
    ev.caso("USR-01", "usuarios", "Mi perfil (JSON)", "Consultar el perfil de quien inició sesión.", "GET", "usuarios/yo",
            token=t_rep, verificar=lambda r: r.json["correo"] == "repartidor1@codex.mx")
    ev.caso("USR-02", "usuarios", "Mi perfil (XML)", "El mismo recurso en XML según Accept.", "GET", "usuarios/yo",
            token=t_plan, formato="xml", verificar=lambda r: "<usuario" in r.texto)
    ev.caso("USR-03", "usuarios", "Actualizar mi teléfono (PATCH)", "Modificar un dato del perfil.", "PATCH", "usuarios/yo",
            cuerpo={"telefono": "8112345678"}, token=t_rep,
            explicacion="El trigger de auditoría registra el cambio con el usuario que actuó.",
            evidencia=lambda r: [pg("SELECT id, telefono, actualizado_en FROM usuario WHERE id = 7"),
                                 pg("SELECT fecha, accion, entidad, detalle FROM auditoria WHERE entidad = 'usuario' "
                                    "AND entidad_id = '7' ORDER BY id DESC LIMIT 1")])
    ev.caso("USR-04", "usuarios", "Teléfono inválido", "Validación de patrón (10 dígitos).", "PATCH", "usuarios/yo",
            cuerpo={"telefono": "12ab"}, token=t_rep, esperado=422)
    ev.caso("USR-05", "usuarios", "Lista de usuarios (administrador)", "Búsqueda y paginación.", "GET",
            "usuarios?q=codex&rol=operador&pagina=1&por_pagina=5", token=t_adm,
            verificar=lambda r: r.json["paginacion"]["total"] >= 1)
    ev.caso("USR-06", "usuarios", "Lista de usuarios sin permiso", "Un repartidor no tiene usuarios.ver.", "GET",
            "usuarios", token=t_rep, esperado=403,
            evidencia=lambda r: [pg("SELECT fecha, modulo, accion, detalle, exitoso FROM auditoria WHERE accion = "
                                    "'acceso_denegado' ORDER BY id DESC LIMIT 1")])
    ev.caso("USR-07", "usuarios", "Usuario inexistente", "Registro que no existe.", "GET", "usuarios/999999",
            token=t_adm, esperado=404)

    # ---------- 3. PRODUCTOS ----------
    print("3. Productos (5103)")
    ev.caso("PRO-01", "productos", "Productos con búsqueda (caché vacía)", "Consultar productos; la respuesta se guarda en Redis.",
            "GET", "productos?q=arroz&pagina=1&por_pagina=5", token=t_plan,
            explicacion="Encabezado X-Cache: MISS. La llave cache:catalogo:productos:* expira según cache_catalogo_segundos.",
            evidencia=lambda r: [rd(*[(1, "TTL", k) for k in bd.r_cache.keys("cache:catalogo:productos:*")[:3]])])
    ev.caso("PRO-02", "productos", "Misma consulta (desde Redis)", "La segunda consulta no toca PostgreSQL.", "GET",
            "productos?q=arroz&pagina=1&por_pagina=5", token=t_plan, verificar=lambda r: r.encabezados.get("X-Cache") == "HIT")
    r = ev.caso("PRO-03", "productos", "Productos (XML)", "Lista en XML válida contra catalogos.xsd.", "GET",
                "productos?pagina=1&por_pagina=2", token=t_plan, formato="xml")
    pid_prod = int(re.search(r"<id>(\d+)</id>", r.texto).group(1)) if r and r.status == 200 else 1
    ev.caso("PRO-04", "productos", "Un producto", "Detalle por id.", "GET", f"productos/{pid_prod}", token=t_plan)
    ev.caso("PRO-05", "productos", "Producto inexistente", "Registro que no existe.", "GET", "productos/999999",
            token=t_plan, esperado=404)
    ev.caso("PRO-06", "productos", "Paginación fuera de rango", "por_pagina máximo 100.", "GET", "productos?por_pagina=500",
            token=t_plan, esperado=400)
    ev.caso("PRO-07", "productos", "Sin token", "Todo endpoint protegido exige Authorization: Bearer.", "GET", "productos",
            esperado=401)

    # ---------- 4. ZONAS ----------
    print("4. Zonas (5108)")
    ev.caso("ZON-01", "zonas", "Zonas (XML)", "Colonias atendidas con centroide, válidas contra catalogos.xsd.", "GET", "zonas",
            token=t_plan, formato="xml")
    ev.caso("ZON-02", "zonas", "Una zona", "Detalle por id.", "GET", "zonas/1", token=t_plan)
    ev.caso("ZON-03", "zonas", "Zona inexistente", "Registro que no existe.", "GET", "zonas/999999", token=t_plan, esperado=404)
    ev.caso("ZON-04", "zonas", "Sin token", "Todo endpoint protegido exige Authorization: Bearer.", "GET", "zonas", esperado=401)

    # ---------- 5. MICROHUBS ----------
    print("5. Microhubs (5109)")
    ev.caso("MIC-01", "microhubs", "Microhubs activos", "Microhubs con coordenadas y radio.", "GET", "microhubs?estatus=activo",
            token=t_plan)
    ev.caso("MIC-02", "microhubs", "Microhub inexistente", "Registro que no existe.", "GET", "microhubs/999999",
            token=t_plan, esperado=404)
    ev.caso("MIC-03", "microhubs", "Sin token", "Todo endpoint protegido exige Authorization: Bearer.", "GET", "microhubs",
            esperado=401)

    # ---------- 6. PEDIDOS ----------
    print("6. Pedidos (5104)")
    r = ev.caso("PED-01", "pedidos", "Pedidos entregados (JSON)", "Lista filtrada por estado y fechas.", "GET",
                "pedidos?estado=entregado&pagina=1&por_pagina=5", token=t_plan)
    pid = r.json["datos"][0]["id"] if r and r.status == 200 and r.json["datos"] else 1
    ev.caso("PED-02", "pedidos", "Pedidos (XML)", "La misma lista en XML.", "GET", "pedidos?estado=entregado&por_pagina=2",
            token=t_plan, formato="xml")
    ev.caso("PED-03", "pedidos", "Detalle con líneas", "Cliente, domicilio y líneas del pedido.", "GET", f"pedidos/{pid}",
            token=t_plan, verificar=lambda r: len(r.json["lineas"]) >= 1)
    ev.caso("PED-04", "pedidos", "Historial de estados", "Cambios de estado con usuario y fecha.", "GET",
            f"pedidos/{pid}/historial", token=t_plan, evidencia=lambda r: [pg(
                "SELECT fecha, estado_anterior, estado_nuevo, usuario_id FROM historial_estatus WHERE pedido_id = %s "
                "ORDER BY fecha, id", (pid,))])
    ev.caso("PED-05", "pedidos", "Filtro inválido", "Un estado que no existe se rechaza.", "GET", "pedidos?estado=inventado",
            token=t_plan, esperado=400)
    fuera = bd.consultar("SELECT p.id FROM pedido p WHERE p.microhub_id <> 1 ORDER BY p.id LIMIT 1", una=True)["id"]
    t_op1 = ev.entrar("operador.mh01@codex.mx")
    ev.caso("PED-06", "pedidos", "Pedido fuera del ámbito", "El operador del MH-01 no ve pedidos de otro microhub (RN22).",
            "GET", f"pedidos/{fuera}", token=t_op1, esperado=404,
            explicacion="El ámbito lo decide PostgreSQL con fn_pedidos_visibles; el servicio no lo puede saltar.")
    ev.caso("PED-07", "pedidos", "Cerrar desde pedidos", "Los cierres de entrega solo se registran en el servicio de entregas.",
            "POST", f"pedidos/{pid}/estado", cuerpo={"estado": "entregado"}, token=t_adm, esperado=409)
    ent = bd.consultar("SELECT p.id, p.microhub_id FROM pedido p WHERE p.estado = 'entregado' AND p.microhub_id IS NOT NULL "
                       "ORDER BY p.id LIMIT 1", una=True)
    t_opx = ev.entrar(f"operador.mh0{ent['microhub_id']}@codex.mx")
    ev.caso("PED-08", "pedidos", "Transición ilegal (regla del motor)", "Un pedido entregado no puede regresar a preparación.",
            "PATCH", f"pedidos/{ent['id']}/estado", cuerpo={"estado": "en_preparacion"}, token=t_opx, esperado=422,
            explicacion="El trigger fn_valida_transicion de PostgreSQL rechaza la transición (RN20); el estado no cambia.",
            evidencia=lambda r: [pg("SELECT id, folio, estado FROM pedido WHERE id = %s", (ent["id"],))])

    # ---------- 7. DOCUMENTOS ----------
    print("7. Documentos (5107)")
    r = ev.caso("DOC-01", "documentos", "Subir evidencia de entrega", "Guardar la foto en MongoDB ligada a la entrega.",
                "POST", "documentos", token=t_rep, esperado=201,
                cuerpo={"nombre": f"evidencia-entrega-{e1}.jpg", "tipo_mime": "image/jpeg", "contenido_base64": B64,
                        "referencia": {"tipo": "entrega", "id": str(e1)}},
                explicacion="Se valida que el contenido sea JPEG real, se calcula su SHA-256 y que la entrega sea del repartidor.",
                evidencia=lambda r: [mg(f"db.documentos.findOne({{_id: ObjectId('{r.json['id']}')}}, {{contenido: 0}})",
                                        lambda db: sin_contenido(db.documentos.find_one({"_id": __import__("bson").ObjectId(r.json["id"])})))])
    doc1 = r.json["id"] if r and r.status == 201 else None
    r = ev.caso("DOC-02", "documentos", "Subir evidencia de la segunda entrega", "Evidencia para el cierre parcial.", "POST",
                "documentos", token=t_rep, esperado=201,
                cuerpo={"nombre": f"evidencia-entrega-{e2}.jpg", "tipo_mime": "image/jpeg", "contenido_base64": B64,
                        "referencia": {"tipo": "entrega", "id": str(e2)}})
    doc2 = r.json["id"] if r and r.status == 201 else None
    ev.caso("DOC-03", "documentos", "Tipo de archivo falso", "Un PDF declarado como JPEG se rechaza por su firma.", "POST",
            "documentos", token=t_rep, esperado=422,
            cuerpo={"nombre": "foto.jpg", "tipo_mime": "image/jpeg",
                    "contenido_base64": __import__("base64").b64encode(b"%PDF-1.4 falso").decode(),
                    "referencia": {"tipo": "entrega", "id": str(e1)}})
    t_rep2 = ev.entrar("repartidor2@codex.mx")
    ev.caso("DOC-04", "documentos", "Evidencia en entrega ajena", "Un repartidor no adjunta a entregas de otro.", "POST",
            "documentos", token=t_rep2, esperado=403,
            cuerpo={"nombre": "x.jpg", "tipo_mime": "image/jpeg", "contenido_base64": B64,
                    "referencia": {"tipo": "entrega", "id": str(e1)}})
    r = ev.caso("DOC-05", "documentos", "Documento temporal", "Documento que después se elimina.", "POST", "documentos",
                token=t_rep, esperado=201, cuerpo={"nombre": "borrador.jpg", "tipo_mime": "image/jpeg",
                                                   "contenido_base64": B64, "referencia": {"tipo": "usuario", "id": "7"}})
    doc_tmp = r.json["id"] if r and r.status == 201 else "0" * 24
    ev.caso("DOC-06", "documentos", "Mis documentos", "Filtro por referencia.", "GET",
            f"documentos?referencia_tipo=entrega&referencia_id={e1}", token=t_rep)
    ev.caso("DOC-07", "documentos", "Metadatos (XML)", "Documento en XML, sin contenido.", "GET", f"documentos/{doc1}",
            token=t_rep, formato="xml")
    ev.caso("DOC-08", "documentos", "Contenido en Base64", "Recuperar el archivo.", "GET", f"documentos/{doc1}/contenido",
            token=t_rep, verificar=lambda r: r.json["contenido_base64"] == B64)
    ev.caso("DOC-09", "documentos", "Eliminar documento (DELETE)", "Borrar un documento propio.", "DELETE",
            f"documentos/{doc_tmp}", token=t_rep, esperado=204,
            evidencia=lambda r: [mg(f"db.documentos.countDocuments({{_id: ObjectId('{doc_tmp}')}})",
                                    lambda db: db.documentos.count_documents({"_id": __import__("bson").ObjectId(doc_tmp)}))])
    ev.caso("DOC-10", "documentos", "Id inexistente", "Registro que no existe.", "GET", "documentos/" + "f" * 24,
            token=t_rep, esperado=404)

    # ---------- 8. SEGUIMIENTO ----------
    print("8. Seguimiento (5110)")
    import datetime as dt
    hora = lambda minutos=0: (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=minutos)).isoformat(timespec="seconds")
    ahora = hora()
    ev.caso("SEG-01", "seguimiento", "Enviar puntos GPS", "Guardar el recorrido del repartidor en MongoDB.", "POST",
            f"seguimiento/{e1}/ubicaciones", token=t_rep, esperado=201,
            cuerpo={"puntos": [{"latitud": 25.7480, "longitud": -100.3600, "precision_m": 9.0, "capturado_en": hora(6)},
                               {"latitud": 25.7486, "longitud": -100.3606, "precision_m": 8.0, "capturado_en": hora(4)},
                               {"latitud": 25.7491, "longitud": -100.3611, "precision_m": 8.5, "capturado_en": hora(2)}]},
            evidencia=lambda r: [mg(f"db.ubicaciones_entrega.find({{entrega_id: NumberLong({e1})}}).sort({{capturado_en: 1}})",
                                    lambda db: [{k: v for k, v in d.items() if k != "_id"}
                                                for d in db.ubicaciones_entrega.find({"entrega_id": e1}).sort("capturado_en", 1)]),
                                 mg("db.ubicaciones_entrega.getIndexes()",
                                    lambda db: list(db.ubicaciones_entrega.index_information().keys()))])
    ev.caso("SEG-02", "seguimiento", "Resumen del recorrido", "Agregación en MongoDB sobre los puntos GPS.", "GET",
            f"seguimiento/{e1}/recorrido", token=t_rep, verificar=lambda r: r.json["puntos"] == 3,
            explicacion="Pipeline: $match por entrega_id → $sort por capturado_en → $group (conteo, inicio, fin, precisión "
                        "promedio y ruta). La distancia se calcula con Haversine sobre la ruta.")
    ev.caso("SEG-03", "seguimiento", "Recorrido de otro repartidor", "El repartidor 2 no ve el rastro de la entrega del repartidor 1.",
            "GET", f"seguimiento/{e1}/recorrido", token=t_rep2, esperado=404)
    ev.caso("SEG-04", "seguimiento", "Recorrido sin token", "Todo endpoint protegido exige Authorization: Bearer.", "GET",
            f"seguimiento/{e1}/recorrido", esperado=401)

    # ---------- 9. ENTREGAS ----------
    print("9. Entregas (5105)")
    ev.caso("ENT-01", "entregas", "Mis entregas", "Paradas abiertas del repartidor en el turno de hoy (RN25).", "GET",
            "entregas/mias?pagina=1&por_pagina=20", token=t_rep,
            verificar=lambda r: {e1, e2} <= {x["id"] for x in r.json["datos"]})
    r = ev.caso("ENT-02", "entregas", "Detalle de la entrega", "Cliente, domicilio y líneas.", "GET", f"entregas/{e1}", token=t_rep)
    det1 = r.json
    det2 = ev.http("entregas", "GET", f"entregas/{e2}", token=t_rep)[0].json
    ev.caso("ENT-03", "entregas", "Entrega de otro repartidor", "El repartidor 2 no ve la entrega del repartidor 1.", "GET",
            f"entregas/{e1}", token=t_rep2, esperado=404)
    uid = str(uuid.uuid4())
    cierre = {"resultado": "entregado", "monto_cobrado": det1["total"] if det1 else 0, "cambio_entregado": 0.0,
              "ubicacion": {"latitud": 25.7491, "longitud": -100.3611, "precision_m": 8.5},
              "evidencia_ids": [doc1], "capturado_en": ahora, "id_cliente_local": uid}
    ev.caso("ENT-04", "entregas", "Monto incorrecto (regla de negocio)", "Una entrega completa cobra el total (RN27).", "POST",
            f"entregas/{e1}/resultado", cuerpo={**cierre, "monto_cobrado": 1.0}, token=t_rep, esperado=422)
    ev.caso("ENT-05", "entregas", "Cerrar entrega como entregado", "Registrar el resultado con evidencia y ubicación.", "POST",
            f"entregas/{e1}/resultado", cuerpo=cierre, token=t_rep, esperado=201,
            verificar=lambda r: r.json["estado_pedido"] == "entregado" and r.json["duplicado"] is False,
            explicacion="Una sola transacción: cierra la entrega, cambia el pedido (el trigger valida la transición y escribe "
                        "historial y bitácora) y el trigger de cierre avisa al cliente. La operación se registra en MongoDB.",
            evidencia=lambda r: [
                pg("SELECT id, cierre_en, resultado, monto_cobrado, id_cliente_local, evidencia_ids, cierre_latitud, "
                   "cierre_longitud FROM entrega WHERE id = %s", (e1,)),
                pg("SELECT estado_anterior, estado_nuevo, usuario_id, fecha FROM historial_estatus WHERE pedido_id = %s "
                   "ORDER BY id DESC LIMIT 1", (det1["pedido_id"],)),
                pg("SELECT destinatario_id, tipo, titulo, mensaje, referencia_tipo, referencia_id FROM web_notificacion "
                   "WHERE referencia_tipo = 'pedido' AND referencia_id = %s ORDER BY id DESC LIMIT 1", (str(det1["pedido_id"]),)),
                mg(f"db.sincronizaciones_moviles.findOne({{operacion_uuid: '{uid}'}})",
                   lambda db: {k: v for k, v in (db.sincronizaciones_moviles.find_one({"operacion_uuid": uid}) or {}).items() if k != "_id"})])
    ev.caso("ENT-06", "entregas", "Reintento con el mismo UUID", "Idempotencia: el cierre no se aplica dos veces.", "POST",
            f"entregas/{e1}/resultado", cuerpo=cierre, token=t_rep, esperado=200,
            verificar=lambda r: r.json["duplicado"] is True,
            explicacion="La respuesta es la misma con duplicado=true. MongoDB actualiza el documento de la operación (intentos = 2).",
            evidencia=lambda r: [mg(f"db.sincronizaciones_moviles.findOne({{operacion_uuid: '{uid}'}}, {{estado: 1, intentos: 1}})",
                                    lambda db: {k: v for k, v in (db.sincronizaciones_moviles.find_one({"operacion_uuid": uid}) or {}).items()
                                                if k in ("estado", "intentos", "sincronizado_en")})])
    ev.caso("ENT-07", "entregas", "Otro cierre sobre la misma entrega", "Conflicto: ya estaba cerrada con otra operación.", "POST",
            f"entregas/{e1}/resultado", cuerpo={**cierre, "id_cliente_local": str(uuid.uuid4())}, token=t_rep, esperado=409)
    ev.caso("ENT-08", "entregas", "Detalle tras el cierre", "El repartidor deja de ver el domicilio (RN26).", "GET",
            f"entregas/{e1}", token=t_rep, esperado=404)
    if det2 and len(det2.get("lineas", [])) >= 2:
        l0, l1 = det2["lineas"][0], det2["lineas"][1]
        parcial = {"resultado": "parcial", "monto_cobrado": 10.0, "cambio_entregado": 0.0, "incidencia": "El cliente rechazó una línea.",
                   "lineas": [{"pedido_detalle_id": l0["pedido_detalle_id"], "cantidad_entregada": l0["cantidad"], "cantidad_devuelta": 0},
                              {"pedido_detalle_id": l1["pedido_detalle_id"], "cantidad_entregada": 0, "cantidad_devuelta": l1["cantidad"]}],
                   "ubicacion": {"latitud": 25.7491, "longitud": -100.3611}, "evidencia_ids": [doc2],
                   "capturado_en": ahora, "id_cliente_local": str(uuid.uuid4())}
        ev.caso("ENT-09", "entregas", "Parcial sin motivo", "Cada línea devuelta necesita motivo (RN28).", "POST",
                f"entregas/{e2}/resultado", cuerpo=parcial, token=t_rep, esperado=422)
        parcial["lineas"][1]["motivo"] = "El cliente la rechazó."
        ev.caso("ENT-10", "entregas", "Cerrar como entrega parcial", "Devolver al inventario lo que no se entregó.", "POST",
                f"entregas/{e2}/resultado", cuerpo=parcial, token=t_rep, esperado=201,
                explicacion="fn_devolver_inventario (la misma función que usa el web) regresa las unidades devueltas.",
                evidencia=lambda r: [pg("SELECT entrega_id, pedido_detalle_id, cantidad_entregada, cantidad_devuelta, motivo "
                                        "FROM entrega_linea WHERE entrega_id = %s", (e2,)),
                                     pg("SELECT tipo, producto_id, cantidad, existencia_resultante, motivo FROM movimiento_inventario "
                                        "WHERE referencia_id = %s AND tipo = 'devolucion_parcial'", (det2["pedido_id"],))])
    ev.caso("ENT-11", "entregas", "Entregas de un pedido (administrador)", "Consulta por pedido para el portal web.", "GET",
            f"entregas?pedido_id={det1['pedido_id']}", token=t_adm, verificar=lambda r: r.json["paginacion"]["total"] == 1)

    # ---------- 10. PLANEACIÓN ----------
    print("10. Planeación (5106)")
    ev.caso("PLA-01", "planeacion", "Candidatos (XML)", "Lista de ubicaciones candidatas.", "GET",
            "candidatos?pagina=1&por_pagina=3", token=t_plan, formato="xml")
    clave = "EV-" + uuid.uuid4().hex[:6].upper()
    nuevo = {"clave": clave, "nombre": "Alianza Norte", "latitud": "25.7601", "longitud": "-100.3555",
             "renta_estimada": "16000.00", "nomina_estimada": "40000.00", "servicios_estimados": "6500.00",
             "otros_costos": "4500.00", "superficie_m2": "110", "capacidad_fisica": "130", "accesibilidad_vial": "7",
             "zona_id": "3", "poblacion_cubierta": "5200", "radio_km": "1.5"}
    r = ev.caso("PLA-02", "planeacion", "Registrar candidato (XML)", "Alta con costo fijo calculado por PostgreSQL.", "POST",
                "candidatos", cuerpo=xml("candidato_nuevo", nuevo), formato="xml", token=t_plan, esperado=201,
                verificar=lambda r: "<costo_fijo>67000.00</costo_fijo>" in r.texto,
                evidencia=lambda r: [pg("SELECT id, clave, nombre, renta_estimada, costo_fijo, decision FROM ubicacion_candidata "
                                        "WHERE clave = %s", (clave,))])
    cid = int(re.search(r"<id>(\d+)</id>", r.texto).group(1)) if r and r.status == 201 else 1
    ev.caso("PLA-03", "planeacion", "Clave duplicada", "No se repite la clave de un candidato.", "POST", "candidatos",
            cuerpo=xml("candidato_nuevo", nuevo), formato="xml", token=t_plan, esperado=409)
    ev.caso("PLA-04", "planeacion", "Modificar candidato (PUT)", "Cambiar la renta recalcula el costo fijo.", "PUT",
            f"candidatos/{cid}", cuerpo={**nuevo, "nombre": "Alianza Norte (editado)", "renta_estimada": 18000},
            token=t_plan, verificar=lambda r: r.json["costo_fijo"] == 69000.0)
    ev.caso("PLA-05", "planeacion", "Simular candidato (XML)", "Viabilidad con los costos del candidato.", "POST",
            f"candidatos/{cid}/simular", cuerpo=f'<simular xmlns="{NS}"/>', formato="xml", token=t_plan,
            explicacion="Usa planeacion_calc.py (las mismas fórmulas del web) y guarda la ejecución en MongoDB.",
            evidencia=lambda r: [mg("db.ejecuciones_analiticas.find().sort({ejecutado_en: -1}).limit(1)",
                                    lambda db: {k: v for k, v in (db.ejecuciones_analiticas.find_one(sort=[("ejecutado_en", -1)]) or {}).items()
                                                if k != "_id"})])
    ev.caso("PLA-06", "planeacion", "Decisión sin motivo suficiente", "La decisión humana exige motivo.", "POST",
            f"candidatos/{cid}/decision", cuerpo={"decision": "aceptado", "motivo": "ok"}, token=t_plan, esperado=422)
    ev.caso("PLA-07", "planeacion", "Decisión humana de apertura", "Registrar la decisión con motivo.", "POST",
            f"candidatos/{cid}/decision", cuerpo={"decision": "condicionado", "motivo": "Renegociar la renta antes de firmar."},
            token=t_plan, evidencia=lambda r: [pg("SELECT id, decision, decision_motivo, decision_por, decision_en FROM "
                                                  "ubicacion_candidata WHERE id = %s", (cid,))])
    supuestos = {"demanda_diaria": 120, "operadores": 3, "repartidores": 4, "ticket": 135.0, "costo_entrega": 22.0,
                 "margen_bruto": 0.28, "renta": 18000.0, "nomina": 42000.0, "servicios": 7000.0, "otros": 5000.0,
                 "distancia_km": 2.4, "capacidad_fisica": 150}
    ev.caso("PLA-08", "planeacion", "Simulación libre: Escenario A", "Punto de equilibrio del caso de la retroalimentación.",
            "POST", "simulaciones", cuerpo={"supuestos": supuestos}, token=t_plan,
            verificar=lambda r: r.json["equilibrio"]["diario"] == 151.9,
            explicacion="72,000 de costos fijos entre 15.80 de margen por pedido = 4,557 pedidos al mes (151.9 al día).")
    r = ev.caso("PLA-09", "planeacion", "Guardar escenario", "Escenario compartido con el portal web.", "POST", "escenarios",
                cuerpo={"nombre": "Escenario A - evidencias", "candidato_id": cid, "supuestos": supuestos}, token=t_plan, esperado=201)
    esc = r.json["id"] if r and r.status == 201 else 0
    ev.caso("PLA-10", "planeacion", "Abrir escenario (XML)", "Escenario con supuestos y resultados.", "GET", f"escenarios/{esc}",
            token=t_plan, formato="xml")
    ev.caso("PLA-11", "planeacion", "Resumen de simulaciones", "Agregación $group en MongoDB por decisión.", "GET",
            "simulaciones/resumen", token=t_plan, verificar=lambda r: r.json["total"] >= 2,
            evidencia=lambda r: [mg("db.ejecuciones_analiticas.aggregate([{$match:{tipo_analisis:'punto_equilibrio'}}, "
                                    "{$group:{_id:'$resultados.decision', cantidad:{$sum:1}, utilizacion_promedio:{$avg:'$resultados.utilizacion'}}}])",
                                    lambda db: list(db.ejecuciones_analiticas.aggregate([
                                        {"$match": {"tipo_analisis": "punto_equilibrio"}},
                                        {"$group": {"_id": "$resultados.decision", "cantidad": {"$sum": 1},
                                                    "utilizacion_promedio": {"$avg": "$resultados.utilizacion"}}}])))])
    ev.caso("PLA-12", "planeacion", "Auditor intenta registrar", "El auditor solo consulta (RN-E01).", "POST", "candidatos",
            cuerpo={**nuevo, "clave": clave + "X"}, token=t_aud, esperado=403)
    ev.caso("PLA-13", "planeacion", "Auditor intenta simular", "Sin simulacion.ejecutar.", "POST", f"candidatos/{cid}/simular",
            cuerpo={}, token=t_aud, esperado=403)
    ev.caso("PLA-14", "planeacion", "Eliminar escenario (DELETE)", "Borrar un escenario.", "DELETE", f"escenarios/{esc}",
            token=t_plan, esperado=204)
    ev.caso("PLA-15", "planeacion", "Dar de baja candidato (DELETE)", "Baja lógica: se conserva su historia.", "DELETE",
            f"candidatos/{cid}", token=t_plan, esperado=204,
            evidencia=lambda r: [pg("SELECT id, clave, estatus, decision FROM ubicacion_candidata WHERE id = %s", (cid,))])
    ev.caso("PLA-16", "planeacion", "Candidato inexistente", "Registro que no existe.", "GET", "candidatos/999999",
            token=t_plan, esperado=404)

    # ---------- 11. TRANSVERSALES ----------
    print("11. Transversales")
    for s in PUERTOS:
        ev.caso(f"SAL-{s[:3].upper()}", s, f"Salud de {s}", "Estado del servicio y de sus dependencias.", "GET", "health",
                verificar=lambda r: r.json["estado"] == "ok")
    ev.caso("MON-01", "auth", "Registro de actividad", "Cada petición queda en MongoDB con su traza.", "GET", "auth/validar",
            token=t_adm, explicacion="El X-Traza-Id de la petición se recupera en logs_tecnicos.correlacion_id.",
            evidencia=lambda r: [mg(f"db.logs_tecnicos.findOne({{correlacion_id: '{r.traza}'}})",
                                    lambda db: {k: v for k, v in (db.logs_tecnicos.find_one({"correlacion_id": r.traza}) or {}).items()
                                                if k != "_id"}),
                                 mg("db.metricas_servicio.aggregate([{$group:{_id:'$etiquetas.servicio', peticiones:{$sum:1}, "
                                    "ms_promedio:{$avg:'$duracion_ms'}}}])",
                                    lambda db: list(db.metricas_servicio.aggregate([
                                        {"$group": {"_id": "$etiquetas.servicio", "peticiones": {"$sum": 1},
                                                    "ms_promedio": {"$avg": "$duracion_ms"}}}, {"$sort": {"_id": 1}}])))])
    # Límite de consumo: se agota al final para no frenar los demás casos.
    ultimo = None
    for _ in range(400):
        ultimo, _e = ev.http("zonas", "GET", "zonas")
        if ultimo.status == 429:
            break
    ev.caso("RAT-01", "zonas", "Límite de consumo excedido", "Más de 240 solicitudes por minuto desde la misma IP.",
            "GET", "zonas", esperado=429, verificar=lambda r: int(r.encabezados.get("Retry-After", 0)) >= 1,
            explicacion="Contador rate:zonas:{ip}:{minuto} en Redis (db 1) con TTL de 120 s; responde Retry-After.",
            evidencia=lambda r: [rd(*[(1, "GET", k) for k in bd.r_cache.keys("rate:zonas:*")[:1]],
                                    *[(1, "TTL", k) for k in bd.r_cache.keys("rate:zonas:*")[:1]])])


# --------------------------------------------------------------------
# Salidas
# --------------------------------------------------------------------
def a_markdown(casos):
    out = ["# Evidencias de petición y respuesta · microservicios v1", "",
           f"Generado el {time.strftime('%Y-%m-%d %H:%M')} contra los servicios en ejecución. "
           f"{sum(c['estado'] == 'PASA' for c in casos)} de {len(casos)} casos pasan.", ""]
    servicio = None
    for c in casos:
        if c["servicio"] != servicio:
            servicio = c["servicio"]
            out += [f"## Servicio {servicio} · puerto {PUERTOS[servicio]}", ""]
        out += [f"### {c['id']} · {c['titulo']} · {c['estado']}", "", f"**Objetivo.** {c['objetivo']}", "",
                f"**Petición.** `{c['metodo']} {c['url']}`", ""]
        if c.get("encabezados"):
            out += ["```http"] + [f"{k}: {v}" for k, v in c["encabezados"].items()] + ["```", ""]
        if c.get("cuerpo"):
            out += ["```" + ("xml" if c["cuerpo"].lstrip().startswith("<") else "json"), c["cuerpo"], "```", ""]
        out += [f"**Respuesta.** HTTP {c.get('obtenido')} (esperado {c['esperado']}) · {c.get('ms', '—')} ms · "
                f"traza `{c.get('traza', '')}`", ""]
        if c.get("respuesta"):
            out += ["```" + ("xml" if c["respuesta"].lstrip().startswith("<") else "json"), c["respuesta"], "```", ""]
        if c.get("explicacion"):
            out += [f"**Explicación.** {c['explicacion']}", ""]
        for e in c.get("evidencia", []):
            out += [f"**Evidencia en {e['motor']}.** `{e['consulta']}`", "", "```json",
                    json.dumps(e["resultado"], ensure_ascii=False, indent=2, default=str), "```", ""]
        if c.get("nota"):
            out += [f"> {c['nota']}", ""]
    return "\n".join(out)


def a_tabla(casos):
    out = ["# Pruebas ejecutadas · microservicios v1", "",
           "| ID | Servicio | Objetivo | Entrada | Esperado | Obtenido | Estado |", "|---|---|---|---|---|---|---|"]
    for c in casos:
        ruta = c["url"].split("/api/v1/")[-1]
        out.append(f"| {c['id']} | {c['servicio']} | {c['objetivo']} | `{c['metodo']} /api/v1/{ruta}` | "
                   f"{c['esperado']} | {c.get('obtenido')} | {c['estado']} |")
    pasan = sum(c["estado"] == "PASA" for c in casos)
    out += ["", f"**Total:** {len(casos)} casos · {pasan} pasan · {len(casos) - pasan} fallan."]
    return "\n".join(out)


def a_html(casos):
    def bloque(titulo, texto, clase=""):
        return f'<div class="b {clase}"><div class="t">{titulo}</div><pre>{html.escape(texto)}</pre></div>' if texto else ""
    tarjetas = []
    for c in casos:
        enc = "\n".join(f"{k}: {v}" for k, v in (c.get("encabezados") or {}).items())
        encr = "\n".join(f"{k}: {v}" for k, v in (c.get("encabezados_respuesta") or {}).items())
        ev = "".join(bloque(f"Evidencia en {e['motor']} · {html.escape(e['consulta'])}",
                            json.dumps(e["resultado"], ensure_ascii=False, indent=2, default=str), "ev")
                     for e in c.get("evidencia", []))
        st = c.get("obtenido")
        tarjetas.append(f"""<section id="{c['id']}"><h3><span class="id">{c['id']}</span> {html.escape(c['titulo'])}
<span class="e {'ok' if c['estado'] == 'PASA' else 'mal'}">{c['estado']}</span></h3>
<p class="obj">{html.escape(c['objetivo'])}</p>
<div class="req"><span class="m {c['metodo']}">{c['metodo']}</span> <code>{html.escape(c['url'])}</code></div>
<div class="g">{bloque('Encabezados de la petición', enc)}{bloque('Cuerpo de la petición', c.get('cuerpo', ''))}</div>
<div class="st">HTTP <b class="{'ok' if st == c['esperado'] else 'mal'}">{st}</b> · esperado {c['esperado']} · {c.get('ms', '—')} ms · traza {c.get('traza', '')}</div>
<div class="g">{bloque('Encabezados de la respuesta', encr)}{bloque('Respuesta', c.get('respuesta', ''))}</div>
{f'<p class="ex">{html.escape(c["explicacion"])}</p>' if c.get('explicacion') else ''}{ev}</section>""")
    pasan = sum(c["estado"] == "PASA" for c in casos)
    indice = "".join(f'<a href="#{c["id"]}" class="{ "ok" if c["estado"] == "PASA" else "mal"}">{c["id"]}</a>' for c in casos)
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Evidencias · Microhubs</title>
<style>body{{font:14px system-ui,sans-serif;margin:24px;background:#f4f4f1;color:#1d2420}}h1{{margin:0}}
section{{background:#fff;border:1px solid #ddd;border-radius:10px;padding:16px;margin:16px 0}}
h3{{margin:0 0 6px}}.id{{font:600 12px monospace;background:#1d2420;color:#fff;padding:2px 6px;border-radius:4px}}
.e{{float:right;font-size:12px;padding:2px 8px;border-radius:10px}}.ok{{color:#11663d}}.mal{{color:#a3202f}}
.e.ok{{background:#dff3e7}}.e.mal{{background:#f8dde1}}.obj{{color:#555;margin:0 0 10px}}
.req{{font-size:15px;margin-bottom:8px}}.m{{font:700 12px monospace;color:#fff;padding:3px 8px;border-radius:4px;background:#2563eb}}
.m.POST{{background:#16a34a}}.m.PUT{{background:#b45309}}.m.PATCH{{background:#7c3aed}}.m.DELETE{{background:#dc2626}}
.g{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}.b .t{{font-size:12px;color:#555;margin:6px 0 2px}}
pre{{background:#111827;color:#e5e7eb;padding:10px;border-radius:6px;overflow:auto;max-height:420px;font-size:12px;margin:0}}
.ev pre{{background:#0f2a1d}}.st{{margin:10px 0 2px;font-size:13px}}.ex{{background:#f1f5f9;padding:8px;border-radius:6px}}
.idx a{{display:inline-block;margin:2px;font:12px monospace;text-decoration:none}}</style></head><body>
<h1>Evidencias de petición y respuesta · microservicios v1</h1>
<p>Plataforma de Microhubs · Codex Innovations · Equipo 04 · {time.strftime('%Y-%m-%d %H:%M')} · <b>{pasan} de {len(casos)} casos pasan</b></p>
<div class="idx">{indice}</div>{''.join(tarjetas)}</body></html>"""


def main():
    ap = argparse.ArgumentParser(description="Evidencias reales de los microservicios")
    ap.add_argument("--salida", default="/tmp/evidencias")
    ap.add_argument("--servicios", default=os.environ.get("MICROSERVICIOS_URL", "http://{servicio}:{puerto}"),
                    help="Plantilla de URL, p. ej. http://localhost:{puerto} desde fuera de Docker")
    a = ap.parse_args()
    ev = Evidencias(a.servicios)
    ejecutar(ev)
    salida = Path(a.salida)
    salida.mkdir(parents=True, exist_ok=True)
    (salida / "evidencias.json").write_text(json.dumps(ev.casos, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    (salida / "evidencias.md").write_text(a_markdown(ev.casos), encoding="utf-8")
    (salida / "pruebas.md").write_text(a_tabla(ev.casos), encoding="utf-8")
    (salida / "evidencias.html").write_text(a_html(ev.casos), encoding="utf-8")
    pasan = sum(c["estado"] == "PASA" for c in ev.casos)
    print(f"\n{pasan} de {len(ev.casos)} casos pasan. Archivos en {salida}: evidencias.html, evidencias.md, pruebas.md, evidencias.json")
    return 0 if pasan == len(ev.casos) else 1


if __name__ == "__main__":
    sys.exit(main())
