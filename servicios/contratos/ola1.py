"""
ola1.py — Contrato v1 de los servicios de la Ola 1: inventario, precios, proveedores, abastecimiento y notificaciones.

El orden de los campos de cada tipo es el orden de las llaves que devuelve el servicio (xs:sequence).
Regenerar:  cd servicios && python contratos/generar.py ola1
"""
from generar import F

L = lambda tipo, item: [F("datos", [tipo], item=item), F("paginacion", "TPaginacion")]    # página de resultados
PAG = {"pagina": 1, "por_pagina": 20, "total": 1, "paginas": 1}
HUB = {"id": 1, "nombre": "Microhub San Bernabé Centro"}
PROD = {"id": 4, "nombre": "Aceite vegetal 1 L"}
PROD_CLAVE = {"id": 4, "clave_interna": "AB-004", "nombre": "Aceite vegetal 1 L"}
REF_ORDEN = {"tipo": "orden_compra", "id": "7"}
FECHA = "2026-10-19T09:30:00-06:00"

MOV_TIPOS = ["recepcion", "salida_pedido", "devolucion_cancelacion", "devolucion_parcial", "merma", "ajuste", "conteo",
             "transferencia_salida", "transferencia_entrada"]
NOTIF_TIPOS = ["pedido", "entrega", "sistema", "planeacion", "inventario", "abastecimiento"]
NOTIF_REFS = ["pedido", "entrega", "candidato", "sistema", "producto", "solicitud", "orden"]
PREF_TIPOS = ["pedido", "entrega", "planeacion", "inventario", "abastecimiento"]

# --------------------------------------------------------------------
# Tipos compartidos por los cinco servicios
# --------------------------------------------------------------------
COMUN = {
    "TRefNombre": [F("id", "long"), F("nombre", "string", nil=True)],
    "TRefProductoClave": [F("id", "long"), F("clave_interna", "string", nil=True), F("nombre", "string", nil=True)],
    "TRefTipoId": [F("tipo", "string", max=30), F("id", "string", max=40)],
}

# --------------------------------------------------------------------
# Inventario
# --------------------------------------------------------------------
INVENTARIO = {
    "TInvExistencia": [F("microhub", "TRefNombre"), F("producto", "TRefProductoClave"), F("existencia", "int"), F("minimo", "int"),
                       F("reservado", "int"), F("disponible", "int"), F("estado", "string", enum=["agotado", "bajo_minimo", "normal"]),
                       F("actualizado_en", "dateTime")],
    "TInvExistenciaLista": L("TInvExistencia", "existencia"),
    "TInvMinimoNuevo": [F("minimo", "int", min=0, maxv=100000)],
    "TInvMovimiento": [F("id", "long"), F("microhub_id", "long"), F("producto_id", "long"), F("tipo", "string", enum=MOV_TIPOS),
                       F("cantidad", "int"), F("existencia_resultante", "int", min=0), F("referencia", "TRefTipoId", nil=True),
                       F("motivo", "string", nil=True), F("usuario_id", "long", nil=True), F("fecha", "dateTime")],
    "TInvMovimientoLista": L("TInvMovimiento", "movimiento"),
    "TInvMovimientoNuevo": [F("microhub_id", "long"), F("producto_id", "long"), F("tipo", "string", enum=["recepcion", "merma", "ajuste", "conteo"]),
                            F("cantidad", "int"), F("motivo", "string", opt=True, nil=True, max=300), F("referencia", "TRefTipoId", opt=True, nil=True),
                            F("operacion_uuid", "string", opt=True, nil=True, max=80, minlen=8)],
    "TInvMovimientoRegistrado": [F("movimiento", "TInvMovimiento"), F("duplicado", "bool")],
    "TInvTransferenciaNueva": [F("origen_microhub_id", "long"), F("destino_microhub_id", "long"), F("producto_id", "long"),
                               F("cantidad", "int", min=1), F("motivo", "string", max=300, minlen=3),
                               F("operacion_uuid", "string", opt=True, nil=True, max=80, minlen=8)],
    "TInvTransferenciaExtremo": [F("microhub_id", "long"), F("existencia", "int", min=0), F("movimiento_id", "long")],
    "TInvTransferencia": [F("producto_id", "long"), F("cantidad", "int", min=1), F("duplicado", "bool"),
                          F("origen", "TInvTransferenciaExtremo"), F("destino", "TInvTransferenciaExtremo")],
    "TInvReserva": [F("id", "long"), F("microhub_id", "long"), F("producto_id", "long"), F("cantidad", "int", min=1),
                    F("estado", "string", enum=["activa", "liberada", "consumida"]), F("vigente", "bool"), F("referencia", "TRefTipoId"),
                    F("creada_en", "dateTime"), F("vence_en", "dateTime"), F("cerrada_en", "dateTime", nil=True)],
    "TInvReservaLista": L("TInvReserva", "reserva"),
    "TInvReservaNueva": [F("microhub_id", "long"), F("producto_id", "long"), F("cantidad", "int", min=1), F("referencia", "TRefTipoId"),
                         F("minutos", "int", opt=True, nil=True, min=1, maxv=1440)],
    "TInvAlerta": [F("microhub", "TRefNombre"), F("producto", "TRefProductoClave"), F("existencia", "int"), F("minimo", "int"),
                   F("disponible", "int"), F("faltante", "int", min=0), F("severidad", "string", enum=["agotado", "critica", "baja"])],
    "TInvAlertaLista": L("TInvAlerta", "alerta"),
}
INVENTARIO_RAICES = {"existencias": "TInvExistenciaLista", "existencia": "TInvExistencia", "minimo_nuevo": "TInvMinimoNuevo",
                     "movimientos": "TInvMovimientoLista", "movimiento_nuevo": "TInvMovimientoNuevo",
                     "movimiento_registrado": "TInvMovimientoRegistrado", "transferencia_nueva": "TInvTransferenciaNueva",
                     "transferencia": "TInvTransferencia", "reservas": "TInvReservaLista", "reserva": "TInvReserva",
                     "reserva_nueva": "TInvReservaNueva", "alertas": "TInvAlertaLista"}

