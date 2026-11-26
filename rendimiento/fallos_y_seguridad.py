#!/usr/bin/env python3
"""
fallos_y_seguridad.py — Demuestra, con la plataforma en marcha, cómo se comporta ante fallas reales y que sus controles de seguridad
funcionan. Provoca cada falla con Docker, observa por HTTP, comprueba que los datos no cambiaron y restaura todo.

  python3 rendimiento/fallos_y_seguridad.py evidencias/ola4                      en local
  NUBE=1 python3 rendimiento/fallos_y_seguridad.py evidencias/nube               en la VM (usa .env y el compose de la nube)

Escribe <carpeta>/fallos.md, <carpeta>/seguridad.md y sus .json. Solo usa la biblioteca estándar. Detiene contenedores: no correrlo mientras
alguien usa el sistema.
"""
import base64
import datetime as dt
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
NUBE = os.environ.get("NUBE") == "1"
CLAVE = os.environ.get("MICROHUBS_CLAVE", "Codex#2026")
COMPOSE = ["docker", "compose", "-f", "docker-compose.integrado.yml"]
if NUBE:
    COMPOSE = ["docker", "compose", "--env-file", ".env", "-f", "docker-compose.integrado.yml", "-f", "deploy/gcp/docker-compose.gcp.yml"]
PUERTOS = {"auth": 5101, "usuarios": 5102, "productos": 5103, "pedidos": 5104, "entregas": 5105, "documentos": 5107, "zonas": 5108,
           "inventario": 5111, "reportes": 5123, "sincronizacion": 5125, "auditoria-monitoreo": 5126, "surtido": 5122}
JPEG = base64.b64encode(bytes([0xFF, 0xD8, 0xFF, 0xE0, 0, 16, 74, 70, 73, 70, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0]) + bytes(range(256))).decode()


def pedir(servicio, metodo, ruta, cuerpo=None, token=None, crudo=None, tipo="application/json", timeout=20):
    url = f"http://127.0.0.1:{PUERTOS[servicio]}/api/v1/{ruta}"
    enc = {"Accept": "application/json"}
    datos = crudo.encode() if isinstance(crudo, str) else crudo
    if cuerpo is not None:
        datos = json.dumps(cuerpo).encode()
    if datos is not None:
        enc["Content-Type"] = tipo
    if token:
        enc["Authorization"] = f"Bearer {token}"
    t = time.perf_counter()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=datos, headers=enc, method=metodo), timeout=timeout) as r:
            status, texto, cab = r.status, r.read().decode("utf-8", "replace"), dict(r.headers)
    except urllib.error.HTTPError as e:
        status, texto, cab = e.code, e.read().decode("utf-8", "replace"), dict(e.headers)
    except Exception as e:                                       # sin conexión o sin respuesta a tiempo
        status, texto, cab = None, f"{type(e).__name__}: {e}", {}
    ms = int((time.perf_counter() - t) * 1000)
    try:
        j = json.loads(texto)
    except ValueError:
        j = None
    return {"servicio": servicio, "metodo": metodo, "ruta": ruta, "status": status, "ms": ms, "texto": texto, "json": j, "cab": cab}


def compose(*args, entorno=None):
    return subprocess.run(COMPOSE + list(args), cwd=RAIZ, capture_output=True, text=True, env={**os.environ, **(entorno or {})}, timeout=240)


def sql(consulta):
    r = subprocess.run(["docker", "exec", "microhubs-integrado-postgres-1", "psql", "-U", "microhubs", "-d", "microhubs_p1", "-At", "-c", consulta],
                       capture_output=True, text=True, timeout=60)
    return (r.stdout or r.stderr).strip()


def documentos_en_mongo():
    r = subprocess.run(["docker", "exec", "microhubs-integrado-mongo-1", "mongosh", "--quiet", "microhubs_eventos", "--eval", "db.documentos.countDocuments()"],
                       capture_output=True, text=True, timeout=60)
    return r.stdout.strip()


def conteos():
    return sql("SELECT 'pedidos=' || (SELECT count(*) FROM microhubs.pedido) || ' entregas=' || (SELECT count(*) FROM microhubs.entrega) || "
               "' existencia_total=' || (SELECT sum(existencia) FROM microhubs.inventario)")


