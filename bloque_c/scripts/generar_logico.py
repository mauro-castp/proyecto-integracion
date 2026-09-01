#!/usr/bin/env python3
"""
generar_logico.py — Codex Innovations · Equipo 04

Construye el diagrama del modelo lógico leyendo el catálogo de PostgreSQL,
no un archivo escrito a mano. Así el diagrama no puede desincronizarse del
DDL: si alguien agrega una columna y no regenera, la diferencia se nota.

  python3 generar_logico.py > logico.dot && dot -Tpng logico.dot -o logico.png
"""
import argparse, subprocess, sys, collections

BD = "microhubs_p1"
ESQ = "microhubs"

GRUPOS = {
    "seguridad": (["rol", "permiso", "rol_permiso", "usuario", "auditoria"],
                  "Identidad, permisos y auditoría", "#1F4E79", "#DCE7F5", "#F2F6FB"),
    "territorio": (["zona", "microhub", "microhub_zona"],
                   "Territorio", "#2E6B4F", "#DCF0E5", "#F1F8F4"),
    "catalogo": (["categoria", "producto", "producto_precio_historico",
                  "inventario", "movimiento_inventario"],
                 "Catálogo e inventario", "#8A5A17", "#FAEBD3", "#FDF7EE"),
    # El area del pedido se parte en dos: junta, el diagrama resulta
    # ilegible en tamano carta.
    "pedido": (["cliente", "domicilio", "pedido", "pedido_detalle"],
               "Pedido: origen y contenido", "#7B2D4E", "#F7DCE7", "#FCF2F6"),
    "cierre": (["historial_estatus", "decision_asignacion", "entrega", "entrega_linea"],
               "Pedido: decision, seguimiento y cierre", "#7B2D4E", "#F7DCE7", "#FCF2F6"),
    "param": (["configuracion", "transicion_permitida", "demanda_no_atendida"],
              "Parámetros y demanda", "#54417B", "#EFEAF7", "#F7F4FB"),
}


def psql(sql):
    r = subprocess.run(
        ["su", "postgres", "-c",
         "psql -h /tmp -d %s -tAF'|' -c \"%s\"" % (BD, sql.replace('"', '\\"'))],
        capture_output=True, text=True)
    if r.returncode:
        sys.exit("psql: " + r.stderr)
    return [l.split("|") for l in r.stdout.strip().split("\n") if l.strip()]


cols = psql("""
SELECT c.table_name, c.column_name, c.data_type, c.is_nullable,
       COALESCE(c.character_maximum_length::text, ''), c.ordinal_position
  FROM information_schema.columns c
 WHERE c.table_schema = '%s'
 ORDER BY c.table_name, c.ordinal_position
""" % ESQ)

pks = {(r[0], r[1]) for r in psql("""
SELECT tc.table_name, kcu.column_name
  FROM information_schema.table_constraints tc
  JOIN information_schema.key_column_usage kcu
    ON kcu.constraint_name = tc.constraint_name AND kcu.table_schema = tc.table_schema
 WHERE tc.table_schema = '%s' AND tc.constraint_type = 'PRIMARY KEY'
""" % ESQ)}

fk_rows = psql("""
SELECT tc.table_name, kcu.column_name, ccu.table_name AS destino
  FROM information_schema.table_constraints tc
  JOIN information_schema.key_column_usage kcu
    ON kcu.constraint_name = tc.constraint_name AND kcu.table_schema = tc.table_schema
  JOIN information_schema.constraint_column_usage ccu
    ON ccu.constraint_name = tc.constraint_name AND ccu.table_schema = tc.table_schema
 WHERE tc.table_schema = '%s' AND tc.constraint_type = 'FOREIGN KEY'
""" % ESQ)
fks = {(r[0], r[1]) for r in fk_rows}
aristas = sorted({(r[0], r[2]) for r in fk_rows if r[0] != r[2]})

ABREV = {
    "character varying": "varchar", "timestamp with time zone": "timestamptz",
    "double precision": "float8", "USER-DEFINED": "enum", "character": "char",
    "integer": "int", "smallint": "int2", "bigint": "int8", "boolean": "bool",
    "numeric": "numeric", "date": "date", "time without time zone": "time",
    "jsonb": "jsonb", "inet": "inet", "text": "text",
}