EXISTENCIA = {"microhub": HUB, "producto": PROD_CLAVE, "existencia": 18, "minimo": 10, "reservado": 3, "disponible": 15, "estado": "normal",
              "actualizado_en": FECHA}
MOVIMIENTO = {"id": 912, "microhub_id": 1, "producto_id": 4, "tipo": "recepcion", "cantidad": 24, "existencia_resultante": 42,
              "referencia": REF_ORDEN, "motivo": "Recepción de la orden OC-20261019-000007", "usuario_id": 2, "fecha": FECHA}
RESERVA = {"id": 31, "microhub_id": 1, "producto_id": 4, "cantidad": 3, "estado": "activa", "vigente": True,
           "referencia": {"tipo": "pedido", "id": "166"}, "creada_en": FECHA, "vence_en": "2026-10-19T10:00:00-06:00", "cerrada_en": None}
ALERTA = {"microhub": HUB, "producto": PROD_CLAVE, "existencia": 4, "minimo": 10, "disponible": 4, "faltante": 6, "severidad": "critica"}

INVENTARIO_EJEMPLOS = {
    "InventarioLista": ("existencias", {"datos": [EXISTENCIA], "paginacion": PAG}),
    "Existencia": ("existencia", EXISTENCIA),
    "MinimoNuevo": ("minimo_nuevo", {"minimo": 12}),
    "MovimientoLista": ("movimientos", {"datos": [MOVIMIENTO], "paginacion": PAG}),
    "MovimientoNuevo": ("movimiento_nuevo", {"microhub_id": 1, "producto_id": 4, "tipo": "recepcion", "cantidad": 24,
                                             "motivo": "Llegada del proveedor", "referencia": REF_ORDEN,
                                             "operacion_uuid": "c5a1f0e2-6b1d-4f0e-9a43-2b7d8e7a1c10"}),
    "MovimientoRegistrado": ("movimiento_registrado", {"movimiento": MOVIMIENTO, "duplicado": False}),
    "TransferenciaNueva": ("transferencia_nueva", {"origen_microhub_id": 1, "destino_microhub_id": 2, "producto_id": 4, "cantidad": 6,
                                                   "motivo": "El microhub 2 se quedó sin aceite",
                                                   "operacion_uuid": "7d2f4b1a-93c0-4c7e-8b55-0a6f3e9d2b41"}),
    "Transferencia": ("transferencia", {"producto_id": 4, "cantidad": 6, "duplicado": False,
                                        "origen": {"microhub_id": 1, "existencia": 12, "movimiento_id": 913},
                                        "destino": {"microhub_id": 2, "existencia": 14, "movimiento_id": 914}}),
    "ReservaLista": ("reservas", {"datos": [RESERVA], "paginacion": PAG}),
    "ReservaNueva": ("reserva_nueva", {"microhub_id": 1, "producto_id": 4, "cantidad": 3, "referencia": {"tipo": "pedido", "id": "166"},
                                       "minutos": 30}),
    "Reserva": ("reserva", RESERVA),
    "AlertaLista": ("alertas", {"datos": [ALERTA], "paginacion": PAG}),
}

