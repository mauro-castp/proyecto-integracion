"""Paginación SQL compartida. Los nombres de columnas siempre vienen del código."""
import math
from flask import abort, g, request, url_for


def limites():
    try:
        pagina = int(request.args.get('pagina', 1))
        cantidad = int(request.args.get('por_pagina', 20))
        if pagina < 1 or cantidad not in (10, 20, 50, 100):
            raise ValueError
    except (TypeError, ValueError):
        abort(400, 'Página inválida o tamaño distinto de 10, 20, 50 o 100.')
    return pagina, cantidad


def paginar(sql, args, consulta, campos=(), marcador='%s', filtrar=True, campo_estatus=None):
    pagina, cantidad = limites()
    condiciones, valores = [], list(args)
    q = request.args.get('q', '').strip()[:120]
    estado = request.args.get('estatus', '')
    if filtrar and q and campos:
        condiciones.append('(' + ' OR '.join(f'lower(CAST({c} AS TEXT)) LIKE {marcador}' for c in campos) + ')')
        valores.extend(['%' + q.lower() + '%'] * len(campos))
    if filtrar and campo_estatus and estado in ('activo', 'inactivo', 'bloqueado', 'baja'):
        condiciones.append(f'CAST({campo_estatus} AS TEXT) = {marcador}')
        valores.append(estado)
    base = f'SELECT * FROM ({sql}) listado' + (' WHERE ' + ' AND '.join(condiciones) if condiciones else '')
    total = consulta(f'SELECT count(*) AS total FROM ({base}) conteo', tuple(valores), una=True)['total']
    paginas = max(1, math.ceil(total / cantidad))
    pagina = min(pagina, paginas)
    g.paginacion = dict(pagina=pagina, por_pagina=cantidad, total=total, paginas=paginas)
    return consulta(base + f' LIMIT {marcador} OFFSET {marcador}', tuple(valores) + (cantidad, (pagina - 1) * cantidad))


def enlace_pagina(pagina):
    valores = request.args.to_dict()
    valores['pagina'] = pagina
    valores.update(request.view_args or {})
    return url_for(request.endpoint, **valores)
