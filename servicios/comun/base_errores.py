"""base_errores.py — Error estandarizado del contrato v1 ({codigo, mensaje, detalles, traza_id})."""


class ErrorApi(Exception):
    def __init__(self, status, codigo, mensaje, detalles=None, encabezados=None):
        super().__init__(mensaje)
        self.status, self.codigo, self.mensaje = status, codigo, mensaje
        self.detalles = detalles or []
        self.encabezados = encabezados or {}


def no_encontrado(mensaje="No existe el recurso solicitado."):
    return ErrorApi(404, "NO_ENCONTRADO", mensaje)


def prohibido(mensaje="Tu perfil no tiene permiso para esta operación."):
    return ErrorApi(403, "PROHIBIDO", mensaje)


def conflicto(mensaje):
    return ErrorApi(409, "CONFLICTO", mensaje)


def invalido(campo, mensaje):
    return ErrorApi(422, "VALIDACION", "Revisa los datos enviados.", [{"campo": campo, "mensaje": mensaje}])


def filtro_invalido(campo, mensaje):
    return ErrorApi(400, "FILTRO_INVALIDO", mensaje, [{"campo": campo, "mensaje": mensaje}])
