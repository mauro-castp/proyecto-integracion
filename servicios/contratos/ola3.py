"""
ola3.py — Contrato v1 de los servicios de la Ola 3: auditoria-monitoreo (5126), reportes (5123) y sincronizacion (5125).

El orden de los campos de cada tipo es el orden de las llaves que devuelve el servicio (xs:sequence). Los cuerpos de entrada llevan las
mismas restricciones que aplica comun/validar.py. Los ejemplos se escriben aquí una vez y de ellos salen el XML y el JSON oficiales.

Regenerar:  cd servicios && python contratos/generar.py ola3
"""
from generar import F
from ola1 import COMUN as _COMUN1                      # TRefNombre, TRefProductoClave, TRefTipoId (comun_ola1.xsd)
from ola2 import COMUN_OLA2_TIPOS as _COMUN2           # TSupuestoDoc, TSupuestosDoc (comun_ola2.xsd)

L = lambda tipo, item: [F("datos", [tipo], item=item), F("paginacion", "TPaginacion")]
DEP = ["postgres", "redis", "mongo", "bucket"]
TIPOS_EXTERNOS = {**_COMUN1, **_COMUN2, "TSaludDependencias": [F(d, "string", enum=["ok", "error", "no_aplica"]) for d in DEP]}

ACCIONES = ["alta", "modificacion", "baja_logica", "login_exitoso", "login_fallido", "logout", "bloqueo_cuenta", "desbloqueo",
            "acceso_denegado", "cambio_estado", "reasignacion", "reversion_administrativa", "movimiento_inventario", "cambio_configuracion", "descarga"]
ESTADOS = ["ok", "degradado", "caido"]
TIPOS_ALERTA = ["servicio_caido", "servicio_degradado", "dependencia_caida", "latencia_alta", "errores_altos"]

