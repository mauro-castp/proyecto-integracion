"""
ola5.py — Contrato v1 de lo que se agregó al cerrar la entrega final: operación desde el escritorio (cambiar el estado de un pedido y
asignar paradas a repartidores en XML), la confirmación de recepción del cliente y la teoría de colas M/M/1 y M/M/c del servicio de
capacidad.

Los servicios ya aceptaban esas operaciones en JSON; aquí se declara su forma XML para que el cliente de escritorio (solo XML) las use.
El orden de los campos es el orden en que el XML de entrada debe traerlos (xs:sequence). Regenerar:  cd servicios && python contratos/generar.py ola5
"""
from generar import F

ESTADOS_MANUALES = ["creado", "pendiente_asignacion", "asignado", "en_preparacion", "en_ruta", "cancelado"]   # los cierres van por entregas

OPERACION = {
    "TOpPedidoEstado": [F("estado", "string", enum=ESTADOS_MANUALES), F("motivo", "string", opt=True, nil=True, max=300)],
    "TOpParada": [F("pedido_id", "long", min=1), F("repartidor_id", "long", min=1), F("orden_parada", "int", min=1, maxv=200),
                  F("distancia_km", "num", opt=True, nil=True, min=0), F("minutos_estimados", "num", opt=True, nil=True, min=0),
                  F("costo_entrega_estimado", "num", opt=True, nil=True, min=0), F("plan_ruta_id", "long", opt=True, nil=True, min=1)],
    "TOpAsignacionNueva": [F("paradas", ["TOpParada"], item="parada")],
    "TOpAsignada": [F("entrega_id", "long"), F("pedido_id", "long"), F("repartidor_id", "long"), F("orden_parada", "int")],
    "TOpAsignacion": [F("asignadas", "int"), F("entregas", ["TOpAsignada"], item="entrega")],
    "TOpRecepcionNueva": [F("pedido_id", "long", min=1), F("conforme", "bool")],
    "TOpRecepcion": [F("pedido_id", "long"), F("folio", "string"), F("entrega_id", "long"), F("resultado", "string", nil=True),
                     F("conforme", "bool"), F("estado_pedido", "string")],
}
COLAS = {
    "TColaCalculoNuevo": [F("microhub_id", "long", opt=True, nil=True, min=1), F("llegadas_hora", "num", opt=True, nil=True, min=0),
                          F("servicio_hora", "num", opt=True, nil=True, min=0), F("servidores", "int", opt=True, nil=True, min=1, maxv=50),
                          F("espera_objetivo_min", "num", opt=True, nil=True, min=0, maxv=600)],
    "TColaMicrohub": [F("id", "long"), F("nombre", "string", nil=True)],
    "TColaFila": [F("servidores", "int"), F("utilizacion_pct", "num"), F("prob_esperar", "num"), F("lq", "num", nil=True),
                  F("wq_min", "num", nil=True), F("w_min", "num", nil=True), F("cumple", "bool")],
    "TColaCalculo": [F("microhub", "TColaMicrohub", nil=True), F("modelo", "string", enum=["M/M/1", "M/M/c"]), F("llegadas_hora", "num"),
                     F("servicio_hora", "num"), F("servidores", "int"), F("carga_ofrecida", "num"), F("utilizacion_pct", "num"),
                     F("estable", "bool"), F("p0", "num", nil=True), F("prob_esperar", "num"), F("lq", "num", nil=True), F("l", "num", nil=True),
                     F("wq_min", "num", nil=True), F("w_min", "num", nil=True), F("espera_objetivo_min", "num"),
                     F("servidores_requeridos", "int", nil=True), F("origen", "string", enum=["indicado", "microhub"]),
                     F("filas", ["TColaFila"], item="fila"), F("nota", "string")],
}
ARCHIVOS = {
    "operacion": {"titulo": "operación desde el escritorio (estado de pedidos, asignación de paradas) y recepción del cliente",
                  "incluye": ["comun"], "tipos": OPERACION,
                  "raices": {"pedido_estado_cambio": "TOpPedidoEstado", "asignacion_nueva": "TOpAsignacionNueva", "asignacion": "TOpAsignacion",
                             "recepcion_cliente_nueva": "TOpRecepcionNueva", "recepcion_cliente": "TOpRecepcion"}},
    "colas": {"titulo": "teoría de colas M/M/1 y M/M/c (servicio de capacidad)", "incluye": ["comun"], "tipos": COLAS,
              "raices": {"cola_calculo_nuevo": "TColaCalculoNuevo", "cola_calculo": "TColaCalculo"}},
}

FILAS = [{"servidores": 3, "utilizacion_pct": 83.33, "prob_esperar": 0.702247, "lq": 3.5112, "wq_min": 21.067, "w_min": 36.067, "cumple": False},
         {"servidores": 4, "utilizacion_pct": 62.5, "prob_esperar": 0.319857, "lq": 0.5331, "wq_min": 3.199, "w_min": 18.199, "cumple": True}]
EJEMPLOS = {
    "PedidoEstadoCambio": ("pedido_estado_cambio", {"estado": "en_preparacion", "motivo": None}),
    "AsignacionNueva": ("asignacion_nueva", {"paradas": [{"pedido_id": 901, "repartidor_id": 7, "orden_parada": 1, "distancia_km": 1.2},
                                                         {"pedido_id": 902, "repartidor_id": 7, "orden_parada": 2}]}),
    "Asignacion": ("asignacion", {"asignadas": 2, "entregas": [{"entrega_id": 412, "pedido_id": 901, "repartidor_id": 7, "orden_parada": 1},
                                                               {"entrega_id": 413, "pedido_id": 902, "repartidor_id": 7, "orden_parada": 2}]}),
    "RecepcionClienteNueva": ("recepcion_cliente_nueva", {"pedido_id": 901, "conforme": True}),
    "RecepcionCliente": ("recepcion_cliente", {"pedido_id": 901, "folio": "PED-20261126-000901", "entrega_id": 412, "resultado": "entregado", "conforme": True,
                                "estado_pedido": "entregado"}),
    "ColaCalculoNuevo": ("cola_calculo_nuevo", {"microhub_id": None, "llegadas_hora": 10, "servicio_hora": 4, "servidores": 3, "espera_objetivo_min": 5}),
    "ColaCalculo": ("cola_calculo", {"microhub": None, "modelo": "M/M/c", "llegadas_hora": 10, "servicio_hora": 4, "servidores": 3,
                                     "carga_ofrecida": 2.5, "utilizacion_pct": 83.33, "estable": True, "p0": 0.044944, "prob_esperar": 0.702247,
                                     "lq": 3.5112, "l": 6.0112, "wq_min": 21.067, "w_min": 36.067, "espera_objetivo_min": 5,
                                     "servidores_requeridos": 4, "origen": "indicado", "filas": FILAS,
                                     "nota": "Con 3 operadores la espera promedio en fila es de 21.1 min; con 4 baja a 3.2 min."}),
}
