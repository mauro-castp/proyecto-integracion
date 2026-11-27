"""
ola4.py — Contrato v1 de las altas, cambios y bajas de la entrega final: productos, zonas, microhubs y usuarios, el alta de pedidos y la
asignación de entregas. Las respuestas de catálogo y de usuarios son las que ya existían.

El orden de los campos es el orden en que el XML de entrada debe traerlos (xs:sequence). Regenerar:  cd servicios && python contratos/generar.py ola4
"""
from generar import F

ROLES = ["administrador", "operador", "planeador", "cliente", "repartidor", "auditor", "analista", "supervisor", "proveedor"]
ESTATUS = ["activo", "inactivo"]


def opcionales(campos):
    return [{**c, "opt": True} for c in campos]


PRODUCTO = [F("clave_interna", "string", max=30, minlen=1), F("nombre", "string", max=160, minlen=1), F("categoria_id", "long", min=1),
            F("unidad", "string", max=20, minlen=1), F("presentacion", "string", opt=True, nil=True, max=60), F("precio", "money", min=0),
            F("imagen_url", "string", opt=True, nil=True, max=300)]
ZONA = [F("clave", "string", max=20, minlen=1), F("nombre", "string", max=120, minlen=1), F("colonia", "string", max=120, minlen=1),
        F("codigo_postal", "string", max=5, minlen=5), F("latitud", "num", min=-90, maxv=90), F("longitud", "num", min=-180, maxv=180),
        F("ticket_minimo", "num", opt=True, nil=True, min=0), F("costo_envio", "num", opt=True, nil=True, min=0)]
MICROHUB = [F("clave", "string", max=20, minlen=1), F("nombre", "string", max=120, minlen=1), F("direccion", "string", max=200, minlen=3),
            F("latitud", "num", min=20, maxv=33), F("longitud", "num", min=-118, maxv=-86), F("radio_km", "num", opt=True, nil=True, min=0.1, maxv=50),
            F("capacidad_turno", "int", opt=True, nil=True, min=1), F("hora_apertura", "string", opt=True, max=5, minlen=5),
            F("hora_cierre", "string", opt=True, max=5, minlen=5)]
CUENTA = [F("nombre", "string", max=80, minlen=1), F("apellidos", "string", max=120, minlen=1), F("telefono", "string", opt=True, nil=True, max=10, minlen=10),
          F("rol", "string", enum=ROLES), F("microhub_id", "long", opt=True, nil=True, min=1)]

ADMIN = {
    "TAdmProductoNuevo": PRODUCTO,
    "TAdmProductoCambio": opcionales(PRODUCTO) + [F("estatus", "string", opt=True, enum=ESTATUS)],
    "TAdmZonaNueva": ZONA,
    "TAdmZonaCambio": opcionales(ZONA) + [F("estatus", "string", opt=True, enum=ESTATUS)],
    "TAdmMicrohubNuevo": MICROHUB,
    "TAdmMicrohubCambio": opcionales(MICROHUB) + [F("estatus", "string", opt=True, enum=ESTATUS)],
    "TAdmUsuarioNuevo": CUENTA + [F("correo", "string", max=160, minlen=6), F("clave", "string", max=72, minlen=10)],
    "TAdmUsuarioCambio": opcionales(CUENTA) + [F("estatus", "string", opt=True, enum=["activo", "bloqueado"])],
    "TAdmLinea": [F("producto_id", "long", min=1), F("cantidad", "int", min=1, maxv=1000)],
    "TAdmPedidoNuevo": [F("cliente_id", "long", opt=True, nil=True, min=1), F("domicilio_id", "long", opt=True, nil=True, min=1),
                        F("lineas", ["TAdmLinea"], item="linea"), F("operacion_uuid", "string", opt=True, nil=True, max=36, minlen=36)],
    "TAdmPedidoCreado": [F("id", "long"), F("folio", "string"), F("estado", "string"), F("zona_id", "long"), F("microhub_id", "long", nil=True),
                         F("subtotal", "money"), F("costo_envio", "money"), F("total", "money"), F("asignado", "bool"), F("motivo", "string", nil=True),
                         F("duplicado", "bool")],
    "TAdmPedidoListo": [F("id", "long"), F("estado", "string"), F("listo_en", "dateTime")],
    "TAdmEntregaNueva": [F("pedido_id", "long", min=1), F("repartidor_id", "long", min=1), F("orden_parada", "int", opt=True, nil=True, min=1, maxv=500)],
    "TAdmEntregaCreada": [F("entrega_id", "long"), F("pedido_id", "long"), F("repartidor_id", "long"), F("estado_pedido", "string")],
}
RAICES = {"producto_nuevo": "TAdmProductoNuevo", "producto_cambio": "TAdmProductoCambio", "zona_nueva": "TAdmZonaNueva", "zona_cambio": "TAdmZonaCambio",
          "microhub_nuevo": "TAdmMicrohubNuevo", "microhub_cambio": "TAdmMicrohubCambio", "usuario_nuevo": "TAdmUsuarioNuevo",
          "usuario_cambio": "TAdmUsuarioCambio", "pedido_nuevo": "TAdmPedidoNuevo", "pedido_creado": "TAdmPedidoCreado", "pedido_listo": "TAdmPedidoListo",
          "entrega_nueva": "TAdmEntregaNueva", "entrega_creada": "TAdmEntregaCreada"}