# --------------------------------------------------------------------
# Precios
# --------------------------------------------------------------------
PRECIOS = {
    "TPreListaResumen": [F("id", "long"), F("nombre", "string"), F("zona_id", "long", nil=True), F("vigente_desde", "date"),
                         F("vigente_hasta", "date", nil=True), F("estatus", "string", enum=["activo", "inactivo"]), F("productos", "int")],
    "TPreListaLista": L("TPreListaResumen", "lista"),
    "TPreItem": [F("producto", "TRefNombre"), F("precio", "money"), F("costo", "money", nil=True), F("margen_pct", "num", nil=True),
                 F("actualizado_en", "dateTime")],
    "TPreListaDetalle": [F("id", "long"), F("nombre", "string"), F("zona_id", "long", nil=True), F("vigente_desde", "date"),
                         F("vigente_hasta", "date", nil=True), F("estatus", "string", enum=["activo", "inactivo"]), F("productos", "int"),
                         F("items", ["TPreItem"], item="item")],
    "TPreItemLista": [F("producto_id", "long"), F("precio", "money", min="0.01"), F("costo", "money", opt=True, nil=True, min=0)],
    "TPreListaNueva": [F("nombre", "string", minlen=3, max=80), F("zona_id", "long", opt=True, nil=True),
                       F("vigente_desde", "date", opt=True, nil=True), F("vigente_hasta", "date", opt=True, nil=True),
                       F("items", ["TPreItemLista"], opt=True, item="item")],
    "TPrePrecioNuevo": [F("precio", "money", min="0.01"), F("costo", "money", opt=True, nil=True, min=0)],
    "TPrePromocionAplicada": [F("id", "long"), F("nombre", "string"), F("tipo", "string", enum=["porcentaje", "monto"]), F("valor", "money")],
    "TPrePrecioVigente": [F("producto_id", "long"), F("zona_id", "long", nil=True), F("fecha", "date"), F("precio_base", "money"),
                          F("lista", "TRefNombre", nil=True), F("precio_vigente", "money"), F("promocion", "TPrePromocionAplicada", nil=True),
                          F("descuento", "money"), F("descuento_limitado", "bool"), F("precio_final", "money"), F("costo", "money", nil=True),
                          F("margen_pct", "num", nil=True), F("bajo_margen", "bool")],
    "TPreLineaNueva": [F("producto_id", "long"), F("cantidad", "int", min=1, maxv=10000)],
    "TPreCalculoNuevo": [F("zona_id", "long", opt=True, nil=True), F("fecha", "date", opt=True, nil=True), F("lineas", ["TPreLineaNueva"], item="linea")],
    "TPreCalculoLinea": [F("producto_id", "long"), F("cantidad", "int", min=1), F("precio_unitario", "money"), F("descuento_unitario", "money"),
                         F("importe", "money"), F("promocion_id", "long", nil=True), F("bajo_margen", "bool")],
    "TPreCalculo": [F("zona_id", "long", nil=True), F("fecha", "date"), F("lineas", ["TPreCalculoLinea"], item="linea"),
                    F("subtotal", "money"), F("descuento_total", "money"), F("total", "money")],
    "TPrePromocion": [F("id", "long"), F("nombre", "string"), F("tipo", "string", enum=["porcentaje", "monto"]), F("valor", "money"),
                      F("producto_id", "long", nil=True), F("categoria_id", "long", nil=True), F("zona_id", "long", nil=True),
                      F("vigente_desde", "date"), F("vigente_hasta", "date"), F("estatus", "string", enum=["activo", "inactivo"])],
    "TPrePromocionLista": L("TPrePromocion", "promocion"),
    "TPrePromocionNueva": [F("nombre", "string", minlen=3, max=80), F("tipo", "string", enum=["porcentaje", "monto"]), F("valor", "money", min="0.01"),
                           F("producto_id", "long", opt=True, nil=True), F("categoria_id", "long", opt=True, nil=True),
                           F("zona_id", "long", opt=True, nil=True), F("vigente_desde", "date", opt=True, nil=True), F("vigente_hasta", "date")],
    "TPreCambio": [F("id", "long"), F("lista_id", "long"), F("producto_id", "long"), F("precio_anterior", "money", nil=True),
                   F("precio_nuevo", "money"), F("usuario_id", "long", nil=True), F("fecha", "dateTime")],
    "TPreHistorialLista": L("TPreCambio", "cambio"),
    "TPreMargen": [F("lista", "TRefNombre"), F("producto", "TRefNombre"), F("precio", "money"), F("costo", "money"), F("margen_pct", "num"),
                   F("bajo_margen", "bool")],
    "TPreMargenLista": L("TPreMargen", "margen"),
    "TPreEscenario": [F("variacion_pct", "int"), F("precio", "money"), F("volumen_estimado", "num"), F("ingreso", "money"),
                      F("ingreso_vs_base_pct", "num"), F("margen_total", "money", nil=True), F("volumen_para_igualar_margen", "num", nil=True)],
    "TPreSensibilidad": [F("producto_id", "long"), F("zona_id", "long", nil=True), F("precio_final", "money"), F("costo", "money", nil=True),
                         F("volumen_base", "int"), F("elasticidad", "num"), F("supuestos", "string"), F("escenarios", ["TPreEscenario"], item="escenario")],
}
PRECIOS_RAICES = {"listas": "TPreListaLista", "lista_detalle": "TPreListaDetalle", "lista_nueva": "TPreListaNueva",
                  "precio_nuevo": "TPrePrecioNuevo", "item_precio": "TPreItem", "precio_vigente": "TPrePrecioVigente",
                  "calculo_nuevo": "TPreCalculoNuevo", "calculo": "TPreCalculo", "promociones": "TPrePromocionLista",
                  "promocion": "TPrePromocion", "promocion_nueva": "TPrePromocionNueva", "historial_precios": "TPreHistorialLista",
                  "margenes": "TPreMargenLista", "sensibilidad": "TPreSensibilidad"}