# --------------------------------------------------------------------
# auditoria-monitoreo
# --------------------------------------------------------------------
AUDITORIA_MONITOREO = {
    "TAudUsuario": [F("id", "long"), F("nombre", "string", nil=True)],
    "TAudCambio": [F("campo", "string"), F("anterior", "string", nil=True), F("nuevo", "string", nil=True)],
    "TAudEvento": [F("id", "long"), F("fecha", "dateTime"), F("usuario", "TAudUsuario", nil=True), F("correo_intento", "string", nil=True),
                   F("ip_origen", "string", nil=True), F("modulo", "string"), F("accion", "string", enum=ACCIONES),
                   F("entidad", "TRefTipoId", nil=True), F("exitoso", "bool"), F("detalle", "string", nil=True),
                   F("cambios", ["TAudCambio"], item="cambio")],
    "TAudEventoLista": L("TAudEvento", "evento"),
    "TAudAccesosTotales": [F(a, "long") for a in ["login_exitoso", "login_fallido", "logout", "bloqueo_cuenta", "desbloqueo", "acceso_denegado"]],
    "TAudCorreoFallo": [F("correo", "string"), F("intentos", "long"), F("ultimo_intento", "dateTime")],
    "TAudDenegado": [F("detalle", "string"), F("veces", "long")],
    "TAudAccesos": [F("desde", "date"), F("hasta", "date"), F("totales", "TAudAccesosTotales"),
                    F("correos_con_mas_fallos", ["TAudCorreoFallo"], item="correo"), F("denegados_frecuentes", ["TAudDenegado"], item="denegado")],
    "TAudTrazaEvento": [F("fecha", "dateTime"), F("origen", "string", enum=["auditoria", "estados", "inventario", "documentos"]),
                        F("accion", "string"), F("descripcion", "string"), F("usuario", "TAudUsuario", nil=True),
                        F("entidad", "TRefTipoId", nil=True), F("cambios", ["TAudCambio"], item="cambio")],
    "TAudObjeto": [F("tipo", "string", enum=["pedido", "entrega", "inventario"]), F("id", "string")],
    "TAudTrazabilidad": [F("objeto", "TAudObjeto"), F("total", "long"), F("eventos", ["TAudTrazaEvento"], item="evento")],

    "TMonResumen": [F("total", "long"), F("ok", "long"), F("degradados", "long"), F("caidos", "long"), F("sin_datos", "long"),
                    F("alertas_abiertas", "long"), F("monitor_activo", "bool"), F("intervalo_seg", "long"), F("ultima_ronda", "dateTime", nil=True)],
    "TMonServicioEstado": [F("servicio", "string"), F("puerto", "int"), F("estado", "string", enum=ESTADOS + ["sin_datos"]),
                           F("verificado_en", "dateTime", nil=True), F("antiguedad_seg", "long", nil=True), F("tiempo_ms", "num", nil=True),
                           F("version", "string", nil=True), F("dependencias", "TSaludDependencias", nil=True), F("error", "string", nil=True),
                           F("peticiones_hora", "long", nil=True), F("errores_5xx_hora", "long", nil=True),
                           F("disponibilidad_24h_pct", "num", nil=True), F("bajo_objetivo", "bool")],
    "TMonDependenciaCaida": [F("dependencia", "string", enum=DEP), F("afectados", ["string"], item="servicio")],
    "TMonEstado": [F("generado_en", "dateTime"), F("resumen", "TMonResumen"), F("servicios", ["TMonServicioEstado"], item="servicio"),
                   F("dependencias_caidas", ["TMonDependenciaCaida"], item="dependencia")],
    "TMonVerificacion": [F("verificado_en", "dateTime"), F("estado", "string", enum=ESTADOS), F("http_status", "int", nil=True),
                         F("tiempo_ms", "num"), F("version", "string", nil=True), F("dependencias", "TSaludDependencias", nil=True),
                         F("error", "string", nil=True)],
    "TMonHistorialLista": L("TMonVerificacion", "verificacion"),
    "TMonDisponibilidadServicio": [F("servicio", "string"), F("verificaciones", "long"), F("caidas", "long"),
                                   F("disponibilidad_pct", "num", nil=True), F("salud_plena_pct", "num", nil=True),
                                   F("tiempo_p50_ms", "num", nil=True), F("tiempo_p95_ms", "num", nil=True), F("tiempo_max_ms", "num", nil=True),
                                   F("bajo_objetivo", "bool")],
    "TMonDisponibilidad": [F("horas", "long"), F("objetivo_pct", "num"), F("servicios", ["TMonDisponibilidadServicio"], item="servicio")],
    "TMonMetricaServicio": [F("servicio", "string"), F("peticiones", "long"), F("errores_5xx", "long"), F("errores_4xx", "long"),
                            F("tasa_5xx_pct", "num", nil=True), F("duracion_p50_ms", "num", nil=True), F("duracion_p95_ms", "num", nil=True),
                            F("duracion_p99_ms", "num", nil=True)],
    "TMonMetricas": [F("minutos", "long"), F("peticiones_total", "long"), F("servicios", ["TMonMetricaServicio"], item="servicio")],
    "TMonReconocida": [F("por", "TAudUsuario"), F("en", "dateTime")],
    "TMonAlerta": [F("id", "long"), F("servicio", "string"), F("tipo", "string", enum=TIPOS_ALERTA),
                   F("severidad", "string", enum=["critica", "alta", "media"]), F("detalle", "string"), F("abierta_en", "dateTime"),
                   F("cerrada_en", "dateTime", nil=True), F("duracion_seg", "long"), F("reconocida", "TMonReconocida", nil=True)],
    "TMonAlertaLista": L("TMonAlerta", "alerta"),
    "TMonVerificacionNueva": [F("servicio", "string", opt=True, nil=True, max=30, minlen=1)],
    "TMonRondaServicio": [F("servicio", "string"), F("estado", "string", enum=ESTADOS), F("tiempo_ms", "num"), F("error", "string", nil=True)],
    "TMonRonda": [F("verificados", "long"), F("ok", "long"), F("degradados", "long"), F("caidos", "long"),
                  F("servicios", ["TMonRondaServicio"], item="servicio")],
}
AUDITORIA_MONITOREO_RAICES = {
    "bitacora": "TAudEventoLista", "accesos": "TAudAccesos", "trazabilidad": "TAudTrazabilidad", "monitoreo_estado": "TMonEstado",
    "monitoreo_historial": "TMonHistorialLista", "monitoreo_disponibilidad": "TMonDisponibilidad", "monitoreo_metricas": "TMonMetricas",
    "monitoreo_alertas": "TMonAlertaLista", "monitoreo_alerta": "TMonAlerta", "monitoreo_verificacion": "TMonRonda",
    "verificacion_nueva": "TMonVerificacionNueva", "supuestos_monitoreo": "TSupuestosDoc"}