def esperar_sano(servicio, segundos=90):
    t = time.time()
    while time.time() - t < segundos:
        if pedir(servicio, "GET", "salud", timeout=5)["status"] == 200:
            return round(time.time() - t, 1)
        time.sleep(2)
    return None


def entrar(correo):
    r = pedir("auth", "POST", "auth/login", {"correo": correo, "clave": CLAVE, "dispositivo": "fallos"})
    return (r["json"] or {}).get("token_acceso")


class Informe:
    def __init__(self, titulo, intro):
        self.titulo, self.intro, self.secciones = titulo, intro, []

    def seccion(self, nombre, que):
        self.secciones.append({"nombre": nombre, "que": que, "pasos": []})
        print(f"== {nombre}", flush=True)

    def paso(self, momento, descripcion, ok, r=None, dato=None):
        p = {"momento": momento, "descripcion": descripcion, "ok": bool(ok)}
        if r is not None:
            p.update(peticion=f"{r['metodo']} {r['servicio']} /{r['ruta']}", status=r["status"], ms=r["ms"], respuesta=r["texto"][:260])
        if dato is not None:
            p["dato"] = dato
        self.secciones[-1]["pasos"].append(p)
        print(f"  {'PASA ' if ok else 'FALLA'} [{momento}] {descripcion}" + (f" → {r['status']} en {r['ms']} ms" if r else ""), flush=True)

    def guardar(self, carpeta, nombre):
        pasos = [p for s in self.secciones for p in s["pasos"]]
        bien = sum(p["ok"] for p in pasos)
        out = [f"# {self.titulo}", "", self.intro, "", f"Ejecutado el {dt.datetime.now().strftime('%Y-%m-%d %H:%M')} "
               f"en {'la VM de Google Cloud' if NUBE else 'el equipo local con Docker'}: **{bien} de {len(pasos)} comprobaciones pasan**.", ""]
        for s in self.secciones:
            out += [f"## {s['nombre']}", "", s["que"], "", "| Momento | Comprobación | Resultado | Petición | HTTP | ms |", "|---|---|---|---|---|---|"]
            for p in s["pasos"]:
                out.append(f"| {p['momento']} | {p['descripcion']} | {'✔' if p['ok'] else '✘'} | {('`' + p['peticion'] + '`') if p.get('peticion') else '—'} "
                           f"| {p.get('status', '—')} | {p.get('ms', '—')} |")
            detalles = [p for p in s["pasos"] if p.get("respuesta") or p.get("dato")]
            if detalles:
                out += ["", "<details><summary>Respuestas y datos observados</summary>", ""]
                for p in detalles:
                    out += [f"**{p['descripcion']}**", "", "```", str(p.get("dato") or p.get("respuesta")), "```", ""]
                out.append("</details>")
            out.append("")
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / f"{nombre}.md").write_text("\n".join(out) + "\n", encoding="utf-8")
        (carpeta / f"{nombre}.json").write_text(json.dumps(self.secciones, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{self.titulo}: {bien} de {len(pasos)}")
        return bien == len(pasos)


def codigo(r):
    return ((r["json"] or {}).get("error") or {}).get("codigo")


def verificar_monitor(token, servicio):
    return pedir("auditoria-monitoreo", "POST", "monitoreo/verificaciones", {"servicio": servicio}, token)


# ====================================================================
def fallos():
    inf = Informe("Pruebas de tolerancia a fallos", "Cada falla se provoca de verdad con Docker. En cada una se comprueba que el sistema la detecta, la informa con un "
                  "error claro, no corrompe datos y se recupera sin intervención manual sobre los datos.")
    adm = entrar("admin@codex.mx")
    antes = conteos()

    inf.seccion("1. Un microservicio detenido (inventario)", "Los que dependen de él deben avisar; los demás siguen.")
    try:
        compose("stop", "inventario")
        r = pedir("inventario", "GET", "salud", timeout=5); inf.paso("durante", "El servicio no responde", r["status"] is None, r)
        r = pedir("reportes", "GET", "reportes/indicadores", token=adm)
        inf.paso("durante", "Los indicadores se entregan y nombran al servicio caído", r["status"] == 200 and "inventario" in (r["json"] or {}).get("fuentes_no_disponibles", []), r)
        r = pedir("reportes", "GET", "reportes/inventario_alertas", token=adm); inf.paso("durante", "El reporte que depende de él responde 503, sin inventar datos", r["status"] == 503, r)
        r = pedir("productos", "GET", "productos?por_pagina=1", token=adm); inf.paso("durante", "El resto de la plataforma sigue atendiendo", r["status"] == 200, r)
        r = verificar_monitor(adm, "inventario"); inf.paso("durante", "El monitoreo lo marca caído y abre una alerta", (r["json"] or {}).get("caidos") == 1, r)
    finally:
        compose("start", "inventario")
    s = esperar_sano("inventario"); inf.paso("después", f"Vuelve a estar sano en {s} s", s is not None)
    verificar_monitor(adm, "inventario")
    r = pedir("auditoria-monitoreo", "GET", "monitoreo/alertas?estado=abiertas&servicio=inventario", token=adm)
    inf.paso("después", "La alerta se cierra sola", (r["json"] or {}).get("paginacion", {}).get("total") == 0, r)

    inf.seccion("2. Redis caído", "Redis guarda las sesiones. Sin él no se puede saber si un token fue revocado: el sistema cierra el paso (503) en lugar de confiar.")
    try:
        compose("stop", "redis")
        r = pedir("pedidos", "GET", "pedidos?por_pagina=1", token=adm); inf.paso("durante", "No deja pasar sin validar la sesión (503)", r["status"] == 503, r)
        r = pedir("pedidos", "GET", "salud", timeout=10); inf.paso("durante", "/salud informa redis con error", r["status"] == 503 and (r["json"] or {}).get("dependencias", {}).get("redis") == "error", r)
        r = pedir("auth", "POST", "auth/login", {"correo": "admin@codex.mx", "clave": CLAVE, "dispositivo": "f"}); inf.paso("durante", "Tampoco se emiten sesiones nuevas", r["status"] in (500, 503), r)
    finally:
        compose("start", "redis")
    s = esperar_sano("pedidos"); inf.paso("después", f"Los servicios vuelven a estar sanos en {s} s", s is not None)
    r = pedir("pedidos", "GET", "pedidos?por_pagina=1", token=adm)
    inf.paso("después", "Los tokens anteriores ya no sirven (Redis no conserva sesiones): nadie revocado puede volver a entrar", r["status"] == 401, r)
    adm = entrar("admin@codex.mx")
    r = pedir("pedidos", "GET", "pedidos?por_pagina=1", token=adm); inf.paso("después", "Con un inicio de sesión nuevo todo funciona", r["status"] == 200, r)

    inf.seccion("3. MongoDB caído", "MongoDB guarda archivos (sus datos), GPS y registros. Lo transaccional no depende de él.")
    n_docs = documentos_en_mongo()
    try:
        compose("stop", "mongo")
        r = pedir("pedidos", "GET", "pedidos?por_pagina=1", token=adm); inf.paso("durante", "Pedidos sigue funcionando (los registros se omiten)", r["status"] == 200, r)
        r = pedir("documentos", "POST", "documentos", {"nombre": "fallo.jpg", "tipo_mime": "image/jpeg", "contenido_base64": JPEG, "referencia": {"tipo": "usuario", "id": "1"}}, adm, timeout=30)
        inf.paso("durante", "Subir un archivo responde con error claro", r["status"] in (500, 503), r)
        r = pedir("documentos", "GET", "salud", timeout=15); inf.paso("durante", "/salud de documentos informa mongo con error", r["status"] == 503 and (r["json"] or {}).get("dependencias", {}).get("mongo") == "error", r)
    finally:
        compose("start", "mongo")
    s = esperar_sano("documentos"); inf.paso("después", f"Documentos se recupera en {s} s", s is not None)
    n2 = documentos_en_mongo(); inf.paso("después", "No quedó ningún registro a medias", n2 == n_docs, dato=f"documentos antes={n_docs} después={n2}")

    inf.seccion("4. PostgreSQL caído", "La base transaccional. Los errores deben ser claros y sin detalles internos.")
    try:
        compose("stop", "postgres")
        r = pedir("pedidos", "GET", "pedidos?por_pagina=1", token=adm, timeout=30)
        inf.paso("durante", "Responde 503 con el formato de error del contrato", r["status"] == 503 and codigo(r) == "SERVICIO_NO_DISPONIBLE", r)
        inf.paso("durante", "El error no muestra consultas, contraseñas ni trazas del programa", not any(x in r["texto"] for x in ("Traceback", "psycopg", "password", "SELECT")), dato=r["texto"][:200])
        r = pedir("pedidos", "GET", "salud", timeout=20); inf.paso("durante", "/salud informa postgres con error", r["status"] == 503, r)
    finally:
        compose("start", "postgres")
    s = esperar_sano("pedidos"); inf.paso("después", f"Se reconecta solo en {s} s, sin reiniciar los servicios", s is not None)
    r = pedir("pedidos", "GET", "pedidos?por_pagina=1", token=adm); inf.paso("después", "Vuelve a responder", r["status"] == 200, r)

    inf.seccion("5. Almacén de archivos fuera de servicio", "El bucket (o la carpeta) no acepta archivos. No debe quedar un registro sin archivo.")
    n_docs = documentos_en_mongo()
    cuerpo = {"nombre": "fallo-almacen.jpg", "tipo_mime": "image/jpeg", "contenido_base64": JPEG, "referencia": {"tipo": "usuario", "id": "1"}}
    try:
        if NUBE:
            compose("up", "-d", "documentos", entorno={"GCS_BUCKET": "microhubs-bucket-que-no-existe-0000"})
        else:
            subprocess.run(["docker", "exec", "-u", "root", "microhubs-integrado-documentos-1", "chmod", "000", "/app/almacen"], capture_output=True)
        time.sleep(6); adm = entrar("admin@codex.mx")
        esperar = pedir("documentos", "GET", "salud", timeout=20)
        inf.paso("durante", "/salud informa el almacén con error", esperar["status"] == 503 and (esperar["json"] or {}).get("dependencias", {}).get("bucket") == "error", esperar)
        r = pedir("documentos", "POST", "documentos", cuerpo, adm, timeout=40); inf.paso("durante", "Subir responde 503", r["status"] == 503, r)
        n2 = documentos_en_mongo(); inf.paso("durante", "No se guardó un registro sin archivo", n2 == n_docs, dato=f"documentos antes={n_docs} después={n2}")
    finally:
        if NUBE:
            compose("up", "-d", "documentos")
        else:
            subprocess.run(["docker", "exec", "-u", "root", "microhubs-integrado-documentos-1", "chmod", "755", "/app/almacen"], capture_output=True)
    s = esperar_sano("documentos"); inf.paso("después", f"Documentos vuelve a estar sano en {s} s", s is not None)
    r = pedir("documentos", "POST", "documentos", cuerpo, adm, timeout=40); inf.paso("después", "Se puede subir de nuevo", r["status"] == 201, r)
    if r["status"] == 201:
        pedir("documentos", "DELETE", f"documentos/{r['json']['id']}", token=adm)

    inf.seccion("6. Un servicio que no contesta (tiempo de espera)", "El contenedor queda congelado: acepta la conexión pero no responde.")
    try:
        subprocess.run(["docker", "pause", "microhubs-integrado-inventario-1"], capture_output=True)
        r = pedir("reportes", "GET", "reportes/inventario_alertas", token=adm, timeout=40)
        inf.paso("durante", "Quien lo llama no se queda colgado: corta a los pocos segundos con 503", r["status"] == 503 and r["ms"] < 15000, r)
        r = verificar_monitor(adm, "inventario"); inf.paso("durante", "El monitoreo lo da por caído tras su tiempo de espera", (r["json"] or {}).get("caidos") == 1, r)
    finally:
        subprocess.run(["docker", "unpause", "microhubs-integrado-inventario-1"], capture_output=True)
    s = esperar_sano("inventario"); inf.paso("después", f"Al reanudarse vuelve en {s} s", s is not None)
    verificar_monitor(adm, "inventario")

    inf.seccion("7. Integridad de los datos", "Pedidos, entregas e inventario antes y después de todas las fallas.")
    despues = conteos(); inf.paso("final", "Ninguna falla creó, borró ni alteró datos", despues == antes, dato=f"antes:   {antes}\ndespués: {despues}")
    return inf


# ====================================================================
def seguridad():
    inf = Informe("Evidencia de seguridad", "Cada control se ejercita contra los servicios en marcha.")
    adm, op = entrar("admin@codex.mx"), entrar("operador.mh01@codex.mx")

    inf.seccion("Autenticación", "JWT firmado y sesión activa en Redis.")
    r = pedir("pedidos", "GET", "pedidos"); inf.paso("—", "Sin token no se entra (401 y WWW-Authenticate)", r["status"] == 401 and "WWW-Authenticate" in r["cab"], r)
    r = pedir("pedidos", "GET", "pedidos", token=adm[:-4] + "AAAA"); inf.paso("—", "Un token alterado se rechaza", r["status"] == 401, r)
    t = entrar("planeador@codex.mx")
    pedir("auth", "POST", "auth/salir", {}, t)
    r = pedir("zonas", "GET", "zonas", token=t); inf.paso("—", "Un token revocado al salir ya no sirve en ningún servicio", r["status"] == 401, r)
    correo = f"nadie.{uuid.uuid4().hex[:8]}@codex.mx"
    ultimo = None
    for _ in range(6):
        ultimo = pedir("auth", "POST", "auth/login", {"correo": correo, "clave": "incorrecta", "dispositivo": "s"})
    inf.paso("—", "Cinco intentos fallidos bloquean la cuenta 15 minutos (423)", ultimo["status"] == 423, ultimo)

    inf.seccion("Autorización", "Permisos por perfil, comprobados por cada servicio.")
    r = pedir("auditoria-monitoreo", "GET", "auditoria", token=op); inf.paso("—", "El operador no puede ver la bitácora (403)", r["status"] == 403, r)
    r = pedir("usuarios", "POST", "usuarios", {"nombre": "x", "apellidos": "y", "correo": "x@y.mx", "clave": "1234567890a", "rol": "administrador"}, op)
    inf.paso("—", "El operador no puede crear un administrador (403)", r["status"] == 403, r)
    n = sql("SELECT count(*) FROM microhubs.auditoria WHERE accion = 'acceso_denegado' AND fecha > now() - interval '2 minutes'")
    inf.paso("—", "Los intentos denegados quedan en la bitácora", n.isdigit() and int(n) >= 2, dato=f"accesos denegados registrados en los últimos 2 minutos: {n}")
    r = sql("UPDATE microhubs.auditoria SET detalle = 'alterado' WHERE id = (SELECT max(id) FROM microhubs.auditoria)")
    inf.paso("—", "La bitácora no se puede modificar, ni siquiera desde la base (RN31)", "RN31" in r, dato=r[:240])
    h = sql("SELECT left(hash_contrasena, 4) FROM microhubs.usuario WHERE correo = 'admin@codex.mx'")
    inf.paso("—", "Las contraseñas se guardan con bcrypt, nunca en claro", h == "$2b$", dato=f"inicio del hash: {h}…")

    inf.seccion("Entradas maliciosas", "Validación de JSON y XML, inyección y archivos.")
    xxe = '<?xml version="1.0"?><!DOCTYPE x [<!ENTITY e SYSTEM "file:///etc/passwd">]><login xmlns="urn:microhubs:v1"><correo>&e;</correo><clave>x</clave></login>'
    r = pedir("auth", "POST", "auth/login", crudo=xxe, tipo="application/xml"); inf.paso("—", "XML con entidad externa (XXE) se rechaza", r["status"] == 400 and "root:" not in r["texto"], r)
    r = pedir("auth", "POST", "auth/login", crudo="{mal", tipo="application/json"); inf.paso("—", "JSON mal formado: 400 sin detalles internos", r["status"] == 400 and "Traceback" not in r["texto"], r)
    n0 = sql("SELECT count(*) FROM microhubs.producto")
    r = pedir("productos", "GET", "productos?q=%27%3B%20DROP%20TABLE%20producto%3B--", token=adm)
    inf.paso("—", "Inyección SQL en la búsqueda: se trata como texto", r["status"] == 200 and sql("SELECT count(*) FROM microhubs.producto") == n0, r)
    r = pedir("documentos", "POST", "documentos", {"nombre": "falso.jpg", "tipo_mime": "image/jpeg", "contenido_base64": base64.b64encode(b"MZ ejecutable").decode(),
                                                  "referencia": {"tipo": "usuario", "id": "1"}}, adm)
    inf.paso("—", "Un archivo que dice ser imagen pero no lo es se rechaza (se revisa su firma)", r["status"] == 422, r)
    # 5 MB y un poco más: pasa el límite del archivo pero cabe en el cuerpo, así que el servicio puede responder con el motivo
    grande = base64.b64encode(b"\xff\xd8\xff" + b"0" * (5 * 1024 * 1024 + 100_000)).decode()
    r = pedir("documentos", "POST", "documentos", {"nombre": "grande.jpg", "tipo_mime": "image/jpeg", "contenido_base64": grande, "referencia": {"tipo": "usuario", "id": "1"}}, adm, timeout=60)
    inf.paso("—", "Un archivo de más de 5 MB se rechaza con el motivo", r["status"] in (413, 422), r)
    r = pedir("zonas", "GET", "zonas/no-existe", token=adm); inf.paso("—", "Los errores usan el formato del contrato, con traza y sin rutas internas", r["status"] == 404 and "traza_id" in r["texto"], r)

    inf.seccion("Archivos privados y cabeceras", "Enlaces firmados con caducidad y cabeceras de protección.")
    r = pedir("documentos", "POST", "documentos", {"nombre": "privado.jpg", "tipo_mime": "image/jpeg", "contenido_base64": JPEG, "referencia": {"tipo": "usuario", "id": "1"}}, adm)
    if r["status"] == 201:
        did = r["json"]["id"]
        e = pedir("documentos", "GET", f"documentos/{did}/enlace", token=adm)
        url = (e["json"] or {}).get("url_firmada", "")
        inf.paso("—", "El archivo se entrega con un enlace firmado que caduca", e["status"] == 200 and (e["json"] or {}).get("segundos", 0) > 0, dato=url.split("?")[0] + "?…(firma omitida)")
        o = pedir("documentos", "GET", f"documentos/{did}/enlace", token=op); inf.paso("—", "Otra persona no obtiene el enlace de un documento privado", o["status"] in (403, 404), o)
        try:
            urllib.request.urlopen(url[:-3] + "abc", timeout=15); alterado = 200
        except urllib.error.HTTPError as x:
            alterado = x.code
        except Exception:
            alterado = None
        inf.paso("—", "Un enlace alterado no sirve", alterado in (400, 403), dato=f"HTTP {alterado}")
        pedir("documentos", "DELETE", f"documentos/{did}", token=adm)
    r = pedir("zonas", "GET", "zonas", token=adm)
    inf.paso("—", "Respuestas con X-Content-Type-Options: nosniff y Cache-Control: no-store", r["cab"].get("X-Content-Type-Options") == "nosniff" and "no-store" in r["cab"].get("Cache-Control", ""), r)

    inf.seccion("Límite de consumo", "240 solicitudes por minuto por IP y servicio.")
    ultimo = None
    for _ in range(300):
        ultimo = pedir("zonas", "GET", "zonas?por_pagina=1", token=adm)
        if ultimo["status"] == 429:
            break
    inf.paso("—", "Al pasar el límite responde 429 con Retry-After", ultimo["status"] == 429 and "Retry-After" in ultimo["cab"], ultimo)

    if NUBE:
        inf.seccion("Infraestructura en la nube", "Secretos y puertos de la VM.")
        env = RAIZ / ".env"
        inf.paso("—", "El archivo de secretos solo lo lee su dueño (600)", env.exists() and oct(env.stat().st_mode)[-3:] == "600")
        txt = env.read_text() if env.exists() else ""
        inf.paso("—", "No quedan los secretos por defecto del repositorio", "cambiar-en-produccion" not in txt and "microhubs_dev" not in txt)
        puertos = subprocess.run(["ss", "-ltnH"], capture_output=True, text=True).stdout
        expuestos = sorted({l.split()[3] for l in puertos.splitlines() if l.split() and l.split()[3].startswith(("0.0.0.0:", "[::]:", "*:"))})
        inf.paso("—", "Ningún microservicio ni base de datos escucha hacia fuera", not any(p.rsplit(":", 1)[1] in {"5000", "5101", "5104", "5107", "5126", "5432", "6379", "27017"} for p in expuestos), dato=", ".join(expuestos))
    return inf


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    carpeta = RAIZ / (sys.argv[1] if len(sys.argv) > 1 else "evidencias/ola4")
    esperar_sano("auth")
    a = seguridad().guardar(carpeta, "seguridad")
    if "--solo-seguridad" in sys.argv:
        return 0 if a else 1
    time.sleep(61)                       # el límite de consumo que se agotó a propósito se libera
    b = fallos().guardar(carpeta, "fallos")
    return 0 if a and b else 1


if __name__ == "__main__":
    sys.exit(main())