LISTA = {"id": 2, "nombre": "Lista San Bernabé Centro", "zona_id": 1, "vigente_desde": "2026-10-01", "vigente_hasta": None, "estatus": "activo", "productos": 20}
ITEM_PRECIO = {"producto": PROD, "precio": 46.35, "costo": 31.5, "margen_pct": 32.0, "actualizado_en": FECHA}
PROMO = {"id": 1, "nombre": "Bebidas -10 %", "tipo": "porcentaje", "valor": 10.0, "producto_id": None, "categoria_id": 2, "zona_id": None,
         "vigente_desde": "2026-10-01", "vigente_hasta": "2027-09-30", "estatus": "activo"}
PRECIO_VIGENTE = {"producto_id": 4, "zona_id": 1, "fecha": "2026-10-19", "precio_base": 45.0, "lista": {"id": 2, "nombre": "Lista San Bernabé Centro"},
                  "precio_vigente": 46.35, "promocion": {"id": 3, "nombre": "Aceite -5 %", "tipo": "porcentaje", "valor": 5.0},
                  "descuento": 2.32, "descuento_limitado": False, "precio_final": 44.03, "costo": 31.5, "margen_pct": 28.5, "bajo_margen": False}

PRECIOS_EJEMPLOS = {
    "ListaLista": ("listas", {"datos": [LISTA], "paginacion": PAG}),
    "ListaNueva": ("lista_nueva", {"nombre": "Lista Valles", "zona_id": 2, "vigente_desde": "2026-11-01", "vigente_hasta": "2027-03-31",
                                   "items": [{"producto_id": 4, "precio": 46.0, "costo": 31.5}]}),
    "ListaDetalle": ("lista_detalle", {**LISTA, "items": [ITEM_PRECIO]}),
    "PrecioNuevo": ("precio_nuevo", {"precio": 46.35, "costo": 31.5}),
    "ItemPrecio": ("item_precio", ITEM_PRECIO),
    "PrecioVigente": ("precio_vigente", PRECIO_VIGENTE),
    "CalculoNuevo": ("calculo_nuevo", {"zona_id": 1, "fecha": "2026-10-19", "lineas": [{"producto_id": 4, "cantidad": 2}, {"producto_id": 12, "cantidad": 1}]}),
    "Calculo": ("calculo", {"zona_id": 1, "fecha": "2026-10-19",
                            "lineas": [{"producto_id": 4, "cantidad": 2, "precio_unitario": 44.03, "descuento_unitario": 2.32, "importe": 88.06,
                                        "promocion_id": 3, "bajo_margen": False}],
                            "subtotal": 92.7, "descuento_total": 4.64, "total": 88.06}),
    "PromocionLista": ("promociones", {"datos": [PROMO], "paginacion": PAG}),
    "PromocionNueva": ("promocion_nueva", {"nombre": "Aceite -5 %", "tipo": "porcentaje", "valor": 5.0, "producto_id": 4, "zona_id": 1,
                                           "vigente_desde": "2026-10-19", "vigente_hasta": "2026-11-30"}),
    "Promocion": ("promocion", PROMO),
    "HistorialLista": ("historial_precios", {"datos": [{"id": 8, "lista_id": 2, "producto_id": 4, "precio_anterior": 45.9, "precio_nuevo": 46.35,
                                                        "usuario_id": 1, "fecha": FECHA}], "paginacion": PAG}),
    "MargenLista": ("margenes", {"datos": [{"lista": {"id": 2, "nombre": "Lista San Bernabé Centro"}, "producto": PROD, "precio": 46.35, "costo": 31.5,
                                            "margen_pct": 32.0, "bajo_margen": False}], "paginacion": PAG}),
    "Sensibilidad": ("sensibilidad", {"producto_id": 4, "zona_id": 1, "precio_final": 44.03, "costo": 31.5, "volumen_base": 100, "elasticidad": -1.2,
                                      "supuestos": "La elasticidad es un supuesto, no una medición: indica cuánto cambia el volumen por cada 1 % que cambia el precio.",
                                      "escenarios": [{"variacion_pct": 10, "precio": 48.43, "volumen_estimado": 88.0, "ingreso": 4261.84,
                                                      "ingreso_vs_base_pct": -3.2, "margen_total": 1494.24, "volumen_para_igualar_margen": 74.2}]}),
}