# --------------------------------------------------------------------
# reportes
# --------------------------------------------------------------------
REPORTES = {
    "TRepFiltros": [F("desde", "date"), F("hasta", "date"), F("zona_id", "long", nil=True), F("microhub_id", "long", nil=True)],
    "TRepColumna": [F("clave", "string"), F("titulo", "string"), F("tipo", "string", enum=["texto", "entero", "dinero", "porcentaje", "fecha"])],
    "TRepFila": [F("celdas", ["string"], item="celda")],
    "TReporte": [F("reporte", "string"), F("familia", "string", enum=["operativo", "logistico", "comercial", "financiero"]), F("titulo", "string"),
                 F("generado_en", "dateTime"), F("filtros", "TRepFiltros"), F("columnas", ["TRepColumna"], item="columna"),
                 F("filas", ["TRepFila"], item="fila"), F("totales", "TRepFila", nil=True), F("total_filas", "long")],
    "TRepCatalogoItem": [F("clave", "string"), F("familia", "string", enum=["operativo", "logistico", "comercial", "financiero"]), F("titulo", "string"),
                         F("descripcion", "string"), F("filtros", ["string"], item="filtro")],
    "TRepCatalogo": [F("datos", ["TRepCatalogoItem"], item="reporte")],
    "TRepSerie": [F("nombre", "string"), F("datos", ["num"], item="dato")],
    "TRepGrafica": [F("reporte", "string"), F("titulo", "string"), F("tipo", "string", enum=["column", "line", "bar", "pie"]), F("unidad", "string"),
                    F("categorias", ["string"], item="categoria"), F("series", ["TRepSerie"], item="serie")],
    "TRepIndicador": [F("clave", "string"), F("titulo", "string"), F("valor", "num", nil=True), F("unidad", "string"), F("fuente", "string")],
    "TRepIndicadores": [F("desde", "date"), F("hasta", "date"), F("indicadores", ["TRepIndicador"], item="indicador"),
                        F("fuentes_no_disponibles", ["string"], item="servicio")],
    "TRepUsuario": [F("id", "long"), F("nombre", "string", nil=True)],
    "TRepExportacion": [F("id", "long"), F("reporte", "string"), F("formato", "string", enum=["csv", "xlsx", "pdf"]), F("filtros", "TRepFiltros"),
                        F("filas", "long"), F("bytes", "long"), F("sha256", "string"), F("creado_por", "TRepUsuario", nil=True), F("creado_en", "dateTime")],
    "TRepExportacionLista": L("TRepExportacion", "exportacion"),
}
REPORTES_RAICES = {"reporte": "TReporte", "reportes_catalogo": "TRepCatalogo", "grafica": "TRepGrafica", "indicadores": "TRepIndicadores",
                   "reportes_exportaciones": "TRepExportacionLista"}

