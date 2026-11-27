"""
Panel de monitoreo del portal. El portal (monolito) NO llama al servicio de monitoreo: lee directamente, solo para consulta,
las tablas donde ese servicio guarda cada verificación y alerta (monitoreo_verificacion y monitoreo_alerta, en PostgreSQL).
"""
from flask import Blueprint, render_template

from nucleo import consultar, requiere

monitoreo_bp = Blueprint("monitoreo", __name__)


@monitoreo_bp.route("/monitoreo")
@requiere("monitoreo.ver")
def panel():
    servicios = consultar(
        "SELECT DISTINCT ON (servicio) servicio, estado, verificado_en, tiempo_ms::float AS tiempo_ms, version, error, "
        "extract(epoch FROM now() - verificado_en)::int AS antiguedad_seg FROM monitoreo_verificacion "
        "ORDER BY servicio, verificado_en DESC")
    disp = {f["servicio"]: f for f in consultar(
        "SELECT servicio, round(100.0 * avg((estado = 'ok')::int), 2) AS pct, round(avg(tiempo_ms)::numeric, 1) AS prom_ms, "
        "round((percentile_cont(0.95) WITHIN GROUP (ORDER BY tiempo_ms))::numeric, 1) AS p95_ms, count(*) AS verificaciones "
        "FROM monitoreo_verificacion WHERE verificado_en > now() - interval '24 hours' GROUP BY servicio")}
    abiertas = consultar("SELECT servicio, tipo, severidad, detalle, abierta_en, reconocida_en FROM monitoreo_alerta "
                         "WHERE cerrada_en IS NULL ORDER BY abierta_en DESC LIMIT 50")
    cerradas = consultar("SELECT servicio, tipo, abierta_en, cerrada_en, (extract(epoch FROM cerrada_en - abierta_en) / 60)::int AS minutos "
                         "FROM monitoreo_alerta WHERE cerrada_en IS NOT NULL ORDER BY cerrada_en DESC LIMIT 15")
    resumen = {"total": len(servicios), "ok": sum(1 for s in servicios if s["estado"] == "ok"),
               "problemas": sum(1 for s in servicios if s["estado"] != "ok"), "alertas": len(abiertas),
               "ultima": max((s["verificado_en"] for s in servicios), default=None)}
    return render_template("web_monitoreo.html", servicios=servicios, disp=disp, abiertas=abiertas, cerradas=cerradas, r=resumen)