# --------------------------------------------------------------------
# Proveedores
# --------------------------------------------------------------------
PROVEEDORES = {
    "TPrvProveedor": [F("id", "long"), F("clave", "string"), F("nombre", "string"), F("contacto", "string", nil=True), F("correo", "string", nil=True),
                      F("telefono", "string", nil=True), F("dias_entrega", "int", min=0, maxv=60), F("pedido_minimo", "money", min=0),
                      F("condiciones_pago", "string", nil=True), F("estatus", "string", enum=["activo", "inactivo"]), F("zonas", ["long"], item="zona_id"),
                      F("calificacion", "num", nil=True), F("evaluaciones", "int", min=0)],
    "TPrvProveedorLista": L("TPrvProveedor", "proveedor"),
    "TPrvProveedorNuevo": [F("clave", "string", minlen=2, max=20), F("nombre", "string", minlen=3, max=120), F("contacto", "string", opt=True, nil=True, max=120),
                           F("correo", "string", opt=True, nil=True, max=160), F("telefono", "string", opt=True, nil=True, max=20),
                           F("dias_entrega", "int", opt=True, min=0, maxv=60), F("pedido_minimo", "money", opt=True, min=0),
                           F("condiciones_pago", "string", opt=True, nil=True, max=120), F("zonas", ["long"], opt=True, item="zona_id")],
    "TPrvProveedorCambio": [F("clave", "string", opt=True, minlen=2, max=20), F("nombre", "string", opt=True, minlen=3, max=120),
                            F("contacto", "string", opt=True, nil=True, max=120), F("correo", "string", opt=True, nil=True, max=160),
                            F("telefono", "string", opt=True, nil=True, max=20), F("dias_entrega", "int", opt=True, min=0, maxv=60),
                            F("pedido_minimo", "money", opt=True, min=0), F("condiciones_pago", "string", opt=True, nil=True, max=120),
                            F("zonas", ["long"], opt=True, item="zona_id")],
    "TPrvItemCatalogo": [F("producto", "TRefNombre"), F("precio_compra", "money"), F("unidad_compra", "string"), F("capacidad_semanal", "int", min=1),
                         F("minimo_compra", "int", min=1), F("vigente_hasta", "date", nil=True)],
    "TPrvCatalogoLista": L("TPrvItemCatalogo", "item"),
    "TPrvOfertaNueva": [F("precio_compra", "money", min="0.01"), F("unidad_compra", "string", opt=True, minlen=1, max=20),
                        F("capacidad_semanal", "int", min=1), F("minimo_compra", "int", opt=True, min=1), F("vigente_hasta", "date", opt=True, nil=True)],
    "TPrvProveedorRef": [F("id", "long"), F("clave", "string"), F("nombre", "string")],
    "TPrvOferta": [F("proveedor", "TPrvProveedorRef"), F("producto", "TRefNombre"), F("precio_compra", "money"), F("unidad_compra", "string"),
                   F("capacidad_semanal", "int", min=1), F("minimo_compra", "int", min=1), F("dias_entrega", "int", min=0), F("pedido_minimo", "money", min=0),
                   F("vigente_hasta", "date", nil=True), F("calificacion", "num", nil=True)],
    "TPrvOfertaLista": L("TPrvOferta", "oferta"),
    "TPrvEvaluacion": [F("id", "long"), F("proveedor_id", "long"), F("puntualidad", "int", min=1, maxv=5), F("calidad", "int", min=1, maxv=5),
                       F("precio", "int", min=1, maxv=5), F("comentario", "string", nil=True), F("evaluado_por", "long", nil=True), F("evaluado_en", "dateTime")],
    "TPrvPromedio": [F("puntualidad", "num"), F("calidad", "num"), F("precio", "num"), F("general", "num")],
    "TPrvEvaluacionLista": [F("datos", ["TPrvEvaluacion"], item="evaluacion"), F("promedio", "TPrvPromedio", nil=True), F("paginacion", "TPaginacion")],
    "TPrvEvaluacionNueva": [F("puntualidad", "int", min=1, maxv=5), F("calidad", "int", min=1, maxv=5), F("precio", "int", min=1, maxv=5),
                            F("comentario", "string", opt=True, nil=True, max=300)],
}
PROVEEDORES_RAICES = {"proveedores": "TPrvProveedorLista", "proveedor": "TPrvProveedor", "proveedor_nuevo": "TPrvProveedorNuevo",
                      "proveedor_cambio": "TPrvProveedorCambio", "catalogo": "TPrvCatalogoLista", "item_catalogo": "TPrvItemCatalogo",
                      "oferta_nueva": "TPrvOfertaNueva", "ofertas": "TPrvOfertaLista", "evaluaciones": "TPrvEvaluacionLista",
                      "evaluacion": "TPrvEvaluacion", "evaluacion_nueva": "TPrvEvaluacionNueva"}

PROVEEDOR = {"id": 2, "clave": "PV-02", "nombre": "Distribuidora Regia", "contacto": "Luis Treviño", "correo": "pedidos@distregia.example",
             "telefono": "8181000102", "dias_entrega": 1, "pedido_minimo": 500.0, "condiciones_pago": "Crédito a 7 días", "estatus": "activo",
             "zonas": [1, 2, 3, 4], "calificacion": 4.0, "evaluaciones": 1}
ITEM_CATALOGO = {"producto": PROD, "precio_compra": 33.3, "unidad_compra": "pieza", "capacidad_semanal": 200, "minimo_compra": 12, "vigente_hasta": None}
EVALUACION = {"id": 3, "proveedor_id": 2, "puntualidad": 5, "calidad": 4, "precio": 3, "comentario": "Muy puntual; precio algo alto.", "evaluado_por": 2,
              "evaluado_en": FECHA}