# --------------------------------------------------------------------
# sincronizacion (el lote de entrada es solo JSON: sus `datos` son el cuerpo del servicio dueño de cada operación, que no cabe en un XSD)
# --------------------------------------------------------------------
SYNC_ESTADOS = ["aplicada", "conflicto", "rechazada", "pendiente"]
SINCRONIZACION = {
    "TSyncUsuario": [F("id", "long"), F("nombre", "string", nil=True)],
    "TSyncOperacionResultado": [F("operacion_uuid", "string"), F("tipo", "string"), F("estado", "string", enum=SYNC_ESTADOS), F("duplicada", "bool"),
                                F("http_status", "int", nil=True), F("codigo", "string", nil=True), F("mensaje", "string", nil=True), F("reintentar", "bool")],
    "TSyncLoteResultado": [F("id", "long"), F("lote_uuid", "string"), F("dispositivo", "string"), F("recibido_en", "dateTime"), F("total", "long"),
                           F("aplicadas", "long"), F("duplicadas", "long"), F("conflictos", "long"), F("rechazadas", "long"), F("pendientes", "long"),
                           F("operaciones", ["TSyncOperacionResultado"], item="operacion")],
    "TSyncLote": [F("id", "long"), F("lote_uuid", "string"), F("dispositivo", "string"), F("cliente", "string", enum=["android", "escritorio", "web"]),
                  F("usuario", "TSyncUsuario"), F("recibido_en", "dateTime"), F("total", "long"), F("aplicadas", "long"), F("duplicadas", "long"),
                  F("conflictos", "long"), F("rechazadas", "long"), F("pendientes", "long")],
    "TSyncLoteLista": L("TSyncLote", "lote"),
    "TSyncOperacion": [F("id", "long"), F("lote_uuid", "string"), F("dispositivo", "string"), F("operacion_uuid", "string"), F("tipo", "string"),
                       F("creada_en", "dateTime"), F("estado", "string", enum=SYNC_ESTADOS), F("http_status", "int", nil=True), F("codigo", "string", nil=True),
                       F("mensaje", "string", nil=True), F("intentos", "int"), F("procesada_en", "dateTime"), F("usuario", "TSyncUsuario")],
    "TSyncOperacionLista": L("TSyncOperacion", "operacion"),
    "TSyncLoteDetalle": [F("id", "long"), F("lote_uuid", "string"), F("dispositivo", "string"), F("cliente", "string", enum=["android", "escritorio", "web"]),
                         F("usuario", "TSyncUsuario"), F("recibido_en", "dateTime"), F("total", "long"), F("aplicadas", "long"), F("duplicadas", "long"),
                         F("conflictos", "long"), F("rechazadas", "long"), F("pendientes", "long"),
                         F("operaciones", ["TSyncOperacion"], item="operacion")],
    "TSyncEstado": [F("dispositivo", "string"), F("ultima_sincronizacion", "dateTime", nil=True), F("lotes", "long"), F("aplicadas", "long"),
                    F("conflictos", "long"), F("rechazadas", "long"), F("pendientes", "long")],
}
SINCRONIZACION_RAICES = {"sync_lote_resultado": "TSyncLoteResultado", "sync_lotes": "TSyncLoteLista", "sync_lote": "TSyncLoteDetalle",
                         "sync_operaciones": "TSyncOperacionLista", "sync_estado": "TSyncEstado", "supuestos_sincronizacion": "TSupuestosDoc"}

ARCHIVOS = {
    "sincronizacion": {"titulo": "servicio: sincronizacion", "incluye": ["comun", "comun_ola2"], "tipos": SINCRONIZACION, "raices": SINCRONIZACION_RAICES},
    "reportes": {"titulo": "servicio: reportes", "incluye": ["comun"], "tipos": REPORTES, "raices": REPORTES_RAICES},
    "auditoria_monitoreo": {"titulo": "servicio: auditoria-monitoreo", "incluye": ["comun", "comun_ola1", "comun_ola2"],
                            "tipos": AUDITORIA_MONITOREO, "raices": AUDITORIA_MONITOREO_RAICES},
}