ARCHIVOS = {"administracion": {"titulo": "altas, cambios y bajas; alta de pedidos y asignación de entregas", "incluye": ["comun"],
                               "tipos": ADMIN, "raices": RAICES}}

UUID = "7b1e4c2a-3f5d-4a6b-9c8d-0e1f2a3b4c5d"
EJEMPLOS = {
    "ProductoNuevo": ("producto_nuevo", {"clave_interna": "AB-900", "nombre": "Avena en hojuelas 500 g", "categoria_id": 1, "unidad": "pieza",
                                         "presentacion": "500 g", "precio": 32.5}),
    "ProductoCambio": ("producto_cambio", {"precio": 34.9, "estatus": "activo"}),
    "ZonaNueva": ("zona_nueva", {"clave": "ZN-NV01", "nombre": "Nueva Esperanza", "colonia": "Nueva Esperanza", "codigo_postal": "64102",
                                 "latitud": 25.7605, "longitud": -100.3702, "ticket_minimo": 80, "costo_envio": 15}),
    "ZonaCambio": ("zona_cambio", {"ticket_minimo": 90}),
    "MicrohubNuevo": ("microhub_nuevo", {"clave": "MH-09", "nombre": "Microhub Alianza", "direccion": "Av. Alianza 100, San Bernabé", "latitud": 25.7601,
                                         "longitud": -100.3555, "radio_km": 1.5, "capacidad_turno": 120, "hora_apertura": "08:00", "hora_cierre": "20:00"}),
    "MicrohubCambio": ("microhub_cambio", {"capacidad_turno": 140}),
    "UsuarioNuevo": ("usuario_nuevo", {"nombre": "Laura", "apellidos": "Cantú Ríos", "telefono": "8110000000", "rol": "repartidor",
                                       "correo": "laura.cantu@ejemplo.mx", "clave": "Una-clave-larga-1"}),
    "UsuarioCambio": ("usuario_cambio", {"estatus": "bloqueado"}),
    "PedidoNuevo": ("pedido_nuevo", {"cliente_id": 1, "lineas": [{"producto_id": 3, "cantidad": 4}, {"producto_id": 7, "cantidad": 2}], "operacion_uuid": UUID}),
    "PedidoCreado": ("pedido_creado", {"id": 901, "folio": "PED-20261126-000901", "estado": "asignado", "zona_id": 1, "microhub_id": 1, "subtotal": 186.0,
                                       "costo_envio": 15.0, "total": 201.0, "asignado": True, "motivo": None, "duplicado": False}),
    "PedidoListo": ("pedido_listo", {"id": 901, "estado": "en_preparacion", "listo_en": "2026-11-26T10:40:00-06:00"}),
    "EntregaNueva": ("entrega_nueva", {"pedido_id": 901, "repartidor_id": 7, "orden_parada": 1}),
    "EntregaCreada": ("entrega_creada", {"entrega_id": 412, "pedido_id": 901, "repartidor_id": 7, "estado_pedido": "en_ruta"}),
}