PROVEEDORES_EJEMPLOS = {
    "ProveedorLista": ("proveedores", {"datos": [PROVEEDOR], "paginacion": PAG}),
    "ProveedorNuevo": ("proveedor_nuevo", {"clave": "PV-04", "nombre": "Frutas y Verduras del Valle", "contacto": "Ana Salinas", "correo": "ventas@fvvalle.example",
                                           "telefono": "8181000104", "dias_entrega": 1, "pedido_minimo": 400.0, "condiciones_pago": "Contado", "zonas": [1, 2]}),
    "ProveedorCambio": ("proveedor_cambio", {"dias_entrega": 2, "zonas": [1, 2, 3]}),
    "Proveedor": ("proveedor", PROVEEDOR),
    "CatalogoLista": ("catalogo", {"datos": [ITEM_CATALOGO], "paginacion": PAG}),
    "OfertaNueva": ("oferta_nueva", {"precio_compra": 33.3, "unidad_compra": "pieza", "capacidad_semanal": 200, "minimo_compra": 12, "vigente_hasta": "2027-03-31"}),
    "ItemCatalogo": ("item_catalogo", ITEM_CATALOGO),
    "OfertaLista": ("ofertas", {"datos": [{"proveedor": {"id": 2, "clave": "PV-02", "nombre": "Distribuidora Regia"}, "producto": PROD,
                                           "precio_compra": 33.3, "unidad_compra": "pieza", "capacidad_semanal": 200, "minimo_compra": 12,
                                           "dias_entrega": 1, "pedido_minimo": 500.0, "vigente_hasta": None, "calificacion": 4.0}], "paginacion": PAG}),
    "EvaluacionLista": ("evaluaciones", {"datos": [EVALUACION], "promedio": {"puntualidad": 5.0, "calidad": 4.0, "precio": 3.0, "general": 4.0},
                                         "paginacion": PAG}),
    "EvaluacionNueva": ("evaluacion_nueva", {"puntualidad": 5, "calidad": 4, "precio": 3, "comentario": "Muy puntual; precio algo alto."}),
    "Evaluacion": ("evaluacion", EVALUACION),
}

# --------------------------------------------------------------------
# Abastecimiento
# --------------------------------------------------------------------
ESTADOS_SOL = ["pendiente", "aprobada", "rechazada", "ordenada"]
ESTADOS_ORD = ["emitida", "parcial", "recibida", "cancelada"]
ABASTECIMIENTO = {
    "TAbaOferta": [F("proveedor", "TRefNombre"), F("precio_compra", "money"), F("dias_entrega", "int", min=0), F("capacidad_semanal", "int", min=1),
                   F("minimo_compra", "int", min=1)],
    "TAbaNecesidad": [F("producto", "TRefNombre"), F("existencia", "int"), F("minimo", "int"), F("disponible", "int"), F("en_camino", "int", min=0),
                      F("solicitado", "int", min=0), F("cantidad_sugerida", "int", min=1), F("cantidad_a_comprar", "int", min=1),
                      F("mejor_oferta", "TAbaOferta", nil=True), F("costo_estimado", "money", nil=True)],
    "TAbaNecesidadLista": [F("microhub_id", "long"), F("factor_objetivo", "num"), F("datos", ["TAbaNecesidad"], item="necesidad"),
                           F("paginacion", "TPaginacion")],
    "TAbaLineaSolicitud": [F("producto", "TRefNombre"), F("cantidad", "int", min=1)],
    "TAbaSolicitud": [F("id", "long"), F("folio", "string"), F("microhub_id", "long"), F("estado", "string", enum=ESTADOS_SOL), F("motivo", "string", nil=True),
                      F("solicitada_por", "long", nil=True), F("decidida_por", "long", nil=True), F("decision_motivo", "string", nil=True),
                      F("decidida_en", "dateTime", nil=True), F("creada_en", "dateTime"), F("lineas", ["TAbaLineaSolicitud"], item="linea")],
    "TAbaSolicitudLista": L("TAbaSolicitud", "solicitud"),
    "TAbaLineaNueva": [F("producto_id", "long"), F("cantidad", "int", min=1, maxv=100000)],
    "TAbaSolicitudNueva": [F("microhub_id", "long"), F("motivo", "string", opt=True, nil=True, max=300), F("lineas", ["TAbaLineaNueva"], item="linea")],
    "TAbaDecision": [F("decision", "string", enum=["aprobada", "rechazada"]), F("motivo", "string", opt=True, nil=True, max=300)],
    "TAbaOrdenarNuevo": [F("proveedor_id", "long", opt=True, nil=True)],
    "TAbaLineaOrden": [F("producto", "TRefNombre"), F("cantidad", "int", min=1), F("precio_compra", "money"), F("cantidad_recibida", "int", min=0),
                       F("pendiente_inventario", "int", min=0)],
    "TAbaOrden": [F("id", "long"), F("folio", "string"), F("solicitud_id", "long", nil=True), F("proveedor", "TRefNombre"), F("microhub_id", "long"),
                  F("estado", "string", enum=ESTADOS_ORD), F("fecha_esperada", "date"), F("total", "money"), F("creada_en", "dateTime"),
                  F("cerrada_en", "dateTime", nil=True), F("lineas", ["TAbaLineaOrden"], item="linea")],
    "TAbaOrdenLista": L("TAbaOrden", "orden"),
    "TAbaOrdenesGeneradas": [F("solicitud_id", "long"), F("ordenes", ["TAbaOrden"], item="orden")],
    "TAbaLineaRecepcion": [F("producto_id", "long"), F("cantidad", "int", min=1, maxv=100000)],
    "TAbaRecepcionNueva": [F("operacion_uuid", "string", opt=True, nil=True, max=60, minlen=8), F("nota", "string", opt=True, nil=True, max=300),
                           F("lineas", ["TAbaLineaRecepcion"], opt=True, item="linea")],
    "TAbaRecepcion": [F("orden", "TAbaOrden"), F("aplicadas", "int", min=0), F("pendientes", "int", min=0), F("aviso", "string", nil=True)],
    "TAbaCancelacion": [F("motivo", "string", minlen=3, max=300)],
    "TAbaConteoSolicitudes": [F("pendiente", "int", min=0), F("aprobada", "int", min=0), F("rechazada", "int", min=0), F("ordenada", "int", min=0)],
    "TAbaConteoOrdenes": [F("emitida", "int", min=0), F("parcial", "int", min=0), F("recibida", "int", min=0), F("cancelada", "int", min=0)],
    "TAbaSeguimiento": [F("microhub_id", "long", nil=True), F("solicitudes", "TAbaConteoSolicitudes"), F("ordenes", "TAbaConteoOrdenes"),
                        F("atrasadas", "int", min=0), F("pendientes_inventario", "int", min=0), F("proxima_entrega", "date", nil=True)],
}
ABASTECIMIENTO_RAICES = {"necesidades": "TAbaNecesidadLista", "solicitudes": "TAbaSolicitudLista", "solicitud": "TAbaSolicitud",
                         "solicitud_nueva": "TAbaSolicitudNueva", "decision_compra": "TAbaDecision", "ordenar_nuevo": "TAbaOrdenarNuevo",
                         "ordenes_generadas": "TAbaOrdenesGeneradas", "ordenes": "TAbaOrdenLista", "orden": "TAbaOrden",
                         "recepcion_nueva": "TAbaRecepcionNueva", "recepcion": "TAbaRecepcion", "cancelacion_nueva": "TAbaCancelacion",
                         "seguimiento_abastecimiento": "TAbaSeguimiento"}