# --------------------------------------------------------------------
# Ejemplos oficiales
# --------------------------------------------------------------------
HUB = "2026-11-25T10:30:00-06:00"
PAG = {"pagina": 1, "por_pagina": 20, "total": 1, "paginas": 1}
DEPS_OK = {"postgres": "ok", "redis": "ok", "mongo": "ok", "bucket": "no_aplica"}
CAMBIO = {"campo": "estado", "anterior": "confirmado", "nuevo": "en_preparacion"}
USUARIO = {"id": 3, "nombre": "Mariana Ortega"}
SUPUESTO = {"clave": "mon_latencia_ms", "valor": "1000", "unidad": "ms", "origen": "supuesto",
            "justificacion": "Un /salud sano responde en decenas de milisegundos; 1 s ya indica saturación de alguna dependencia.",
            "como_calibrar": "Tomar el p95 de tiempo_ms de monitoreo_verificacion en una semana normal y poner el umbral al doble."}
ALERTA = {"id": 12, "servicio": "documentos", "tipo": "dependencia_caida", "severidad": "alta",
          "detalle": "documentos no alcanza: bucket.", "abierta_en": HUB, "cerrada_en": None, "duracion_seg": 95,
          "reconocida": {"por": USUARIO, "en": HUB}}

SYNC_U = "4f1d7a2e-9b3c-4d5e-8f60-1a2b3c4d5e6f"
SYNC_LOTE = {"id": 8, "lote_uuid": "0b8e6f1c-2a4d-4c7e-9a31-5d6e7f809a1b", "dispositivo": "android-repartidor1", "cliente": "android", "usuario": USUARIO,
             "recibido_en": HUB, "total": 2, "aplicadas": 1, "duplicadas": 0, "conflictos": 1, "rechazadas": 0, "pendientes": 0}
SYNC_OP = {"id": 31, "lote_uuid": SYNC_LOTE["lote_uuid"], "dispositivo": "android-repartidor1", "operacion_uuid": SYNC_U, "tipo": "entrega_resultado",
           "creada_en": HUB, "estado": "conflicto", "http_status": 409, "codigo": "CONFLICTO", "mensaje": "La entrega ya se cerró con otro identificador.",
           "intentos": 1, "procesada_en": HUB, "usuario": USUARIO}
FILTROS = {"desde": "2026-10-26", "hasta": "2026-11-25", "zona_id": None, "microhub_id": None}