por_tabla = collections.OrderedDict()
for t, c, dt, nul, ln, _ in cols:
    tipo = ABREV.get(dt, dt)
    if ln:
        tipo += "(%s)" % ln
    por_tabla.setdefault(t, []).append((c, tipo, nul == "YES"))

grupo_de = {}
for g, (tablas, *_r) in GRUPOS.items():
    for t in tablas:
        grupo_de[t] = g

ap = argparse.ArgumentParser()
ap.add_argument("--grupo", help="Genera solo un area tematica; las tablas externas "
                                "referenciadas aparecen como nodos compactos.")
args = ap.parse_args()

grupo_de = {}
for g, (tablas, *_r) in GRUPOS.items():
    for t in tablas:
        grupo_de[t] = g

if args.grupo:
    if args.grupo not in GRUPOS:
        sys.exit("grupo desconocido: " + args.grupo)
    grupos_dibujados = {args.grupo: GRUPOS[args.grupo]}
    propias = set(GRUPOS[args.grupo][0])
    # Tablas de otras areas a las que este grupo apunta: se muestran como
    # referencia externa para que el diagrama no quede colgando de la nada.
    externas = sorted({d for o, d in aristas if o in propias and d not in propias})
    aristas_dib = [(o, d) for o, d in aristas
                   if o in propias and (d in propias or d in externas)]
else:
    grupos_dibujados = GRUPOS
    propias = set(por_tabla)
    externas = []
    aristas_dib = aristas

out = []
w = out.append
w('digraph logico {')
w('  rankdir=LR; bgcolor="white"; splines=spline; overlap=false;')
w('  nodesep=0.30; ranksep=%s; pad=0.25;' % ("0.95" if args.grupo else "1.05"))
w('  node [shape=plaintext, fontname="Helvetica", fontsize=9];')
w('  edge [color="#5B6B7F", penwidth=1.0, arrowsize=0.65, arrowhead=normal];')

for g, (tablas, etiqueta, borde, cab, fondo) in grupos_dibujados.items():
    w('  subgraph cluster_%s {' % g)
    w('    label="  %s  "; fontname="Helvetica-Bold"; fontsize=12; fontcolor="%s";' % (etiqueta, borde))
    w('    style="rounded,filled"; fillcolor="%s"; color="%s";' % (fondo, borde))
    for t in tablas:
        if t not in por_tabla:
            continue
        filas = ['<TR><TD BGCOLOR="%s" COLSPAN="2"><B>%s</B></TD></TR>'
                 % (cab, t.upper().replace("_", " "))]
        for c, tipo, nulo in por_tabla[t]:
            marca = ""
            if (t, c) in pks:
                marca = "PK "
            if (t, c) in fks:
                marca += "FK "
            nom = ("<B>%s%s</B>" % (marca, c)) if marca else ("%s%s" % (marca, c))
            if not nulo and not marca:
                nom = "<U>%s</U>" % nom
            filas.append('<TR><TD ALIGN="LEFT" PORT="%s">%s</TD>'
                         '<TD ALIGN="LEFT"><FONT COLOR="#6B7A8C" POINT-SIZE="8">%s</FONT></TD></TR>'
                         % (c, nom, tipo))
        w('    %s [label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" '
          'CELLPADDING="3" COLOR="%s">%s</TABLE>>];' % (t, borde, "".join(filas)))
    w('  }')

for t in externas:
    g = grupo_de.get(t)
    borde = GRUPOS[g][2] if g else "#6B7A8C"
    cab = GRUPOS[g][3] if g else "#EEEEEE"
    w('  %s [label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4" '
      'COLOR="%s"><TR><TD BGCOLOR="%s"><B>%s</B></TD></TR>'
      '<TR><TD><FONT POINT-SIZE="7" COLOR="#6B7A8C">otra area</FONT></TD></TR>'
      '</TABLE>>];' % (t, borde, cab, t.upper().replace("_", " ")))

for origen, destino in aristas_dib:
    estilo = ' [style=dashed]' if destino in externas else ''
    w('  %s -> %s%s;' % (origen, destino, estilo))

w('}')
print("\n".join(out))
print("-- grupo=%s tablas=%d aristas=%d" % (args.grupo or "todos", len(propias), len(aristas_dib)),
      file=sys.stderr)