SOLICITUD = {"id": 5, "folio": "SC-20261019-000005", "microhub_id": 1, "estado": "pendiente", "motivo": "Se acabó el aceite el fin de semana",
             "solicitada_por": 2, "decidida_por": None, "decision_motivo": None, "decidida_en": None, "creada_en": FECHA,
             "lineas": [{"producto": PROD, "cantidad": 24}]}
ORDEN = {"id": 7, "folio": "OC-20261019-000007", "solicitud_id": 5, "proveedor": {"id": 2, "nombre": "Distribuidora Regia"}, "microhub_id": 1,
         "estado": "emitida", "fecha_esperada": "2026-10-20", "total": 799.2, "creada_en": FECHA, "cerrada_en": None,
         "lineas": [{"producto": PROD, "cantidad": 24, "precio_compra": 33.3, "cantidad_recibida": 0, "pendiente_inventario": 0}]}

ABASTECIMIENTO_EJEMPLOS = {
    "NecesidadLista": ("necesidades", {"microhub_id": 1, "factor_objetivo": 3.0,
                                       "datos": [{"producto": PROD, "existencia": 4, "minimo": 10, "disponible": 4, "en_camino": 0, "solicitado": 0,
                                                  "cantidad_sugerida": 26, "cantidad_a_comprar": 26,
                                                  "mejor_oferta": {"proveedor": {"id": 2, "nombre": "Distribuidora Regia"}, "precio_compra": 33.3,
                                                                   "dias_entrega": 1, "capacidad_semanal": 200, "minimo_compra": 12},
                                                  "costo_estimado": 865.8}], "paginacion": PAG}),
    "SolicitudCompraLista": ("solicitudes", {"datos": [SOLICITUD], "paginacion": PAG}),
    "SolicitudCompraNueva": ("solicitud_nueva", {"microhub_id": 1, "motivo": "Se acabó el aceite el fin de semana",
                                                 "lineas": [{"producto_id": 4, "cantidad": 24}]}),
    "SolicitudCompra": ("solicitud", SOLICITUD),
    "DecisionCompra": ("decision_compra", {"decision": "aprobada", "motivo": "Hay presupuesto de octubre"}),
    "OrdenarNuevo": ("ordenar_nuevo", {"proveedor_id": 2}),
    "OrdenesGeneradas": ("ordenes_generadas", {"solicitud_id": 5, "ordenes": [ORDEN]}),
    "OrdenCompraLista": ("ordenes", {"datos": [ORDEN], "paginacion": PAG}),
    "OrdenCompra": ("orden", ORDEN),
    "RecepcionNueva": ("recepcion_nueva", {"operacion_uuid": "9b3c2d10-55aa-4e1b-8f6c-1d2e3f405162", "nota": "Llegó completo",
                                           "lineas": [{"producto_id": 4, "cantidad": 24}]}),
    "RecepcionResultado": ("recepcion", {"orden": {**ORDEN, "estado": "recibida", "cerrada_en": FECHA,
                                                   "lineas": [{"producto": PROD, "cantidad": 24, "precio_compra": 33.3, "cantidad_recibida": 24,
                                                               "pendiente_inventario": 0}]},
                                         "aplicadas": 1, "pendientes": 0, "aviso": None}),
    "CancelacionNueva": ("cancelacion_nueva", {"motivo": "El proveedor ya no surte este producto"}),
    "SeguimientoAbastecimiento": ("seguimiento_abastecimiento", {"microhub_id": 1, "solicitudes": {"pendiente": 1, "aprobada": 0, "rechazada": 0, "ordenada": 2},
                                                                 "ordenes": {"emitida": 1, "parcial": 0, "recibida": 1, "cancelada": 0}, "atrasadas": 0,
                                                                 "pendientes_inventario": 0, "proxima_entrega": "2026-10-20"}),
}