EJEMPLOS = {
    "SyncLoteNuevo": (None, {"lote_uuid": SYNC_LOTE["lote_uuid"], "dispositivo": "android-repartidor1", "cliente": "android", "operaciones": [
        {"operacion_uuid": "6a0f3b5c-1d2e-4f70-8a9b-0c1d2e3f4a5b", "tipo": "ubicaciones", "creada_en": HUB,
         "datos": {"entrega_id": 163, "puntos": [{"latitud": 25.7491, "longitud": -100.3611, "capturado_en": HUB}]}},
        {"operacion_uuid": SYNC_U, "tipo": "entrega_resultado", "creada_en": HUB,
         "datos": {"entrega_id": 163, "resultado": "entregado", "monto_cobrado": 130.5, "cambio_entregado": 0,
                   "ubicacion": {"latitud": 25.7491, "longitud": -100.3611}, "evidencia_ids": [], "capturado_en": HUB}}]}),
    "SyncLoteResultado": ("sync_lote_resultado", {
        "id": 8, "lote_uuid": SYNC_LOTE["lote_uuid"], "dispositivo": "android-repartidor1", "recibido_en": HUB, "total": 2, "aplicadas": 1, "duplicadas": 0,
        "conflictos": 1, "rechazadas": 0, "pendientes": 0, "operaciones": [
            {"operacion_uuid": "6a0f3b5c-1d2e-4f70-8a9b-0c1d2e3f4a5b", "tipo": "ubicaciones", "estado": "aplicada", "duplicada": False, "http_status": 201,
             "codigo": None, "mensaje": None, "reintentar": False},
            {"operacion_uuid": SYNC_U, "tipo": "entrega_resultado", "estado": "conflicto", "duplicada": False, "http_status": 409, "codigo": "CONFLICTO",
             "mensaje": "La entrega ya se cerró con otro identificador.", "reintentar": False}]}),
    "SyncLoteLista": ("sync_lotes", {"datos": [SYNC_LOTE], "paginacion": PAG}),
    "SyncLote": ("sync_lote", {**SYNC_LOTE, "operaciones": [SYNC_OP]}),
    "SyncOperacionLista": ("sync_operaciones", {"datos": [SYNC_OP], "paginacion": PAG}),
    "SyncEstado": ("sync_estado", {"dispositivo": "android-repartidor1", "ultima_sincronizacion": HUB, "lotes": 8, "aplicadas": 20, "conflictos": 1,
                                   "rechazadas": 0, "pendientes": 2}),
    "SupuestosSincronizacion": ("supuestos_sincronizacion", {"datos": [{**SUPUESTO, "clave": "sync_antiguedad_max_dias", "valor": "14", "unidad": "días"}]}),
    "Reporte": ("reporte", {
        "reporte": "pedidos_por_dia", "familia": "operativo", "titulo": "Pedidos por día", "generado_en": HUB, "filtros": FILTROS,
        "columnas": [{"clave": "fecha", "titulo": "Día", "tipo": "fecha"}, {"clave": "pedidos", "titulo": "Pedidos", "tipo": "entero"},
                     {"clave": "venta", "titulo": "Venta", "tipo": "dinero"}],
        "filas": [{"celdas": ["2026-11-24", "12", "1534.50"]}], "totales": {"celdas": ["Total", "12", "1534.50"]}, "total_filas": 1}),
    "ReportesCatalogo": ("reportes_catalogo", {"datos": [
        {"clave": "pedidos_por_dia", "familia": "operativo", "titulo": "Pedidos por día", "descripcion": "Pedidos, unidades y venta de cada día.",
         "filtros": ["desde", "hasta", "zona_id", "microhub_id"]}]}),
    "ReporteGrafica": ("grafica", {"reporte": "pedidos_por_dia", "titulo": "Pedidos por día", "tipo": "line", "unidad": "pedidos / MXN",
                                   "categorias": ["2026-11-24"], "series": [{"nombre": "Pedidos", "datos": [12.0]}, {"nombre": "Venta", "datos": [1534.5]}]}),
    "ReportesIndicadores": ("indicadores", {"desde": "2026-10-26", "hasta": "2026-11-25", "indicadores": [
        {"clave": "pedidos", "titulo": "Pedidos del periodo", "valor": 12, "unidad": "pedidos", "fuente": "pedidos"}], "fuentes_no_disponibles": ["inventario"]}),
    "ReportesExportacionLista": ("reportes_exportaciones", {"datos": [
        {"id": 4, "reporte": "pedidos_por_dia", "formato": "xlsx", "filtros": FILTROS, "filas": 1, "bytes": 5120,
         "sha256": "9f2c0ab4d5e7c1d8a3b6f0e2d4c8a1b7e5f3d9c2a0b8e6f4d2c0a8b6e4f2d0c8", "creado_por": {"id": 3, "nombre": "Mariana Ortega"}, "creado_en": HUB}],
        "paginacion": PAG}),
    "BitacoraLista": ("bitacora", {"datos": [
        {"id": 5021, "fecha": HUB, "usuario": USUARIO, "correo_intento": None, "ip_origen": "172.18.0.9", "modulo": "pedidos",
         "accion": "cambio_estado", "entidad": {"tipo": "pedido", "id": "163"}, "exitoso": True, "detalle": None, "cambios": [CAMBIO]}],
        "paginacion": PAG}),
    "Accesos": ("accesos", {"desde": "2026-11-18", "hasta": "2026-11-25",
                            "totales": {"login_exitoso": 42, "login_fallido": 3, "logout": 30, "bloqueo_cuenta": 0, "desbloqueo": 0, "acceso_denegado": 2},
                            "correos_con_mas_fallos": [{"correo": "alguien@ejemplo.mx", "intentos": 3, "ultimo_intento": HUB}],
                            "denegados_frecuentes": [{"detalle": "GET /api/v1/auditoria sin auditoria.ver", "veces": 2}]}),
    "Trazabilidad": ("trazabilidad", {"objeto": {"tipo": "pedido", "id": "163"}, "total": 2, "eventos": [
        {"fecha": HUB, "origen": "estados", "accion": "cambio_estado", "descripcion": "confirmado → en_preparacion", "usuario": USUARIO,
         "entidad": {"tipo": "pedido", "id": "163"}, "cambios": []},
        {"fecha": HUB, "origen": "auditoria", "accion": "cambio_estado", "descripcion": "estado: confirmado → en_preparacion", "usuario": USUARIO,
         "entidad": {"tipo": "pedido", "id": "163"}, "cambios": [CAMBIO]}]}),
    "MonitoreoEstado": ("monitoreo_estado", {
        "generado_en": HUB,
        "resumen": {"total": 24, "ok": 22, "degradados": 1, "caidos": 1, "sin_datos": 0, "alertas_abiertas": 2, "monitor_activo": True,
                    "intervalo_seg": 30, "ultima_ronda": HUB},
        "servicios": [{"servicio": "pedidos", "puerto": 5104, "estado": "ok", "verificado_en": HUB, "antiguedad_seg": 12, "tiempo_ms": 18.4,
                       "version": "1.0.0", "dependencias": DEPS_OK, "error": None, "peticiones_hora": 340, "errores_5xx_hora": 0,
                       "disponibilidad_24h_pct": 100.0, "bajo_objetivo": False}],
        "dependencias_caidas": [{"dependencia": "bucket", "afectados": ["documentos"]}]}),
    "MonitoreoHistorial": ("monitoreo_historial", {"datos": [
        {"verificado_en": HUB, "estado": "ok", "http_status": 200, "tiempo_ms": 18.4, "version": "1.0.0", "dependencias": DEPS_OK, "error": None}],
        "paginacion": PAG}),
    "MonitoreoDisponibilidad": ("monitoreo_disponibilidad", {"horas": 24, "objetivo_pct": 99.0, "servicios": [
        {"servicio": "pedidos", "verificaciones": 2880, "caidas": 0, "disponibilidad_pct": 100.0, "salud_plena_pct": 100.0,
         "tiempo_p50_ms": 14.2, "tiempo_p95_ms": 31.0, "tiempo_max_ms": 120.5, "bajo_objetivo": False}]}),
    "MonitoreoMetricas": ("monitoreo_metricas", {"minutos": 60, "peticiones_total": 340, "servicios": [
        {"servicio": "pedidos", "peticiones": 340, "errores_5xx": 0, "errores_4xx": 4, "tasa_5xx_pct": 0.0,
         "duracion_p50_ms": 21, "duracion_p95_ms": 80, "duracion_p99_ms": 140}]}),
    "MonitoreoAlertaLista": ("monitoreo_alertas", {"datos": [ALERTA], "paginacion": PAG}),
    "MonitoreoAlerta": ("monitoreo_alerta", ALERTA),
    "MonitoreoVerificacion": ("monitoreo_verificacion", {"verificados": 1, "ok": 1, "degradados": 0, "caidos": 0, "servicios": [
        {"servicio": "pedidos", "estado": "ok", "tiempo_ms": 18.4, "error": None}]}),
    "MonitoreoVerificacionNueva": ("verificacion_nueva", {"servicio": "pedidos"}),
    "SupuestosMonitoreo": ("supuestos_monitoreo", {"datos": [SUPUESTO]}),
}
