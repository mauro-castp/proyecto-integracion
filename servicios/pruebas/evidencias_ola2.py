"""
evidencias_ola2.py — Casos de petición y respuesta de la Ola 2: demanda, cobertura, capacidad, costos, punto de equilibrio,
surtido, rutas y simulación, más lo que ganaron pedidos, entregas e inventario. Los llama evidencias.py con las mismas
herramientas (ev.caso, pg, rd, mg), así que salen en el mismo informe, con lo que quedó en PostgreSQL después de cada petición.

Dejan la base como la encontraron en lo que se puede deshacer (población de una zona, personal de un microhub, conceptos de
costo, restricciones de surtido, historia de demanda, planes y simulaciones de prueba). Los pedidos listos para despachar que
la prueba de rutas necesita se reutilizan si ya existen.
"""
import datetime as dt
import time
import uuid


def ejecutar_ola2(ev, h):
    pg, bd, xml = h.pg, h.bd, h.xml
    from pruebas.preparar_listos import dejar_listos
    print("12. Ola 2: demanda, cobertura, capacidad, costos, punto de equilibrio, surtido, rutas y simulación (5115 a 5122)")
    t_adm, t_plan, t_aud = ev.entrar("admin@codex.mx"), ev.entrar("planeador@codex.mx"), ev.entrar("auditor@codex.mx")
    t_op1, t_op2, t_cli = ev.entrar("operador.mh01@codex.mx"), ev.entrar("operador.mh02@codex.mx"), ev.entrar("juan.chapa1@correo.mx")

    def uno(sql, args=()):
        return bd.consultar(sql, args, una=True)

    def ejecutar(sql, args=()):
        with bd.conexion() as con, con.cursor() as cur:
            cur.execute(sql, args)

    def silencioso(servicio, metodo, ruta, cuerpo=None, token=None):
        return ev.http(servicio, metodo, ruta, cuerpo, token=token)[0]

    hub1 = uno("SELECT id FROM microhub WHERE clave = 'MH-01'")["id"]
    hub2 = uno("SELECT id FROM microhub WHERE clave = 'MH-02'")["id"]
    hub3 = uno("SELECT id FROM microhub WHERE clave = 'MH-03'")["id"]
    hoy = dt.date.today()

    # ================= ALIMENTADORES: lo que ganaron pedidos, entregas e inventario =================
    print("  Pedidos, entregas e inventario (lo que alimenta al análisis)")
    ev.caso("ALI-01", "pedidos", "Resumen de pedidos por día y zona", "Lo consume el servicio de demanda: pedidos, unidades, venta y clientes por día y zona.",
            "GET", "pedidos/resumen?por_pagina=5", token=t_adm,
            verificar=lambda r: r.json["datos"] and {"fecha", "zona_id", "pedidos", "unidades", "venta", "clientes", "no_atendidos"} <= set(r.json["datos"][0]),
            explicacion="Agrupa por el día de Monterrey (no el de UTC), sin pedidos cancelados. La demanda no atendida solo se suma en consultas de toda la red.",
            evidencia=lambda r: [pg("SELECT (creado_en AT TIME ZONE 'America/Monterrey')::date AS dia, zona_id, count(*) AS pedidos FROM pedido "
                                    "WHERE estado <> 'cancelado' GROUP BY 1, 2 ORDER BY 1, 2 LIMIT 5")])
    ev.caso("ALI-02", "pedidos", "Resumen con agrupación inválida", "Un valor desconocido de «agrupar» se rechaza.", "GET", "pedidos/resumen?agrupar=otra",
            token=t_adm, esperado=400, verificar=lambda r: r.json["error"]["codigo"] == "FILTRO_INVALIDO")
    ev.caso("ALI-03", "pedidos", "Ventas por producto", "Lo consume surtido: unidades y venta de cada producto, sin cancelados.", "GET", "pedidos/ventas?por_pagina=5",
            token=t_adm, verificar=lambda r: r.json["datos"] and r.json["datos"][0]["unidades"] >= r.json["datos"][-1]["unidades"])
    ev.caso("ALI-04", "pedidos", "Pedidos listos sin microhub", "El microhub es obligatorio.", "GET", "pedidos/listos", token=t_adm, esperado=400,
            verificar=lambda r: r.json["error"]["codigo"] == "FILTRO_INVALIDO")
    ev.caso("ALI-05", "pedidos", "Pedidos listos de un microhub", "Con las coordenadas de entrega: lo que rutas agrupa y ordena.", "GET",
            f"pedidos/listos?microhub_id={hub1}", token=t_op1, verificar=lambda r: r.json["paginacion"]["total"] >= 0,
            evidencia=lambda r: [pg("SELECT count(*) AS listos FROM pedido WHERE microhub_id = %s AND estado = 'en_preparacion' AND listo_en IS NOT NULL", (hub1,))])
    ev.caso("ALI-06", "entregas", "Repartidores activos", "Con las entregas que tienen abiertas hoy; lo consume rutas.", "GET", "entregas/repartidores",
            token=t_op1, verificar=lambda r: r.json["datos"] and "entregas_abiertas" in r.json["datos"][0])
    ev.caso("ALI-07", "inventario", "Quiebres de inventario", "Veces que una salida dejó el producto en cero y si hoy está agotado; lo consume surtido.", "GET",
            f"inventario/quiebres?microhub_id={hub1}&por_pagina=5", token=t_adm, verificar=lambda r: r.json["paginacion"]["total"] >= 0)
    ev.caso("ALI-08", "inventario", "Quiebres con ventana inválida", "dias debe estar entre 1 y 365.", "GET", "inventario/quiebres?dias=0", token=t_adm, esperado=400)

    # ================= DEMANDA =================
    print("  Demanda (5115)")
    ev.caso("DEM-01", "demanda", "Observaciones de demanda", "Pedidos por día, zona y categoría, con la fuente de cada dato.", "GET",
            "demanda/observaciones?nivel=total&por_pagina=5", token=t_adm,
            verificar=lambda r: r.json["datos"] and r.json["datos"][0]["fuente"] in ("pedidos", "sintetica", "manual"),
            explicacion="La historia de demostración es sintética y lo dice en cada renglón (fuente = sintetica): no se hace pasar por ventas reales.",
            evidencia=lambda r: [pg("SELECT fuente, count(*) AS observaciones, min(fecha) AS desde, max(fecha) AS hasta FROM demanda_observacion GROUP BY fuente")])
    ev.caso("DEM-02", "demanda", "Observaciones (XML)", "Respuesta XML que cumple demanda.xsd.", "GET", "demanda/observaciones?por_pagina=3", token=t_adm,
            formato="xml", verificar=lambda r: "<observaciones_demanda" in r.texto)
    ev.caso("DEM-03", "demanda", "Fuente desconocida", "Un filtro desconocido se rechaza.", "GET", "demanda/observaciones?fuente=inventada", token=t_adm, esperado=400)
    ev.caso("DEM-04", "demanda", "El operador consulta la demanda", "Sin demanda.ver.", "GET", "demanda/observaciones", token=t_op1, esperado=403)
    ev.caso("DEM-05", "demanda", "Resumen por zona", "Pedidos, ticket promedio, pedidos por cliente y demanda no atendida.", "GET", "demanda/resumen", token=t_adm,
            verificar=lambda r: r.json["total"]["pedidos"] == sum(z["pedidos"] for z in r.json["zonas"]),
            evidencia=lambda r: [pg("SELECT zona_id, sum(pedidos) AS pedidos, round(sum(venta) / NULLIF(sum(pedidos), 0), 2) AS ticket FROM demanda_observacion "
                                    "WHERE categoria_id IS NULL GROUP BY zona_id ORDER BY zona_id")])
    ev.caso("DEM-06", "demanda", "Patrones de la semana", "Índice de cada día de la semana y venta por categoría.", "GET", "demanda/patrones", token=t_adm,
            verificar=lambda r: len(r.json["semanal"]) == 7 and r.json["suficiente"],
            explicacion="Índice = promedio de ese día ÷ promedio general. Con menos de dos semanas completas vale 1 y el resultado lo dice (suficiente = false).")
    ev.caso("DEM-07", "demanda", "Proyección con banda de error", "14 días con mínimo y máximo; la banda sale del error del propio ajuste.", "GET",
            "demanda/proyeccion", token=t_adm,
            verificar=lambda r: len(r.json["serie"]) == 14 and all(d["minimo"] <= d["pedidos"] <= d["maximo"] for d in r.json["serie"]),
            explicacion="Tendencia por mínimos cuadrados sobre la serie sin estacionalidad, por el índice del día. Banda = proyección ± 1.28 desviaciones.")
    ev.caso("DEM-08", "demanda", "Proyección con promedio móvil", "El otro método: nivel de los últimos 7 días, sin tendencia.", "GET",
            "demanda/proyeccion?metodo=promedio_movil&horizonte=7", token=t_adm, verificar=lambda r: r.json["pendiente_pedidos_dia"] == 0.0)
    ev.caso("DEM-09", "demanda", "Método inventado", "Solo existen dos métodos.", "GET", "demanda/proyeccion?metodo=magico", token=t_adm, esperado=400)
    ev.caso("DEM-10", "demanda", "Comparación contra lo observado", "Se ocultan los últimos 7 días, se proyectan y se miden el error y el sesgo.", "GET",
            "demanda/comparacion", token=t_adm, verificar=lambda r: r.json["dias_prueba"] == 7 and r.json["mape_pct"] is not None,
            explicacion="MAPE = promedio de |proyectado − observado| ÷ observado. «dentro_banda_pct» dice cuántos días reales cayeron dentro de la banda.")
    ev.caso("DEM-11", "demanda", "Demanda potencial", "Hogares × penetración × pedidos por hogar, contra lo observado.", "GET", "demanda/potencial", token=t_adm,
            verificar=lambda r: len(r.json["escenarios"]) == 5,
            explicacion="Penetración 12 % y 2.5 pedidos por hogar al mes son supuestos documentados (GET /demanda/supuestos): no son datos medidos.")
    ev.caso("DEM-12", "demanda", "Potencial con otra penetración", "El cálculo no cambia la configuración: solo la consulta.", "GET", "demanda/potencial?penetracion=0.2",
            token=t_adm, verificar=lambda r: r.json["penetracion"] == 0.2)
    ev.caso("DEM-13", "demanda", "Sincronizar sin permiso", "Traer la demanda real exige demanda.editar.", "POST", "demanda/sincronizacion",
            cuerpo={"desde": (hoy - dt.timedelta(days=2)).isoformat(), "hasta": hoy.isoformat()}, token=t_aud, esperado=403)
    desde, hasta = hoy - dt.timedelta(days=2), hoy
    respaldo = bd.consultar("SELECT * FROM demanda_observacion WHERE fecha BETWEEN %s AND %s", (desde, hasta))
    ev.caso("DEM-14", "demanda", "Sincronizar con pedidos reales", "Lo sintético del rango se reemplaza por lo real.", "POST", "demanda/sincronizacion",
            cuerpo={"desde": desde.isoformat(), "hasta": hasta.isoformat()}, token=t_plan, esperado=201,
            verificar=lambda r: r.json["filas_escritas"] >= 0,
            explicacion="Lee pedidos/resumen y guarda las observaciones como propias (fuente = pedidos). Es idempotente: repetirlo deja lo mismo.",
            evidencia=lambda r: [pg("SELECT fuente, count(*) AS observaciones FROM demanda_observacion WHERE fecha BETWEEN %s AND %s GROUP BY fuente", (desde, hasta))])
    ejecutar("DELETE FROM demanda_observacion WHERE fecha BETWEEN %s AND %s", (desde, hasta))
    for f in respaldo:
        ejecutar("INSERT INTO demanda_observacion (fecha, zona_id, categoria_id, pedidos, unidades, venta, clientes, no_atendidos, fuente) "
                 "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                 (f["fecha"], f["zona_id"], f["categoria_id"], f["pedidos"], f["unidades"], f["venta"], f["clientes"], f["no_atendidos"], f["fuente"]))
    ev.caso("DEM-15", "demanda", "Sincronizar con fechas inválidas", "desde no puede ser posterior a hasta.", "POST", "demanda/sincronizacion",
            cuerpo={"desde": "2026-10-10", "hasta": "2026-10-01"}, token=t_plan, esperado=422)
    ev.caso("DEM-16", "demanda", "Sincronizar (XML)", "El cuerpo XML se valida contra demanda.xsd antes de procesarse.", "POST", "demanda/sincronizacion",
            cuerpo=xml("sincronizacion_nueva", {"desde": hoy.isoformat(), "hasta": hoy.isoformat()}), token=t_plan, formato="xml", esperado=201,
            verificar=lambda r: "<sincronizacion" in r.texto)
    ejecutar("DELETE FROM demanda_observacion WHERE fecha = %s", (hoy,))
    for f in [x for x in respaldo if x["fecha"] == hoy]:
        ejecutar("INSERT INTO demanda_observacion (fecha, zona_id, categoria_id, pedidos, unidades, venta, clientes, no_atendidos, fuente) "
                 "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                 (f["fecha"], f["zona_id"], f["categoria_id"], f["pedidos"], f["unidades"], f["venta"], f["clientes"], f["no_atendidos"], f["fuente"]))
    ev.caso("DEM-17", "demanda", "Supuestos de la demanda", "Valor, origen (medido, supuesto o normativo), justificación y cómo calibrarlo.", "GET",
            "demanda/supuestos", token=t_adm, verificar=lambda r: all(s["como_calibrar"] and s["origen"] for s in r.json["datos"]),
            evidencia=lambda r: [pg("SELECT clave, origen, left(justificacion, 80) AS justificacion FROM supuesto_documentado WHERE servicio = 'demanda' ORDER BY clave")])

    # ================= COBERTURA =================
    print("  Cobertura (5116)")
    ev.caso("COB-01", "cobertura", "Cobertura por zona", "Qué microhubs cubren cada zona, a cuántos minutos y si hay traslape.", "GET", "cobertura/zonas", token=t_adm,
            verificar=lambda r: r.json["datos"] and all(z["estado"] in ("cubierta", "sin_cobertura") for z in r.json["datos"]),
            explicacion="La regla de cobertura es el radio en línea recta (igual que fn_cubre en PostgreSQL); la distancia por calle (× 1.3) solo estima el tiempo.",
            evidencia=lambda r: [pg("SELECT m.clave, m.radio_km, z.clave AS zona, round(fn_distancia_km(m.latitud, m.longitud, z.latitud, z.longitud)::numeric, 2) AS km "
                                    "FROM microhub m CROSS JOIN zona z WHERE m.estatus = 'activo' ORDER BY z.clave, km LIMIT 8")])
    ev.caso("COB-02", "cobertura", "Resumen de la red", "Porcentaje de zonas y hogares cubiertos, tiempo promedio y zonas traslapadas.", "GET", "cobertura/resumen",
            token=t_adm, verificar=lambda r: 0 <= r.json["pct_hogares"] <= 100)
    ev.caso("COB-03", "cobertura", "Resumen (XML)", "Respuesta XML que cumple cobertura.xsd.", "GET", "cobertura/resumen", token=t_adm, formato="xml",
            verificar=lambda r: "<cobertura_resumen" in r.texto)
    m1 = uno("SELECT latitud::float AS lat, longitud::float AS lng FROM microhub WHERE id = %s", (hub1,))
    ev.caso("COB-04", "cobertura", "Un punto junto a un microhub", "Qué microhubs lo cubren y a qué distancia.", "GET",
            f"cobertura/punto?latitud={m1['lat']}&longitud={m1['lng']}", token=t_adm,
            verificar=lambda r: r.json["cubierto"] and r.json["opciones"][0]["distancia_km"] == 0.0)
    ev.caso("COB-05", "cobertura", "Un punto fuera de la red", "Nadie lo cubre; se dice cuál es la zona más cercana.", "GET",
            "cobertura/punto?latitud=26.9&longitud=-101.4", token=t_adm, verificar=lambda r: not r.json["cubierto"] and r.json["zona_mas_cercana"])
    ev.caso("COB-06", "cobertura", "Coordenadas inválidas", "La latitud debe estar entre 20 y 33.", "GET", "cobertura/punto?latitud=95&longitud=10", token=t_adm, esperado=400)
    r = ev.caso("COB-07", "cobertura", "Ubicaciones candidatas con ranking", "Cada candidata de planeación frente a la red actual.", "GET", "cobertura/candidatos",
                token=t_adm, verificar=lambda r: [c["ranking"] for c in r.json["datos"]] == list(range(1, len(r.json["datos"]) + 1)),
                explicacion="Primero la que suma más hogares nuevos y, a igualdad, la que acerca el servicio a más hogares ya cubiertos. Las candidatas "
                            "salen del servicio de planeación (cobertura no lee su tabla).")
    cid = r.json["datos"][0]["candidato"]["id"] if r is not None and r.status == 200 and r.json["datos"] else None
    if cid:
        ev.caso("COB-08", "cobertura", "Evaluar una candidata", "Zonas nuevas, hogares nuevos, traslape y costo de la última milla.", "POST", "cobertura/evaluaciones",
                cuerpo={"candidato_id": cid}, token=t_adm, verificar=lambda r: r.json["id"] is None and r.json["candidato"]["id"] == cid)
        ev.caso("COB-09", "cobertura", "Guardar la evaluación sin permiso", "Guardar exige planeacion.editar.", "POST", "cobertura/evaluaciones",
                cuerpo={"candidato_id": cid, "guardar": True}, token=t_aud, esperado=403)
        guardada = ev.caso("COB-10", "cobertura", "Guardar la evaluación", "Queda en cobertura_evaluacion con su resultado completo.", "POST", "cobertura/evaluaciones",
                           cuerpo={"candidato_id": cid, "guardar": True, "nombre": "Evidencia Ola 2"}, token=t_plan, esperado=201,
                           verificar=lambda r: r.json["id"] is not None,
                           evidencia=lambda r: [pg("SELECT id, nombre, parametros, creado_por FROM cobertura_evaluacion WHERE nombre = 'Evidencia Ola 2'")])
        if guardada is not None and guardada.status == 201:
            ev.caso("COB-17", "cobertura", "Evaluaciones guardadas", "Lista de lo que el planeador ha evaluado.", "GET", "cobertura/evaluaciones?por_pagina=5", token=t_adm,
                    verificar=lambda r: guardada.json["id"] in [e["id"] for e in r.json["datos"]])
            ev.caso("COB-18", "cobertura", "Abrir una evaluación guardada", "Con el resultado completo con que se guardó.", "GET", f"cobertura/evaluaciones/{guardada.json['id']}", token=t_adm,
                    verificar=lambda r: r.json["nombre"] == "Evidencia Ola 2")
        ejecutar("DELETE FROM cobertura_evaluacion WHERE nombre = 'Evidencia Ola 2'")
    ev.caso("COB-11", "cobertura", "Evaluar una coordenada sobre un microhub", "Todo se traslapa: se avisa de canibalización.", "POST", "cobertura/evaluaciones",
            cuerpo={"latitud": m1["lat"], "longitud": m1["lng"], "radio_km": 2}, token=t_adm,
            verificar=lambda r: r.json["canibaliza"] and r.json["solapamiento_pct"] == 100.0 and r.json["hogares_nuevos"] == 0)
    ev.caso("COB-12", "cobertura", "Evaluar sin coordenadas", "Hace falta un candidato o una coordenada.", "POST", "cobertura/evaluaciones",
            cuerpo={"radio_km": 2}, token=t_adm, esperado=422)
    ev.caso("COB-13", "cobertura", "Escenarios de radio y de rodeo", "Cuánto cubre la red con otros radios y otro factor de calle.", "GET",
            "cobertura/escenarios?radios=0.5,1,1.5,2&rodeos=1.2,1.5", token=t_adm, verificar=lambda r: len(r.json["filas"]) == 8,
            explicacion="El rodeo (1.3 por omisión) es un supuesto: la distancia real por calle es mayor que la recta.")
    z0 = uno("SELECT zona_id, poblacion FROM cobertura_zona_dato ORDER BY zona_id LIMIT 1")
    fuente_orig = uno("SELECT fuente FROM cobertura_zona_dato WHERE zona_id = %s", (z0["zona_id"],))["fuente"]
    ev.caso("COB-14", "cobertura", "Corregir la población con su fuente", "La población de cada zona se corrige con el dato de INEGI; hay que decir de dónde sale.", "PUT",
            f"cobertura/zonas/{z0['zona_id']}/poblacion", cuerpo={"poblacion": z0["poblacion"] + 100, "fuente": "INEGI, Censo 2020, AGEB de prueba"}, token=t_plan,
            verificar=lambda r: r.json["hogares"] == round((z0["poblacion"] + 100) / 3.6),
            evidencia=lambda r: [pg("SELECT zona_id, poblacion, fuente FROM cobertura_zona_dato WHERE zona_id = %s", (z0["zona_id"],)),
                                 pg("SELECT accion, entidad, valores_anteriores, valores_nuevos FROM auditoria WHERE entidad = 'cobertura_zona_dato' ORDER BY id DESC LIMIT 1")])
    ejecutar("UPDATE cobertura_zona_dato SET poblacion = %s, fuente = %s WHERE zona_id = %s", (z0["poblacion"], fuente_orig, z0["zona_id"]))
    ev.caso("COB-15", "cobertura", "Corregir la población sin permiso", "Es del planeador.", "PUT", f"cobertura/zonas/{z0['zona_id']}/poblacion",
            cuerpo={"poblacion": 1, "fuente": "Sin permiso"}, token=t_op1, esperado=403)
    ev.caso("COB-16", "cobertura", "Supuestos de la cobertura", "Rodeo, velocidad, tiempo de servicio, promesa de entrega y tamaño del hogar.", "GET", "cobertura/supuestos",
            token=t_adm, verificar=lambda r: {"factor_rodeo_distancia", "tamano_hogar"} <= {s["clave"] for s in r.json["datos"]})

    # ================= CAPACIDAD =================
    print("  Capacidad (5117)")
    ev.caso("CAP-01", "capacidad", "Personal de cada microhub", "Operadores, repartidores y tope de espacio.", "GET", "capacidad/recursos", token=t_adm,
            verificar=lambda r: r.json["paginacion"]["total"] >= 3,
            evidencia=lambda r: [pg("SELECT microhub_id, operadores, repartidores, capacidad_fisica FROM capacidad_recurso ORDER BY microhub_id")])
    ev.caso("CAP-02", "capacidad", "El operador pide otro microhub", "Solo ve los recursos del suyo.", "GET", f"capacidad/recursos/{hub2}", token=t_op1, esperado=403)
    ev.caso("CAP-03", "capacidad", "Capacidad con una carga dada", "Capacidad por etapa, utilización, cuello de botella y personal requerido.", "GET",
            f"capacidad/microhubs/{hub1}?carga_dia=60", token=t_adm,
            verificar=lambda r: r.json["carga_dia"] == 60 and r.json["nivel"] in ("estable", "atencion", "riesgo") and len(r.json["etapas"]) == 4,
            explicacion="Cada operador hace picking, empaque y despacho uno tras otro: su ritmo combinado es 1 ÷ (1/10 + 1/20 + 1/30). El reparto depende de "
                        "repartidores, distancia y paradas por viaje. La capacidad es la menor de las dos, limitada por el espacio.")
    ev.caso("CAP-13", "capacidad", "Capacidad de todos los microhubs", "Una fila por microhub con su utilización y su nivel; el operador solo ve el suyo.", "GET",
            "capacidad/microhubs?carga_dia=40&por_pagina=100", token=t_adm, verificar=lambda r: len(r.json["datos"]) >= 3)
    ev.caso("CAP-04", "capacidad", "Un microhub saturado", "Con 95 % de la capacidad el nivel es de riesgo (umbral 85 %).", "GET",
            f"capacidad/microhubs/{hub1}?carga_dia=140", token=t_adm, verificar=lambda r: r.json["nivel"] == "riesgo")
    ev.caso("CAP-05", "capacidad", "Horas fuera de rango", "horas va de 1 a 24.", "GET", f"capacidad/microhubs/{hub1}?horas=99", token=t_adm, esperado=400)
    ev.caso("CAP-06", "capacidad", "Capacidad (XML)", "Respuesta XML que cumple capacidad.xsd.", "GET", f"capacidad/microhubs/{hub1}?carga_dia=60", token=t_adm,
            formato="xml", verificar=lambda r: "<capacidad_microhub" in r.texto)
    ev.caso("CAP-07", "capacidad", "Simular más personal", "Qué pasa con 120 pedidos al día y 6 operadores y 6 repartidores.", "POST", "capacidad/simulaciones",
            cuerpo={"microhub_id": hub1, "pedidos_dia": 120, "operadores": 6, "repartidores": 6, "capacidad_fisica": 1000}, token=t_adm,
            verificar=lambda r: r.json["diferencia_capacidad_dia"] > 0)
    ev.caso("CAP-08", "capacidad", "Curva de carga", "Utilización a distintas cargas y el punto donde se pasa del umbral.", "GET", f"capacidad/cargas?microhub_id={hub1}",
            token=t_adm, verificar=lambda r: r.json["carga_estable"] < r.json["carga_en_riesgo"])
    orig = uno("SELECT operadores, repartidores, capacidad_fisica FROM capacidad_recurso WHERE microhub_id = %s", (hub1,))
    ev.caso("CAP-09", "capacidad", "Cambiar el personal", "El planeador corrige operadores y repartidores del microhub.", "PUT", f"capacidad/recursos/{hub1}",
            cuerpo={"operadores": orig["operadores"] + 1, "repartidores": orig["repartidores"], "capacidad_fisica": orig["capacidad_fisica"]}, token=t_plan,
            verificar=lambda r: r.json["operadores"] == orig["operadores"] + 1,
            evidencia=lambda r: [pg("SELECT operadores, repartidores, capacidad_fisica FROM capacidad_recurso WHERE microhub_id = %s", (hub1,)),
                                 pg("SELECT accion, valores_anteriores, valores_nuevos FROM auditoria WHERE entidad = 'capacidad_recurso' ORDER BY id DESC LIMIT 1")])
    ejecutar("UPDATE capacidad_recurso SET operadores = %s, repartidores = %s, capacidad_fisica = %s WHERE microhub_id = %s",
             (orig["operadores"], orig["repartidores"], orig["capacidad_fisica"], hub1))
    ev.caso("CAP-10", "capacidad", "Cambiar el personal sin permiso", "El operador no tiene capacidad.editar.", "PUT", f"capacidad/recursos/{hub1}",
            cuerpo={"operadores": 9, "repartidores": 9}, token=t_op1, esperado=403)
    ev.caso("CAP-11", "capacidad", "Personal inválido", "Al menos un operador.", "PUT", f"capacidad/recursos/{hub1}", cuerpo={"operadores": 0, "repartidores": 3},
            token=t_plan, esperado=422)
    ev.caso("CAP-12", "capacidad", "Supuestos de la capacidad", "Productividad por etapa, umbrales y horas del turno.", "GET", "capacidad/supuestos", token=t_adm,
            verificar=lambda r: {"picking_pedidos_hora", "umbral_utilizacion_riesgo"} <= {s["clave"] for s in r.json["datos"]})

    # ================= COSTOS =================
    print("  Costos (5119)")
    ev.caso("COS-01", "costos", "Conceptos de un microhub", "Los globales (pago al repartidor, empaque, comisión) y los propios (renta, nómina…).", "GET",
            f"costos/conceptos?microhub_id={hub1}&por_pagina=100", token=t_adm,
            verificar=lambda r: {c["ambito"] for c in r.json["datos"]} == {"global", "microhub"},
            evidencia=lambda r: [pg("SELECT ambito, tipo, categoria, count(*) AS conceptos, sum(monto) AS monto FROM costo_concepto WHERE estatus = 'activo' "
                                    "AND (ambito = 'global' OR (ambito = 'microhub' AND ambito_id = %s)) GROUP BY ambito, tipo, categoria ORDER BY 1, 2, 3", (hub1,))])
    ev.caso("COS-02", "costos", "Resumen de costos", "Fijos del mes por categoría y variables por unidad.", "GET", f"costos/resumen?microhub_id={hub1}", token=t_adm,
            verificar=lambda r: abs(r.json["fijos_mes"] - sum(c["monto"] for c in r.json["por_categoria"])) < 0.05)
    ev.caso("COS-03", "costos", "Costo por pedido y por entrega", "Costo fijo ÷ pedidos del mes + variable + comisión + entrega.", "GET",
            f"costos/unitarios?microhub_id={hub1}&pedidos_mes=1000&ticket=150", token=t_adm,
            verificar=lambda r: abs(r.json["costo_fijo_pedido"] - r.json["fijos_mes"] / 1000) < 0.02 and "ticket" in r.json["entrada"]["valores_modificados"],
            explicacion="Costo de entrega = pago por entrega + 2 × distancia × costo por km ÷ paradas por viaje. Los valores que la petición cambia aparecen en "
                        "«valores_modificados».")
    ev.caso("COS-04", "costos", "Rentabilidad", "Margen de contribución, utilidad del mes y margen operativo.", "GET", f"costos/rentabilidad?microhub_id={hub1}&pedidos_mes=1500",
            token=t_adm, verificar=lambda r: abs(r.json["utilidad_mes"] - (r.json["margen_contribucion_mes"] - r.json["costos_fijos_mes"])) < 0.05)
    ev.caso("COS-05", "costos", "Sensibilidad de costos", "Cada palanca sube y baja 10 y 20 %; se dice cuál mueve más la utilidad.", "GET",
            f"costos/sensibilidad?microhub_id={hub1}&pedidos_mes=1500", token=t_adm, verificar=lambda r: r.json["palanca_mas_sensible"])
    ev.caso("COS-06", "costos", "Costos (XML)", "Respuesta XML que cumple costos.xsd.", "GET", f"costos/unitarios?microhub_id={hub1}", token=t_adm, formato="xml",
            verificar=lambda r: "<costos_unitarios" in r.texto)
    ev.caso("COS-07", "costos", "El operador consulta costos", "Sin costos.ver.", "GET", "costos/conceptos", token=t_op1, esperado=403)
    nuevo = {"ambito": "microhub", "ambito_id": hub1, "nombre": "Evidencia de vigilancia", "categoria": "servicios", "tipo": "fijo", "unidad": "mes", "monto": 1500.0,
             "justificacion": "Concepto creado por la evidencia de la Ola 2"}
    ev.caso("COS-08", "costos", "Alta de un concepto sin permiso", "Un auditor consulta, no edita.", "POST", "costos/conceptos", cuerpo=nuevo, token=t_aud, esperado=403)
    r = ev.caso("COS-09", "costos", "Alta de un concepto", "Costo fijo de un microhub con su justificación.", "POST", "costos/conceptos", cuerpo=nuevo, token=t_plan,
                esperado=201, verificar=lambda r: r.json["estatus"] == "activo",
                evidencia=lambda r: [pg("SELECT id, ambito, ambito_id, nombre, tipo, unidad, monto, fuente, creado_por FROM costo_concepto WHERE nombre = 'Evidencia de vigilancia'"),
                                     pg("SELECT accion, entidad, modulo FROM auditoria WHERE entidad = 'costo_concepto' ORDER BY id DESC LIMIT 1")])
    if r is not None and r.status == 201:
        cc = r.json["id"]
        ev.caso("COS-10", "costos", "Cambiar el monto", "Cualquier subconjunto de campos; el ámbito no cambia.", "PUT", f"costos/conceptos/{cc}",
                cuerpo={"monto": 1800.0, "justificacion": "Se ajustó el monto en la evidencia"}, token=t_plan, verificar=lambda r: r.json["monto"] == 1800.0)
        ev.caso("COS-16", "costos", "Cambiar con PATCH", "PATCH es alias de PUT: lo usa la app Android cuando la JVM no admite PUT con cuerpo parcial.", "PATCH", f"costos/conceptos/{cc}",
                cuerpo={"monto": 1900.0, "justificacion": "Segundo ajuste del monto en la evidencia"}, token=t_plan, verificar=lambda r: r.json["monto"] == 1900.0)
        ev.caso("COS-11", "costos", "Dar de baja un concepto", "Baja lógica: el renglón se conserva para la historia.", "DELETE", f"costos/conceptos/{cc}", token=t_plan, esperado=204,
                evidencia=lambda r: [pg("SELECT id, estatus FROM costo_concepto WHERE id = %s", (cc,))])
        ejecutar("DELETE FROM costo_concepto WHERE id = %s", (cc,))
    ev.caso("COS-12", "costos", "Fijo con unidad variable", "Un costo fijo se da por mes.", "POST", "costos/conceptos",
            cuerpo={**nuevo, "nombre": "Evidencia inválida", "unidad": "pedido"}, token=t_plan, esperado=422)
    ev.caso("COS-13", "costos", "Microhub inexistente", "El ámbito debe existir.", "POST", "costos/conceptos", cuerpo={**nuevo, "ambito_id": 99999, "nombre": "Evidencia inválida"},
            token=t_plan, esperado=422, verificar=lambda r: r.json["error"]["detalles"][0]["campo"] == "ambito_id")
    cand_id = cid or 1
    ev.caso("COS-14", "costos", "Costos de una ubicación candidata", "Sin conceptos propios toma renta, nómina y servicios de la ubicación (planeación).", "GET",
            f"costos/resumen?candidato_id={cand_id}", token=t_adm, verificar=lambda r: r.json["ambito"] == "candidato" and r.json["fijos_mes"] > 0)
    ev.caso("COS-15", "costos", "Supuestos de los costos", "Volumen y ticket de referencia, paradas por viaje y margen por omisión; los montos de cada costo son conceptos con su propia justificación.", "GET",
            "costos/supuestos", token=t_adm, verificar=lambda r: {"cos_pedidos_mes_ref", "paradas_por_viaje"} <= {s["clave"] for s in r.json["datos"]})

    # ================= PUNTO DE EQUILIBRIO =================
    print("  Punto de equilibrio (5120)")
    escenario_a = {"pedidos_dia": 45, "ticket": 135, "margen_bruto": 0.28, "costos_fijos": 60000, "costo_variable_pedido": 32.6}
    ev.caso("EQU-01", "punto-equilibrio", "El escenario A de la retroalimentación", "45 pedidos al día, ticket 135, margen 28 %, fijos 60,000 y entrega 32.60.", "POST",
            "punto-equilibrio/calculos", cuerpo=escenario_a, token=t_adm,
            verificar=lambda r: r.json["decision"] == "no_viable" and abs(r.json["equilibrio_diario"] - 60000 / 5.2 / 30) < 0.01 and len(r.json["pasos"]) == 3,
            explicacion="Margen por pedido = 135 × 28 % − 32.60 = 5.20. Equilibrio mensual = 60,000 ÷ 5.20 = 11,538 pedidos; diario = 384.6, contra 45 esperados: "
                        "no es viable con estos supuestos. La respuesta trae el cálculo paso a paso.")
    base = {"ticket": 150, "margen_bruto": 0.30, "costos_fijos": 40000, "costo_variable_pedido": 20}
    for cid_, pedidos, decision in (("EQU-02", 70, "viable"), ("EQU-03", 55, "viable_ajustado"), ("EQU-04", 40, "no_viable")):
        ev.caso(cid_, "punto-equilibrio", f"Decisión: {decision}", f"Con {pedidos} pedidos al día el equilibrio es 53.3.", "POST", "punto-equilibrio/calculos",
                cuerpo={**base, "pedidos_dia": pedidos}, token=t_adm, verificar=lambda r, d=decision: r.json["decision"] == d)
    ev.caso("EQU-05", "punto-equilibrio", "Equilibrio de un microhub con sus datos", "Costos de costos, ticket y demanda de demanda, personal de cobertura.", "POST",
            "punto-equilibrio/calculos", cuerpo={"microhub_id": hub1}, token=t_adm,
            verificar=lambda r: r.json["entrada"]["origen"]["costos_fijos"] == "costos" and r.json["entrada"]["origen"]["pedidos_dia"] == "demanda_repartida",
            explicacion="La respuesta dice de dónde salió cada número (costos, demanda, configuración o manual). La demanda de cada zona se reparte entre los "
                        "microhubs que la cubren.")
    ev.caso("EQU-06", "punto-equilibrio", "Un dato escrito sustituye al de otro servicio", "Con ticket = 200 el origen del ticket es «manual».", "POST",
            "punto-equilibrio/calculos", cuerpo={"microhub_id": hub1, "ticket": 200}, token=t_adm, verificar=lambda r: r.json["entrada"]["origen"]["ticket"] == "manual")
    ev.caso("EQU-07", "punto-equilibrio", "Falta información", "Sin microhub ni candidato hay que dar los datos.", "POST", "punto-equilibrio/calculos", cuerpo={"pedidos_dia": 10},
            token=t_adm, esperado=422)
    ev.caso("EQU-08", "punto-equilibrio", "Sensibilidad", "Cada variable sube y baja 10 y 20 %; se ordenan por lo que mueven la utilidad.", "POST",
            "punto-equilibrio/sensibilidad", cuerpo={**base, "pedidos_dia": 70}, token=t_adm,
            verificar=lambda r: len(r.json["filas"]) == 20 and r.json["variable_mas_sensible"] == r.json["ranking"][0]["etiqueta"])
    ev.caso("EQU-09", "punto-equilibrio", "Equilibrio (XML)", "Entrada y salida en XML, validadas contra punto_equilibrio.xsd.", "POST", "punto-equilibrio/calculos",
            cuerpo=xml("equilibrio_calculo_nuevo", escenario_a), token=t_plan, formato="xml", verificar=lambda r: "<equilibrio_calculo" in r.texto)
    ev.caso("EQU-10", "punto-equilibrio", "Guardar sin permiso", "Guardar un escenario exige equilibrio.editar.", "POST", "punto-equilibrio/calculos",
            cuerpo={**escenario_a, "guardar": True}, token=t_aud, esperado=403)
    guardados = []
    for cid_, nombre, pedidos in (("EQU-11", "Evidencia equilibrio A", 45), ("EQU-12", "Evidencia equilibrio B", 80)):
        r = ev.caso(cid_, "punto-equilibrio", f"Guardar «{nombre}»", "Queda en equilibrio_escenario con su cálculo completo.", "POST", "punto-equilibrio/calculos",
                    cuerpo={**base, "pedidos_dia": pedidos, "guardar": True, "nombre": nombre}, token=t_plan, esperado=201, verificar=lambda r: r.json["id"] is not None,
                    evidencia=lambda r, n=nombre: [pg("SELECT id, nombre, microhub_id, candidato_id, creado_por FROM equilibrio_escenario WHERE nombre = %s", (n,))])
        if r is not None and r.status == 201:
            guardados.append(r.json["id"])
    ev.caso("EQU-13", "punto-equilibrio", "Escenarios guardados", "Abrir la lista de escenarios.", "GET", "punto-equilibrio/escenarios?por_pagina=100", token=t_adm,
            verificar=lambda r: set(guardados) <= {e["id"] for e in r.json["datos"]})
    if len(guardados) == 2:
        ev.caso("EQU-14", "punto-equilibrio", "Comparar escenarios", "Lado a lado: decisión, equilibrio, diferencia y utilidad.", "GET",
                f"punto-equilibrio/comparacion?ids={guardados[0]},{guardados[1]}", token=t_adm, verificar=lambda r: r.json["mejor_utilidad_id"] == guardados[1])
        ev.caso("EQU-15", "punto-equilibrio", "Abrir un escenario", "Con su cálculo paso a paso.", "GET", f"punto-equilibrio/escenarios/{guardados[0]}", token=t_adm,
                verificar=lambda r: r.json["pasos"])
        ev.caso("EQU-16", "punto-equilibrio", "Borrar sin permiso", "Borrar es de equilibrio.editar.", "DELETE", f"punto-equilibrio/escenarios/{guardados[0]}", token=t_aud, esperado=403)
        ev.caso("EQU-17", "punto-equilibrio", "Borrar un escenario", "Se elimina el escenario.", "DELETE", f"punto-equilibrio/escenarios/{guardados[0]}", token=t_plan, esperado=204,
                evidencia=lambda r: [pg("SELECT count(*) AS quedan FROM equilibrio_escenario WHERE id = %s", (guardados[0],))])
    ejecutar("DELETE FROM equilibrio_escenario WHERE nombre IN ('Evidencia equilibrio A', 'Evidencia equilibrio B')")
    ev.caso("EQU-18", "punto-equilibrio", "Equilibrio de todos los microhubs", "Una fila por microhub activo con sus datos reales.", "GET", "punto-equilibrio/microhubs", token=t_adm,
            verificar=lambda r: len(r.json["datos"]) == uno("SELECT count(*) AS n FROM microhub WHERE estatus = 'activo'")["n"])
    ev.caso("EQU-19", "punto-equilibrio", "Supuestos del equilibrio", "Margen de seguridad mínimo y margen bruto por omisión.", "GET", "punto-equilibrio/supuestos", token=t_adm,
            verificar=lambda r: {"peq_margen_seguridad_pct", "margen_bruto_default"} <= {s["clave"] for s in r.json["datos"]})

    # ================= SURTIDO =================
    print("  Surtido (5122)")
    ev.caso("SUR-01", "surtido", "Clasificación ABC", "A hasta 80 % acumulado de unidades, B hasta 95 %, C el resto.", "GET", f"surtido/abc?microhub_id={hub1}", token=t_adm,
            verificar=lambda r: [c["clase"] for c in r.json["clases"]] == ["A", "B", "C"] and r.json["clases"][0]["pct_unidades"] >= 70,
            explicacion="El corte (80/95) es una convención de Pareto, documentada como «normativo» en GET /surtido/supuestos.")
    ev.caso("SUR-02", "surtido", "Análisis de un microhub", "Clase, rotación, cobertura, margen, quiebres y recomendación por producto.", "GET",
            f"surtido/analisis?microhub_id={hub1}", token=t_adm,
            verificar=lambda r: r.json["resumen"]["productos"] == len(r.json["filas"]) and all(f["recomendacion"] in ("Aumentar", "Mantener", "Reducir", "Eliminar", "Excluir") for f in r.json["filas"]),
            explicacion="Aumentar si hubo quiebres, la existencia está en el mínimo o la cobertura de un A o B es menos de la mitad del objetivo; Reducir con más de 30 "
                        "días de cobertura; Eliminar si no se movió. Lo que se sugiere aumentar se limita al espacio y al presupuesto del microhub.",
            evidencia=lambda r: [pg("SELECT microhub_id, espacio_total, presupuesto FROM surtido_restriccion ORDER BY microhub_id")])
    ev.caso("SUR-03", "surtido", "Análisis de toda la red", "Sin microhub no hay restricciones de espacio ni de presupuesto.", "GET", "surtido/analisis", token=t_adm,
            verificar=lambda r: r.json["microhub"] is None and r.json["resumen"]["espacio"]["total"] is None)
    ev.caso("SUR-04", "surtido", "Solo clase A", "Filtro por clase.", "GET", f"surtido/analisis?microhub_id={hub1}&clase=A", token=t_adm,
            verificar=lambda r: r.json["filas"] and {f["clase"] for f in r.json["filas"]} == {"A"})
    ev.caso("SUR-05", "surtido", "Clase inventada", "Solo A, B o C.", "GET", f"surtido/analisis?microhub_id={hub1}&clase=Z", token=t_adm, esperado=400)
    ev.caso("SUR-06", "surtido", "Análisis (XML)", "Respuesta XML que cumple surtido.xsd.", "GET", f"surtido/analisis?microhub_id={hub1}", token=t_adm, formato="xml",
            verificar=lambda r: "<surtido_analisis" in r.texto)
    ev.caso("SUR-07", "surtido", "El operador analiza su microhub", "Operador y supervisor solo trabajan con el suyo.", "GET", f"surtido/analisis?microhub_id={hub1}", token=t_op1)
    ev.caso("SUR-08", "surtido", "El operador analiza otro microhub", "No puede.", "GET", f"surtido/analisis?microhub_id={hub2}", token=t_op1, esperado=403)
    ev.caso("SUR-09", "surtido", "Restricciones de un microhub", "Espacio y presupuesto.", "GET", f"surtido/restricciones/{hub1}", token=t_adm,
            verificar=lambda r: r.json["espacio_total"] > 0)
    rest = uno("SELECT espacio_total, presupuesto FROM surtido_restriccion WHERE microhub_id = %s", (hub1,))
    ev.caso("SUR-10", "surtido", "Cambiar las restricciones", "El planeador fija otro espacio y presupuesto.", "PUT", f"surtido/restricciones/{hub1}",
            cuerpo={"espacio_total": float(rest["espacio_total"]) + 100, "presupuesto": float(rest["presupuesto"])}, token=t_plan,
            verificar=lambda r: r.json["espacio_total"] == float(rest["espacio_total"]) + 100,
            evidencia=lambda r: [pg("SELECT espacio_total, presupuesto FROM surtido_restriccion WHERE microhub_id = %s", (hub1,)),
                                 pg("SELECT accion, entidad, valores_anteriores, valores_nuevos FROM auditoria WHERE entidad = 'surtido_restriccion' ORDER BY id DESC LIMIT 1")])
    ejecutar("UPDATE surtido_restriccion SET espacio_total = %s, presupuesto = %s WHERE microhub_id = %s", (rest["espacio_total"], rest["presupuesto"], hub1))
    ev.caso("SUR-19", "surtido", "Cambiar las restricciones con PATCH", "PATCH es alias de PUT.", "PATCH", f"surtido/restricciones/{hub1}",
            cuerpo={"espacio_total": float(rest["espacio_total"]) + 50, "presupuesto": float(rest["presupuesto"])}, token=t_plan,
            verificar=lambda r: r.json["espacio_total"] == float(rest["espacio_total"]) + 50)
    ejecutar("UPDATE surtido_restriccion SET espacio_total = %s, presupuesto = %s WHERE microhub_id = %s", (rest["espacio_total"], rest["presupuesto"], hub1))
    ev.caso("SUR-11", "surtido", "Cambiar restricciones sin permiso", "Solo surtido.editar.", "PUT", f"surtido/restricciones/{hub1}", cuerpo={"espacio_total": 10}, token=t_aud, esperado=403)
    ev.caso("SUR-12", "surtido", "Espacio inválido", "Mayor que cero.", "PUT", f"surtido/restricciones/{hub1}", cuerpo={"espacio_total": 0}, token=t_plan, esperado=422)
    r = ev.caso("SUR-13", "surtido", "Guardar la recomendación", "Queda con sus líneas y los supuestos usados, para compararla después.", "POST", "surtido/recomendaciones",
                cuerpo={"microhub_id": hub1, "nota": "Evidencia de la Ola 2"}, token=t_plan, esperado=201,
                verificar=lambda r: len(r.json["lineas"]) == r.json["resumen"]["productos"],
                evidencia=lambda r: [pg("SELECT id, microhub_id, resumen, creado_por FROM surtido_recomendacion WHERE parametros::jsonb ->> 'nota' = 'Evidencia de la Ola 2'"),
                                     pg("SELECT accion, count(*) AS lineas, sum(sugerido) AS sugerido FROM surtido_recomendacion_linea WHERE recomendacion_id = "
                                        "(SELECT max(id) FROM surtido_recomendacion) GROUP BY accion ORDER BY accion")])
    if r is not None and r.status == 201:
        rid = r.json["id"]
        ev.caso("SUR-18", "surtido", "Recomendaciones guardadas", "Para compararlas con el tiempo.", "GET", f"surtido/recomendaciones?microhub_id={hub1}", token=t_adm,
                verificar=lambda x: rid in [g["id"] for g in x.json["datos"]])
        ev.caso("SUR-14", "surtido", "Abrir la recomendación", "Con el mismo resumen con que se guardó.", "GET", f"surtido/recomendaciones/{rid}", token=t_adm,
                verificar=lambda x: x.json["resumen"] == r.json["resumen"])
        ev.caso("SUR-15", "surtido", "Otro microhub abre la recomendación", "El operador de otro microhub no la ve.", "GET", f"surtido/recomendaciones/{rid}", token=t_op2, esperado=403)
    ev.caso("SUR-16", "surtido", "Guardar sin permiso", "El operador no tiene surtido.editar.", "POST", "surtido/recomendaciones", cuerpo={"microhub_id": hub1}, token=t_op1, esperado=403)
    ejecutar("DELETE FROM surtido_recomendacion WHERE parametros::jsonb ->> 'nota' = 'Evidencia de la Ola 2'")
    ev.caso("SUR-17", "surtido", "Supuestos del surtido", "Cortes ABC, días de cobertura y ventana de análisis.", "GET", "surtido/supuestos", token=t_adm,
            verificar=lambda r: {"abc_a_pct", "ventana_analisis_dias"} <= {s["clave"] for s in r.json["datos"]})

    # ================= RUTAS =================
    print("  Rutas (5118)")
    listos = dejar_listos(6, microhub_id=hub1)
    ids_listos = [p["pedido_id"] for p in listos]
    ev.caso("RUT-01", "pedidos", "Pedidos listos para despachar", "Los que rutas va a agrupar: en preparación y marcados como listos.", "GET",
            f"pedidos/listos?microhub_id={hub1}&por_pagina=100", token=t_op1, verificar=lambda r: set(ids_listos) <= {p["id"] for p in r.json["datos"]},
            evidencia=lambda r: [pg("SELECT id, folio, estado, zona_id, listo_en IS NOT NULL AS listo FROM pedido WHERE id = ANY(%s) ORDER BY id", (ids_listos,))])
    ev.caso("RUT-02", "rutas", "Calcular un plan sin guardarlo", "Agrupa por zona, reparte entre repartidores, ordena las paradas, y calcula distancia, tiempo y costo.", "POST",
            "rutas/planes", cuerpo={"microhub_id": hub1, "pedido_ids": ids_listos}, token=t_op1,
            verificar=lambda r: sorted(x["pedido"]["id"] for ruta in r.json["rutas"] for x in ruta["paradas"]) == sorted(ids_listos) and r.json["id"] is None,
            explicacion="Exacto (prueba todos los órdenes) hasta 8 paradas; con más, vecino más cercano mejorado con 2-opt. Distancia por calle = línea recta × 1.3; "
                        "minutos = distancia ÷ 22 km/h + 4 min por parada; costo = km × 4.50 + 18 por entrega.",
            evidencia=lambda r: [pg("SELECT count(*) AS planes FROM plan_despacho WHERE microhub_id = %s", (hub1,))])
    ev.caso("RUT-03", "rutas", "Comparar métodos de recorrido", "Las mismas paradas con orden de llegada, vecino más cercano, 2-opt y exacto.", "POST", "rutas/comparaciones",
            cuerpo={"microhub_id": hub1, "pedido_ids": ids_listos}, token=t_op1, verificar=lambda r: len(r.json["filas"]) == 4 and r.json["filas"][0]["mejora_pct"] == 0.0)
    ev.caso("RUT-04", "rutas", "Otro método", "El exacto con un solo repartidor.", "POST", "rutas/planes", cuerpo={"microhub_id": hub1, "pedido_ids": ids_listos, "metodo": "exacto"},
            token=t_op1, verificar=lambda r: all(ruta["metodo"] == "TSP exacto" for ruta in r.json["rutas"]))
    r = ev.caso("RUT-05", "rutas", "Guardar un plan propuesto", "Queda en plan_despacho como «propuesto»; todavía no escribe rutas.", "POST", "rutas/planes",
                cuerpo={"microhub_id": hub1, "pedido_ids": ids_listos, "guardar": True}, token=t_plan, esperado=201, verificar=lambda r: r.json["estado"] == "propuesto",
                evidencia=lambda r: [pg("SELECT id, microhub_id, estado, version FROM plan_despacho WHERE id = %s", (r.json["id"],)),
                                     pg("SELECT count(*) AS rutas FROM plan_ruta WHERE plan_despacho_id = %s", (r.json["id"],))])
    if r is not None and r.status == 201:
        pid = r.json["id"]
        primero = r.json["rutas"][0]["paradas"][0]["pedido"]["id"]
        rep = r.json["rutas"][0]["repartidor"]["id"]
        ev.caso("RUT-06", "rutas", "Retraso de un repartidor", "Suma minutos a su ruta y dice qué paradas quedan fuera de la promesa de 30 minutos.", "POST",
                f"rutas/planes/{pid}/ajustes", cuerpo={"tipo": "retraso", "repartidor_id": rep, "minutos": 25}, token=t_plan,
                verificar=lambda x: x.json["version"] == 2 and "paradas_fuera_de_promesa" in x.json)
        ev.caso("RUT-07", "rutas", "Quitar un pedido", "Recalcula la ruta afectada con el mismo método.", "POST", f"rutas/planes/{pid}/ajustes",
                cuerpo={"tipo": "quitar_pedido", "pedido_id": primero}, token=t_plan,
                verificar=lambda x: x.json["total"]["paradas"] == len(ids_listos) - 1)
        ev.caso("RUT-08", "rutas", "Agregar de nuevo el pedido", "Lo pone en la ruta con menos paradas, sin pasar del tope de 8.", "POST", f"rutas/planes/{pid}/ajustes",
                cuerpo={"tipo": "agregar_pedido", "pedido_id": primero}, token=t_plan, verificar=lambda x: x.json["total"]["paradas"] == len(ids_listos))
        ev.caso("RUT-09", "rutas", "El operador de otro microhub abre el plan", "Operador y supervisor solo trabajan con el suyo.", "GET", f"rutas/planes/{pid}", token=t_op2, esperado=403)
        ev.caso("RUT-10", "rutas", "Confirmar el plan", "Comprueba que los pedidos sigan listos y deja las rutas en plan_ruta.", "POST", f"rutas/planes/{pid}/confirmar",
                cuerpo={}, token=t_plan, verificar=lambda x: x.json["estado"] == "confirmado",
                evidencia=lambda x: [pg("SELECT id, repartidor_id, metodo, paradas, distancia_km, minutos, costo_estimado FROM plan_ruta WHERE plan_despacho_id = %s ORDER BY id", (pid,)),
                                     pg("SELECT count(*) AS paradas FROM plan_ruta_parada WHERE plan_ruta_id IN (SELECT id FROM plan_ruta WHERE plan_despacho_id = %s)", (pid,))])
        ev.caso("RUT-11", "rutas", "Confirmar otra vez", "Un plan confirmado no se vuelve a confirmar.", "POST", f"rutas/planes/{pid}/confirmar", cuerpo={}, token=t_plan, esperado=409)
        ev.caso("RUT-12", "rutas", "Planes guardados", "Lista con estado, rutas, paradas, distancia y costo.", "GET", f"rutas/planes?microhub_id={hub1}", token=t_adm,
                verificar=lambda x: pid in [p["id"] for p in x.json["datos"]])
        ejecutar("DELETE FROM plan_ruta_parada WHERE plan_ruta_id IN (SELECT id FROM plan_ruta WHERE plan_despacho_id = %s)", (pid,))
        ejecutar("DELETE FROM plan_ruta WHERE plan_despacho_id = %s", (pid,))
        ejecutar("DELETE FROM plan_despacho WHERE id = %s", (pid,))
    r = ev.http("rutas", "POST", "rutas/planes", {"microhub_id": hub1, "pedido_ids": ids_listos, "guardar": True}, token=t_plan)[0]
    if r.status == 201:
        ev.caso("RUT-13", "rutas", "Cancelar un plan propuesto", "Un plan que no se confirmó se cancela.", "POST", f"rutas/planes/{r.json['id']}/cancelar", cuerpo={}, token=t_plan,
                verificar=lambda x: x.json["estado"] == "cancelado")
        ejecutar("DELETE FROM plan_despacho WHERE id = %s", (r.json["id"],))
    ev.caso("RUT-14", "rutas", "Un microhub sin pedidos listos", "No hay nada que despachar.", "POST", "rutas/planes", cuerpo={"microhub_id": hub3}, token=t_plan, esperado=422)
    ev.caso("RUT-15", "rutas", "Pedidos que no están listos", "Un pedido ajeno o no listo se rechaza.", "POST", "rutas/planes", cuerpo={"microhub_id": hub1, "pedido_ids": [999999]},
            token=t_plan, esperado=422)
    ev.caso("RUT-16", "rutas", "El operador planea otro microhub", "No puede.", "POST", "rutas/planes", cuerpo={"microhub_id": hub1, "pedido_ids": ids_listos}, token=t_op2, esperado=403)
    ev.caso("RUT-17", "rutas", "El auditor intenta planear", "Consulta, no planea.", "POST", "rutas/planes", cuerpo={"microhub_id": hub1}, token=t_aud, esperado=403)
    lista_xml = "<pedido_ids>" + "".join(f"<id>{i}</id>" for i in ids_listos[:3]) + "</pedido_ids>"
    ev.caso("RUT-18", "rutas", "Plan en XML con lista de pedidos", "El cuerpo XML lleva la lista de pedidos y se valida contra rutas.xsd.", "POST", "rutas/planes",
            cuerpo=f'<?xml version="1.0" encoding="UTF-8"?><ruta_plan_nuevo xmlns="{h.NS}"><microhub_id>{hub1}</microhub_id>{lista_xml}<metodo>exacto</metodo></ruta_plan_nuevo>',
            token=t_plan, formato="xml", verificar=lambda x: "<ruta_plan" in x.texto)
    from pruebas.preparar_listos import retirar
    retirar([p["pedido_id"] for p in listos if p["nuevo"]])                 # los pedidos que se prepararon para la evidencia se retiran
    ev.caso("RUT-19", "rutas", "Supuestos de las rutas", "Velocidad, tiempo por parada, costo por km, tope de paradas y rodeo.", "GET", "rutas/supuestos", token=t_adm,
            verificar=lambda x: {"velocidad_reparto_kmh", "max_paradas_repartidor", "factor_rodeo_distancia"} <= {s["clave"] for s in x.json["datos"]})

    # ================= SIMULACIÓN =================
    print("  Simulación (5121)")

    def esperar(eid, fin=("terminada", "fallida", "cancelada")):
        for _ in range(60):
            r_, _e = ev.http("simulacion", "GET", f"simulacion/ejecuciones/{eid}", token=t_adm)
            if r_.json and r_.json["estado"] in fin:
                return r_
            time.sleep(0.5)
        return r_

    creadas = []
    r = ev.caso("SIM-01", "simulacion", "Poner una simulación en cola", "Junta la entrada de otros servicios, la guarda y responde 202 sin esperar el resultado.", "POST",
                "simulacion/ejecuciones", cuerpo={"microhub_id": hub1, "dias": 14, "replicas": 100, "semilla": 11}, token=t_plan, esperado=202,
                verificar=lambda x: x.json["estado"] in ("en_cola", "ejecutando") and x.json["resultados"] is None,
                explicacion="La entrada (demanda, ticket, costos, personal, capacidad y su origen) queda guardada en la ejecución: con ella y la semilla el resultado "
                            "es siempre el mismo. Un hilo del servicio la toma de la cola con FOR UPDATE SKIP LOCKED.",
                evidencia=lambda x: [pg("SELECT id, estado, semilla, version_modelo, creado_por, parametros::jsonb -> 'replicas' AS replicas FROM simulacion_ejecucion WHERE id = %s", (x.json["id"],))])
    if r is not None and r.status == 202:
        sid = r.json["id"]
        creadas.append(sid)
        t = esperar(sid)
        ev.caso("SIM-02", "simulacion", "Resultados de la simulación", "Media y percentiles 10, 50 y 90 de utilidad, pedidos atendidos y rechazados; probabilidad de perder.", "GET",
                f"simulacion/ejecuciones/{sid}", token=t_adm, verificar=lambda x: x.json["estado"] == "terminada" and len(x.json["huella"]) == 64,
                explicacion="Monte Carlo día por día: demanda de Poisson por el índice semanal, ausentismo de operadores y repartidores, capacidad con el personal "
                            "presente. La huella es el SHA-256 de los resultados.",
                evidencia=lambda x: [pg("SELECT estado, huella, inicio_en IS NOT NULL AS inicio, fin_en IS NOT NULL AS fin, intentos FROM simulacion_ejecucion WHERE id = %s", (sid,))])
        rep = ev.caso("SIM-03", "simulacion", "Repetir con la misma entrada y semilla", "Debe dar exactamente lo mismo.", "POST", f"simulacion/ejecuciones/{sid}/repetir",
                      cuerpo={}, token=t_plan, esperado=202)
        if rep is not None and rep.status == 202:
            rid = rep.json["id"]
            creadas.append(rid)
            esperar(rid)
            ev.caso("SIM-04", "simulacion", "La repetición coincide", "Misma huella: la simulación es reproducible.", "GET", f"simulacion/ejecuciones/{rid}", token=t_adm,
                    verificar=lambda x: x.json["reproducible"] is True and x.json["huella"] == t.json["huella"],
                    evidencia=lambda x: [pg("SELECT id, estado, huella, parametros::jsonb ->> 'repeticion_de' AS repite_a FROM simulacion_ejecucion WHERE id = ANY(%s::uuid[]) ORDER BY creado_en",
                                            ([sid, rid],))])
        otra = ev.http("simulacion", "POST", "simulacion/ejecuciones", {"microhub_id": hub1, "dias": 14, "replicas": 100, "semilla": 12}, token=t_plan)[0]
        if otra.status == 202:
            creadas.append(otra.json["id"])
            t2 = esperar(otra.json["id"])
            ev.caso("SIM-05", "simulacion", "Otra semilla, otro resultado", "Misma entrada con semilla 12: la huella cambia.", "GET", f"simulacion/ejecuciones/{otra.json['id']}",
                    token=t_adm, verificar=lambda x: x.json["huella"] != t.json["huella"])
            ev.caso("SIM-06", "simulacion", "Comparar ejecuciones", "Utilidad media, P10, P90, probabilidad de pérdida y días saturados lado a lado.", "GET",
                    f"simulacion/comparacion?ids={sid},{otra.json['id']}", token=t_adm, verificar=lambda x: len(x.json["ejecuciones"]) == 2)
    manual = ev.caso("SIM-07", "simulacion", "Escenario manual", "Sin microhub ni candidato, con todos los datos escritos (el escenario A).", "POST", "simulacion/ejecuciones",
                     cuerpo={"pedidos_dia": 45, "ticket": 135, "costos_fijos": 60000, "costo_variable_pedido": 32.6, "operadores": 3, "repartidores": 2, "dias": 14,
                             "replicas": 100, "semilla": 12}, token=t_plan, esperado=202, verificar=lambda x: x.json["objeto"]["tipo"] == "manual")
    if manual is not None and manual.status == 202:
        creadas.append(manual.json["id"])
        esperar(manual.json["id"])
        ev.caso("SIM-08", "simulacion", "Con el escenario A se pierde dinero", "100 % de las réplicas terminan en pérdida: lo que ya decía el punto de equilibrio.", "GET",
                f"simulacion/ejecuciones/{manual.json['id']}", token=t_adm, verificar=lambda x: x.json["resultados"]["prob_perdida_pct"] == 100.0)
    ev.caso("SIM-09", "simulacion", "Entrada incompleta", "Sin microhub hay que dar todos los datos.", "POST", "simulacion/ejecuciones", cuerpo={"pedidos_dia": 45}, token=t_plan, esperado=422,
            verificar=lambda x: {"ticket", "costos_fijos", "operadores"} <= {d["campo"] for d in x.json["error"]["detalles"]})
    ev.caso("SIM-10", "simulacion", "Demasiado trabajo", "Días × réplicas no puede pasar de 200,000.", "POST", "simulacion/ejecuciones",
            cuerpo={"microhub_id": hub1, "dias": 365, "replicas": 2000}, token=t_plan, esperado=422)
    grande = ev.http("simulacion", "POST", "simulacion/ejecuciones", {"microhub_id": hub1, "dias": 300, "replicas": 600}, token=t_plan)[0]
    if grande.status == 202:
        creadas.append(grande.json["id"])
        ev.caso("SIM-11", "simulacion", "Cancelar una ejecución", "Una ejecución en cola o en curso se puede cancelar.", "POST", f"simulacion/ejecuciones/{grande.json['id']}/cancelar",
                cuerpo={}, token=t_plan, verificar=lambda x: x.json["estado"] == "cancelada",
                evidencia=lambda x: [pg("SELECT id, estado, fin_en IS NOT NULL AS fin, resultados IS NULL AS sin_resultados FROM simulacion_ejecucion WHERE id = %s", (grande.json["id"],))])
        ev.caso("SIM-12", "simulacion", "Cancelar una cancelada", "Solo se cancela lo que está en cola o en curso.", "POST", f"simulacion/ejecuciones/{grande.json['id']}/cancelar",
                cuerpo={}, token=t_plan, esperado=409)
    ev.caso("SIM-13", "simulacion", "Ejecuciones", "Lista paginada, la más reciente primero.", "GET", "simulacion/ejecuciones?por_pagina=5", token=t_adm,
            verificar=lambda x: x.json["datos"] and "huella" in x.json["datos"][0])
    ev.caso("SIM-14", "simulacion", "El auditor consulta simulaciones", "Sin simulacion.ver.", "GET", "simulacion/ejecuciones", token=t_aud, esperado=403)
    ev.caso("SIM-15", "simulacion", "El operador simula", "Sin simulacion.ejecutar.", "POST", "simulacion/ejecuciones", cuerpo={"microhub_id": hub1}, token=t_op1, esperado=403)
    en_xml = ev.caso("SIM-16", "simulacion", "Poner en cola (XML)", "Entrada y salida en XML, validadas contra simulacion.xsd.", "POST", "simulacion/ejecuciones",
                     cuerpo=xml("simulacion_nueva", {"microhub_id": hub1, "dias": 5, "replicas": 20, "semilla": 3}), token=t_plan, formato="xml", esperado=202,
                     verificar=lambda x: "<simulacion_ejecucion" in x.texto)
    ev.caso("SIM-17", "simulacion", "Una ejecución inexistente", "Un identificador que no existe.", "GET", f"simulacion/ejecuciones/{uuid.uuid4()}", token=t_adm, esperado=404)
    ev.caso("SIM-18", "simulacion", "Supuestos de la simulación", "Réplicas, ausentismo, variación de la demanda y semilla.", "GET", "simulacion/supuestos", token=t_plan,
            verificar=lambda x: {"sim_ausentismo", "sim_variacion_demanda"} <= {s["clave"] for s in x.json["datos"]})
    # espera a que el trabajador termine lo que quedó en cola y limpia
    time.sleep(1.5)
    ejecutar("DELETE FROM simulacion_ejecucion WHERE creado_en > now() - interval '30 minutes' AND creado_por = (SELECT id FROM usuario WHERE correo = 'planeador@codex.mx')")