# --------------------------------------------------------------------
# Notificaciones (sustituye al contrato anterior: más tipos y referencias, envío por rol, preferencias)
# --------------------------------------------------------------------
NOTIFICACIONES = {
    "TNotificacionReferencia": [F("tipo", "string", enum=NOTIF_REFS), F("id", "string")],
    "TNotificacion": [F("id", "long"), F("tipo", "string", enum=NOTIF_TIPOS), F("titulo", "string"), F("mensaje", "string"), F("leida", "bool"),
                      F("referencia", "TNotificacionReferencia", nil=True), F("creada_en", "dateTime")],
    "TNotificacionLista": L("TNotificacion", "notificacion"),
    "TConteo": [F("no_leidas", "long", min=0)],
    "TNotificacionNueva": [F("usuario_id", "long", opt=True), F("rol", "string", opt=True, max=40), F("microhub_id", "long", opt=True),
                           F("tipo", "string", enum=NOTIF_TIPOS), F("titulo", "string", max=120), F("mensaje", "string", max=400),
                           F("referencia", "TNotificacionReferencia", opt=True)],
    "TNotEnvio": [F("enviadas", "int", min=0), F("omitidas", "int", min=0), F("ids", ["long"], item="id")],
    "TNotLectura": [F("marcadas", "int", min=0)],
    "TNotPreferencia": [F("tipo", "string", enum=PREF_TIPOS), F("activa", "bool")],
    "TNotPreferencias": [F("datos", ["TNotPreferencia"], item="preferencia")],
    "TNotPreferenciaNueva": [F("activa", "bool")],
}
NOTIFICACIONES_RAICES = {"notificacion": "TNotificacion", "notificaciones": "TNotificacionLista", "conteo": "TConteo", "envio": "TNotEnvio",
                         "lectura": "TNotLectura", "preferencias": "TNotPreferencias", "preferencia": "TNotPreferencia",
                         "preferencia_nueva": "TNotPreferenciaNueva"}
NOTIFICACIONES_EJEMPLOS = {
    "Envio": ("envio", {"enviadas": 2, "omitidas": 1, "ids": [311, 312]}),
    "Lectura": ("lectura", {"marcadas": 4}),
    "Preferencias": ("preferencias", {"datos": [{"tipo": t, "activa": t != "planeacion"} for t in PREF_TIPOS]}),
    "PreferenciaNueva": ("preferencia_nueva", {"activa": False}),
    "Preferencia": ("preferencia", {"tipo": "inventario", "activa": False}),
}

# --------------------------------------------------------------------
ARCHIVOS = {
    "comun_ola1": {"titulo": "servicio: comun (referencias de la Ola 1)", "incluye": ["comun"], "tipos": COMUN, "raices": {}},
    "inventario": {"titulo": "servicio: inventario", "incluye": ["comun", "comun_ola1"], "tipos": INVENTARIO, "raices": INVENTARIO_RAICES},
    "precios": {"titulo": "servicio: precios", "incluye": ["comun", "comun_ola1"], "tipos": PRECIOS, "raices": PRECIOS_RAICES},
    "proveedores": {"titulo": "servicio: proveedores", "incluye": ["comun", "comun_ola1"], "tipos": PROVEEDORES, "raices": PROVEEDORES_RAICES},
    "abastecimiento": {"titulo": "servicio: abastecimiento", "incluye": ["comun", "comun_ola1"], "tipos": ABASTECIMIENTO, "raices": ABASTECIMIENTO_RAICES},
    "notificaciones": {"titulo": "servicio: notificaciones", "incluye": ["comun"], "tipos": NOTIFICACIONES, "raices": NOTIFICACIONES_RAICES},
}
EJEMPLOS = {**INVENTARIO_EJEMPLOS, **PRECIOS_EJEMPLOS, **PROVEEDORES_EJEMPLOS, **ABASTECIMIENTO_EJEMPLOS, **NOTIFICACIONES_EJEMPLOS}
