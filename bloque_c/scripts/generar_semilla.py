#!/usr/bin/env python3
"""
generar_semilla.py — Codex Innovations · Equipo 04
Genera 03_semilla.sql de forma determinista (semilla fija = 2604).

Volumen configurable desde CLI:
    python3 generar_semilla.py --clientes 40 --pedidos 180 --dias 45

Los datos territoriales corresponden a cuatro colonias reales del sector
San Bernabé, Monterrey, N. L. Los códigos postales están verificados contra
el Catálogo Nacional de Códigos Postales. Las coordenadas son aproximaciones
documentadas del centroide de cada colonia y deben sustituirse por
coordenadas levantadas en campo antes de operar.
"""
import argparse, random, unicodedata
from datetime import date, timedelta

import bcrypt

SEMILLA = 2604
CONTRASENA_DEMO = "Codex#2026"

# ---------------------------------------------------------------------
# Territorio: cuatro colonias del sector San Bernabé
# CP verificados. Nótese que Valles y Paseo comparten el 64103: por eso la
# zona se identifica por (colonia, codigo_postal) y no solo por CP.
# ---------------------------------------------------------------------
ZONAS = [
    # clave,      nombre,                    colonia,                  cp,      lat,       lng,      ticket, envio, gratis
    ("ZN-SB01", "San Bernabé Centro",      "San Bernabé",             "64100", 25.745500, -100.358500, 80.00, 15.00, 250.00),
    ("ZN-SB02", "Valles de San Bernabé",   "Valles de San Bernabé",   "64103", 25.753000, -100.369000, 80.00, 15.00, 250.00),
    ("ZN-SB03", "Paseo de San Bernabé",    "Paseo de San Bernabé",    "64103", 25.758000, -100.374500, 90.00, 18.00, 260.00),
    ("ZN-SB04", "San Bernabé X (F-113)",   "San Bernabé X (F-113)",   "64105", 25.749500, -100.380000, 75.00, 15.00, 240.00),
]

MICROHUBS = [
    # clave,   nombre,                         direccion,                        lat,        lng,       radio, cap, estatus
    ("MH-01", "Microhub San Bernabé Centro",  "Av. Rodrigo Gómez 1420, local 3", 25.748000, -100.364000, 1.50, 12, "activo"),
    ("MH-02", "Microhub Valles",              "Valle de Santiago 208",           25.755500, -100.372000, 1.50, 12, "activo"),
    ("MH-03", "Microhub Poniente F-113",      "Camino a San Bernabé 77",         25.750000, -100.381000, 1.20,  8, "activo"),
    ("MH-04", "Microhub Piloto Alianza",      "Alianza Real 45",                 25.762000, -100.352000, 1.50, 10, "inactivo"),
]

MICROHUB_ZONAS = {"MH-01": [1, 2], "MH-02": [2, 3], "MH-03": [4, 1], "MH-04": [3]}

CATEGORIAS = [
    ("Abarrote básico", 1), ("Bebidas", 2), ("Lácteos y huevo", 3),
    ("Limpieza del hogar", 4), ("Higiene personal", 5),
]

PRODUCTOS = [
    # clave,   nombre,                                  cat, unidad,   presentacion,  precio
    ("AB-001", "Frijol negro a granel",                  1, "kg",     "1 kg",         38.50),
    ("AB-002", "Arroz superextra",                       1, "kg",     "1 kg",         29.90),
    ("AB-003", "Aceite vegetal",                         1, "botella","900 ml",       42.00),
    ("AB-004", "Azúcar estándar",                        1, "kg",     "1 kg",         28.50),
    ("AB-005", "Sal de mesa",                            1, "pieza",  "1 kg",         14.00),
    ("AB-006", "Harina de maíz nixtamalizado",           1, "kg",     "1 kg",         26.00),
    ("AB-007", "Harina de trigo",                        1, "kg",     "1 kg",         24.50),
    ("AB-008", "Pasta para sopa surtida",                1, "pieza",  "200 g",         9.50),
    ("AB-009", "Atún en agua",                           1, "lata",   "140 g",        21.00),
    ("AB-010", "Sardina en salsa de tomate",             1, "lata",   "425 g",        26.50),
    ("AB-011", "Frijoles refritos",                      1, "lata",   "430 g",        23.00),
    ("AB-012", "Chiles jalapeños en escabeche",          1, "lata",   "380 g",        19.50),
    ("AB-013", "Puré de tomate",                         1, "pieza",  "210 g",        11.00),
    ("AB-014", "Café soluble",                           1, "frasco", "63 g",         52.00),
    ("AB-015", "Avena en hojuelas",                      1, "bolsa",  "400 g",        27.00),
    ("AB-016", "Galletas María",                         1, "paquete","170 g",        16.50),
    ("AB-017", "Tortillas de maíz",                      1, "kg",     "1 kg",         24.00),
    ("AB-018", "Pan de caja blanco",                     1, "paquete","680 g",        44.00),
    ("AB-019", "Huevo blanco",                           1, "kg",     "1 kg",         42.00),
    ("AB-020", "Lenteja",                                1, "kg",     "500 g",        24.00),
    ("BE-001", "Agua purificada",                        2, "garrafón","20 L",        38.00),
    ("BE-002", "Agua embotellada",                       2, "botella","1.5 L",        15.00),
    ("BE-003", "Refresco de cola",                       2, "botella","2 L",          38.50),
    ("BE-004", "Refresco sabor manzana",                 2, "botella","2 L",          36.00),
    ("BE-005", "Jugo de naranja",                        2, "envase", "1 L",          28.00),
    ("BE-006", "Bebida de soya",                         2, "envase", "946 ml",       32.00),
    ("BE-007", "Té helado de limón",                     2, "botella","600 ml",       17.00),
    ("BE-008", "Polvo para agua de sabor",               2, "sobre",  "25 g",          7.50),
    ("LA-001", "Leche entera",                           3, "envase", "1 L",          27.50),
    ("LA-002", "Leche deslactosada",                     3, "envase", "1 L",          31.00),
    ("LA-003", "Queso fresco",                           3, "pieza",  "400 g",        58.00),
    ("LA-004", "Queso Oaxaca",                           3, "pieza",  "400 g",        72.00),
    ("LA-005", "Crema ácida",                            3, "envase", "450 ml",       36.00),
    ("LA-006", "Yogur natural",                          3, "envase", "900 g",        44.00),
    ("LA-007", "Mantequilla",                            3, "barra",  "90 g",         22.00),
    ("LA-008", "Jamón de pavo",                          3, "paquete","250 g",        46.00),
    ("LI-001", "Detergente en polvo",                    4, "bolsa",  "1 kg",         42.00),
    ("LI-002", "Jabón para trastes",                     4, "pieza",  "400 g",        26.00),
    ("LI-003", "Cloro",                                  4, "botella","950 ml",       19.50),
    ("LI-004", "Limpiador multiusos",                    4, "botella","1 L",          28.00),
    ("LI-005", "Suavizante de telas",                    4, "botella","800 ml",       33.00),
    ("LI-006", "Papel higiénico",                        4, "paquete","4 rollos",     38.00),
    ("LI-007", "Servilletas",                            4, "paquete","500 pzas",     32.00),
    ("LI-008", "Bolsas para basura",                     4, "paquete","10 pzas",      24.00),
    ("LI-009", "Fibra para trastes",                     4, "paquete","3 pzas",       18.00),
    ("HI-001", "Jabón de tocador",                       5, "pieza",  "150 g",        14.50),
    ("HI-002", "Shampoo",                                5, "botella","400 ml",       54.00),
    ("HI-003", "Pasta dental",                           5, "pieza",  "100 ml",       32.00),
    ("HI-004", "Desodorante",                            5, "pieza",  "50 g",         48.00),
    ("HI-005", "Toallas femeninas",                      5, "paquete","10 pzas",      36.00),
    ("HI-006", "Pañal etapa 3",                          5, "paquete","10 pzas",      68.00),
]

ROLES = [
    ("administrador", "Administrador", "Administra catálogos, usuarios, configuración y supervisa la operación.", False),
    ("operador",      "Operador de microhub", "Prepara pedidos, mantiene inventario y cierra entregas de su microhub.", True),
    ("planeador",     "Planeador", "Ejecuta análisis de demanda, ubicación, capacidad y viabilidad.", False),
    ("cliente",       "Cliente", "Integra carrito, confirma pedidos y da seguimiento a los propios.", False),
    ("repartidor",    "Repartidor", "Ejecuta la ruta del turno y registra el resultado de la entrega.", False),
    ("auditor",       "Auditor", "Consulta bitácora, conciliaciones y evidencia. Solo lectura.", False),
    ("visitante",     "Público", "Consulta catálogo y cobertura sin autenticación.", False),
]

MODULOS = {
    "usuarios":     ["ver", "crear", "editar", "baja"],
    "roles":        ["ver", "editar"],
    "zonas":        ["ver", "crear", "editar", "baja"],
    "productos":    ["ver", "crear", "editar", "baja"],
    "microhubs":    ["ver", "crear", "editar", "baja"],
    "inventario":   ["ver", "movimiento", "ajuste"],
    "pedidos":      ["ver", "crear", "cambiar_estado", "cancelar", "reasignar"],
    "entregas":     ["ver", "asignar", "cerrar"],
    "indicadores":  ["ver"],
    "bitacora":     ["ver"],
    "configuracion":["ver", "editar"],
    "simulacion":   ["ver", "ejecutar"],
    "catalogo_publico": ["ver"],
}

PERMISOS_POR_ROL = {
    "administrador": "TODOS",
    "operador": ["pedidos.ver", "pedidos.cambiar_estado", "inventario.ver", "inventario.movimiento",
                 "entregas.ver", "entregas.asignar", "entregas.cerrar", "indicadores.ver",
                 "productos.ver", "catalogo_publico.ver"],
    "planeador": ["pedidos.ver", "pedidos.reasignar", "indicadores.ver", "simulacion.ver",
                  "simulacion.ejecutar", "zonas.ver", "microhubs.ver", "productos.ver",
                  "catalogo_publico.ver"],
    "cliente": ["pedidos.ver", "pedidos.crear", "pedidos.cancelar", "catalogo_publico.ver", "productos.ver"],
    "repartidor": ["entregas.ver", "entregas.cerrar", "pedidos.ver"],
    "auditor": ["bitacora.ver", "pedidos.ver", "inventario.ver", "entregas.ver",
                "indicadores.ver", "usuarios.ver", "configuracion.ver"],
    "visitante": ["catalogo_publico.ver"],
}

# RN19-RN24 + tabla de la sección 5 del entregable de reglas.
TRANSICIONES = [
    ("creado", "asignado", "sistema", False, "El pedido pasó validaciones y existe microhub elegible."),
    ("creado", "asignado", "administrador", False, "Asignación administrativa."),
    ("creado", "pendiente_asignacion", "sistema", False, "RN14: no existe microhub elegible."),
    ("creado", "cancelado", "cliente", False, "RN21: el Cliente aún puede cancelar."),
    ("creado", "cancelado", "administrador", True, "Cancelación administrativa con motivo."),
    ("pendiente_asignacion", "asignado", "planeador", True, "RN24: reasignación manual con motivo obligatorio."),
    ("pendiente_asignacion", "asignado", "administrador", True, "Reasignación administrativa con motivo."),
    ("pendiente_asignacion", "cancelado", "administrador", True, "Cancelación administrativa con motivo."),
    ("asignado", "en_preparacion", "operador", False, "RN23: el operador inicia el alistamiento."),
    ("asignado", "cancelado", "cliente", False, "RN21: la cancelación todavía está permitida."),
    ("asignado", "cancelado", "administrador", True, "Cancelación administrativa con motivo."),
    ("en_preparacion", "en_ruta", "operador", False, "RN23: pedido preparado y entregado al reparto."),
    ("en_ruta", "entregado", "repartidor", False, "Entrega completada y cobro registrado."),
    ("en_ruta", "entregado", "operador", False, "Cierre operativo en P1 (sección 2.9)."),
    ("en_ruta", "entrega_parcial", "repartidor", False, "RN28: parte del pedido no se entrega."),
    ("en_ruta", "entrega_parcial", "operador", False, "Cierre operativo en P1."),
    ("en_ruta", "entrega_fallida", "repartidor", True, "RN29: motivo o incidencia obligatoria."),
    ("en_ruta", "entrega_fallida", "operador", True, "RN29: motivo o incidencia obligatoria."),
]

CONFIGURACION = [
    ("radio_cobertura_km",    "1.5",  "numerico", "km",      "RN05. Radio de servicio por omisión de un microhub."),
    ("ticket_minimo",         "80",   "numerico", "MXN",     "RN07. Subtotal mínimo para confirmar un pedido."),
    ("costo_envio",           "15",   "numerico", "MXN",     "RN08. No cuenta para el ticket mínimo."),
    ("envio_gratis_desde",    "250",  "numerico", "MXN",     "Umbral de envío gratuito. Parámetro sin RN propia: pendiente de formalizar."),
    ("capacidad_turno",       "12",   "entero",   "pedidos", "RN12. Capacidad por microhub y turno."),
    ("limite_unidades_linea", "20",   "entero",   "unidades","RN09. Límite global por línea de pedido."),
    ("intentos_fallidos_max", "5",    "entero",   "intentos","RF06. Antes: constante en el texto del RF."),
    ("bloqueo_minutos",       "15",   "entero",   "minutos", "RF06. Duración del bloqueo temporal."),
    ("jwt_acceso_minutos",    "15",   "entero",   "minutos", "RF03. Vigencia del token de acceso."),
    ("jwt_refresh_dias",      "7",    "entero",   "días",    "RF03. Vigencia del token de renovación."),
    ("reset_token_minutos",   "30",   "entero",   "minutos", "RF05. Vigencia del token de un solo uso."),
    ("umbral_ajuste_inventario", "25","entero",   "unidades","CU07 A3. Ajuste que exige autorización administrativa."),
    ("cache_catalogo_segundos", "300","entero",   "segundos","RNF07. TTL del catálogo público en Redis."),
    ("rate_publico_por_minuto", "60", "entero",   "peticiones","CU02 A3. Límite de consultas públicas por origen."),
]

NOMBRES = ["María", "José", "Guadalupe", "Juan", "Rosa", "Miguel", "Ana", "Luis", "Martha",
           "Jorge", "Patricia", "Francisco", "Leticia", "Ricardo", "Alma", "Sergio", "Norma",
           "Raúl", "Blanca", "Alejandro", "Sandra", "Óscar", "Verónica", "Héctor", "Silvia",
           "Armando", "Claudia", "Gerardo", "Yolanda", "Rubén"]
APELLIDOS = ["Garza", "Treviño", "Salazar", "Rodríguez", "Martínez", "Cavazos", "González",
             "Hernández", "Guerrero", "Villarreal", "Elizondo", "de la Cruz", "Ramos",
             "Zúñiga", "Alanís", "Lozano", "Ibarra", "Sepúlveda", "Escobedo", "Chapa"]
CALLES = ["Rodrigo Gómez", "Valle de Santiago", "Camino a San Bernabé", "Río Salinas",
          "Emiliano Zapata", "Los Ángeles", "Valle Alto", "Nogal", "Cerro Prieto",
          "Fresno", "Paseo del Valle", "Aztlán", "Fidel Velázquez", "Ruiz Cortines"]


def sin_acentos(t):
    return "".join(c for c in unicodedata.normalize("NFD", t)
                   if unicodedata.category(c) != "Mn")


def esc(t):
    return t.replace("'", "''")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clientes", type=int, default=40)
    ap.add_argument("--pedidos", type=int, default=180)
    ap.add_argument("--dias", type=int, default=45)
    ap.add_argument("--salida", default="03_semilla.sql")
    args = ap.parse_args()

    rnd = random.Random(SEMILLA)
    hash_demo = bcrypt.hashpw(CONTRASENA_DEMO.encode(), bcrypt.gensalt(rounds=10)).decode()

    o = []
    w = o.append

    w("-- =====================================================================")
    w("-- 03_semilla.sql — GENERADO por generar_semilla.py (semilla %d)" % SEMILLA)
    w("-- Codex Innovations · Equipo 04 · Primer Parcial")
    w("--")
    w("-- NO editar a mano: volver a generar con")
    w("--   python3 generar_semilla.py --clientes %d --pedidos %d --dias %d"
      % (args.clientes, args.pedidos, args.dias))
    w("--")
    w("-- Contraseña de todas las cuentas demo: %s" % CONTRASENA_DEMO)
    w("-- El hash es bcrypt real (coste 10), no un marcador de posición.")
    w("-- Territorio: cuatro colonias del sector San Bernabé, Monterrey, N. L.")
    w("-- CP verificados contra el Catálogo Nacional de Códigos Postales.")
    w("-- Coordenadas: aproximaciones documentadas del centroide de colonia.")
    w("-- =====================================================================")
    w("")
    w("SET search_path TO microhubs, public;")
    w("BEGIN;")
    w("")

    # --- configuración ---
    w("-- ---------- Configuración operativa (RN40) ----------")
    for clave, valor, tipo, unidad, desc in CONFIGURACION:
        w("INSERT INTO configuracion (clave, valor, tipo_dato, ambito, unidad, descripcion) "
          "VALUES ('%s', '%s', '%s', 'global', '%s', '%s');"
          % (clave, valor, tipo, unidad, esc(desc)))
    w("")

    # --- roles ---
    w("-- ---------- Roles, permisos y ámbitos (RF01, RF02) ----------")
    for clave, nombre, desc, req in ROLES:
        w("INSERT INTO rol (clave, nombre, descripcion, requiere_microhub) "
          "VALUES ('%s', '%s', '%s', %s);" % (clave, esc(nombre), esc(desc), str(req).lower()))
    w("")

    permisos = []
    for modulo, acciones in MODULOS.items():
        for accion in acciones:
            permisos.append(("%s.%s" % (modulo, accion), modulo, accion))
    for clave, modulo, accion in permisos:
        w("INSERT INTO permiso (clave, modulo, accion) VALUES ('%s', '%s', '%s');"
          % (clave, modulo, accion))
    w("")

    for rol_clave, lista in PERMISOS_POR_ROL.items():
        if lista == "TODOS":
            w("INSERT INTO rol_permiso (rol_id, permiso_id) "
              "SELECT r.id, p.id FROM rol r CROSS JOIN permiso p WHERE r.clave = '%s';" % rol_clave)
        else:
            claves = ", ".join("'%s'" % c for c in lista)
            w("INSERT INTO rol_permiso (rol_id, permiso_id) "
              "SELECT r.id, p.id FROM rol r JOIN permiso p ON p.clave IN (%s) "
              "WHERE r.clave = '%s';" % (claves, rol_clave))
    w("")

    # --- transiciones ---
    w("-- ---------- Máquina de estados como dato (RN19-RN24) ----------")
    for o_, d_, rol_, mot, desc in TRANSICIONES:
        w("INSERT INTO transicion_permitida (estado_origen, estado_destino, rol_clave, "
          "requiere_motivo, descripcion) VALUES ('%s', '%s', '%s', %s, '%s');"
          % (o_, d_, rol_, str(mot).lower(), esc(desc)))
    w("")

    # --- zonas ---
    w("-- ---------- Zonas: cuatro colonias del sector San Bernabé ----------")
    for clave, nombre, colonia, cp, lat, lng, tk, env, gr in ZONAS:
        w("INSERT INTO zona (clave, nombre, colonia, codigo_postal, centroide_lat, "
          "centroide_lng, ticket_minimo, costo_envio, envio_gratis_desde) VALUES "
          "('%s', '%s', '%s', '%s', %.6f, %.6f, %.2f, %.2f, %.2f);"
          % (clave, esc(nombre), esc(colonia), cp, lat, lng, tk, env, gr))
    w("")

    # --- microhubs ---
    w("-- ---------- Microhubs ----------")
    for clave, nombre, dirn, lat, lng, radio, cap, est in MICROHUBS:
        w("INSERT INTO microhub (clave, nombre, direccion, latitud, longitud, radio_km, "
          "capacidad_turno, estatus) VALUES ('%s', '%s', '%s', %.6f, %.6f, %.2f, %d, '%s');"
          % (clave, esc(nombre), esc(dirn), lat, lng, radio, cap, est))
    for mh, zonas in MICROHUB_ZONAS.items():
        for zi in zonas:
            w("INSERT INTO microhub_zona (microhub_id, zona_id) SELECT m.id, z.id FROM microhub m, "
              "zona z WHERE m.clave = '%s' AND z.clave = '%s';" % (mh, ZONAS[zi - 1][0]))
    w("")

    # --- catálogo ---
    w("-- ---------- Catálogo ----------")
    for nombre, orden in CATEGORIAS:
        w("INSERT INTO categoria (nombre, orden) VALUES ('%s', %d);" % (esc(nombre), orden))
    for cl, nom, cat, uni, pres, precio in PRODUCTOS:
        w("INSERT INTO producto (clave_interna, nombre, categoria_id, unidad, presentacion, precio) "
          "SELECT '%s', '%s', c.id, '%s', '%s', %.2f FROM categoria c WHERE c.orden = %d;"
          % (cl, esc(nom), uni, pres, precio, cat))
    w("")

    # --- usuarios internos ---
    w("-- ---------- Usuarios internos ----------")
    internos = [
        ("Mauro", "Castillo Peña", "admin@codex.mx", "administrador", None),
        ("Ruth Elizabeth", "Soriano", "operador.mh01@codex.mx", "operador", "MH-01"),
        ("María José", "Cedillo Mata", "operador.mh02@codex.mx", "operador", "MH-02"),
        ("Jorge Antonio", "Arreola Cantu", "operador.mh03@codex.mx", "operador", "MH-03"),
        ("Vanessa", "Morante López", "planeador@codex.mx", "planeador", None),
        ("Alicia", "Guerrero Chapa", "auditor@codex.mx", "auditor", None),
        ("Ramiro", "Alanís Lozano", "repartidor1@codex.mx", "repartidor", None),
        ("Diana", "Sepúlveda Ibarra", "repartidor2@codex.mx", "repartidor", None),
    ]
    for nom, ape, correo, rol, mh in internos:
        if mh:
            w("INSERT INTO usuario (nombre, apellidos, correo, telefono, hash_contrasena, rol_id, microhub_id) "
              "SELECT '%s', '%s', '%s', '81%08d', '%s', r.id, m.id FROM rol r, microhub m "
              "WHERE r.clave = '%s' AND m.clave = '%s';"
              % (esc(nom), esc(ape), correo, rnd.randint(10000000, 99999999), hash_demo, rol, mh))
        else:
            w("INSERT INTO usuario (nombre, apellidos, correo, telefono, hash_contrasena, rol_id) "
              "SELECT '%s', '%s', '%s', '81%08d', '%s', r.id FROM rol r WHERE r.clave = '%s';"
              % (esc(nom), esc(ape), correo, rnd.randint(10000000, 99999999), hash_demo, rol))
    w("")

    # --- clientes ---
    w("-- ---------- Clientes y domicilios (RN03: un domicilio activo) ----------")
    usados = set()
    for i in range(1, args.clientes + 1):
        nom = rnd.choice(NOMBRES)
        ape = "%s %s" % (rnd.choice(APELLIDOS), rnd.choice(APELLIDOS))
        base = "%s.%s" % (sin_acentos(nom).lower(), sin_acentos(ape.split()[0]).lower())
        correo = "%s%d@correo.mx" % (base, i)
        usados.add(correo)
        zi = rnd.randrange(len(ZONAS))
        zclave, _, colonia, cp, zlat, zlng, *_ = ZONAS[zi]
        # Dispersión ~ +/- 0.6 km alrededor del centroide de la colonia.
        lat = zlat + rnd.uniform(-0.0055, 0.0055)
        lng = zlng + rnd.uniform(-0.0060, 0.0060)

        w("INSERT INTO usuario (nombre, apellidos, correo, telefono, hash_contrasena, rol_id) "
          "SELECT '%s', '%s', '%s', '81%08d', '%s', r.id FROM rol r WHERE r.clave = 'cliente';"
          % (esc(nom), esc(ape), correo, rnd.randint(10000000, 99999999), hash_demo))
        w("INSERT INTO cliente (usuario_id, aviso_privacidad_version, aviso_privacidad_aceptado_en) "
          "SELECT u.id, 'AP-2026.1', now() - interval '%d days' FROM usuario u WHERE u.correo = '%s';"
          % (rnd.randint(10, 120), correo))
        w("INSERT INTO domicilio (cliente_id, calle, numero_ext, colonia, codigo_postal, "
          "referencia, latitud, longitud, zona_id) "
          "SELECT c.id, '%s', '%d', '%s', '%s', '%s', %.6f, %.6f, z.id "
          "FROM cliente c JOIN usuario u ON u.id = c.usuario_id, zona z "
          "WHERE u.correo = '%s' AND z.clave = '%s';"
          % (esc(rnd.choice(CALLES)), rnd.randint(100, 4999), esc(colonia), cp,
             esc(rnd.choice(["Casa de dos pisos", "Portón negro", "Frente a la tienda",
                             "Esquina con la primaria", "Barda blanca"])),
             lat, lng, correo, zclave))
    w("")

    # --- inventario ---
    w("-- ---------- Inventario inicial por microhub activo ----------")
    w("-- Existencias distintas por hub a propósito: sin esa asimetría, la regla")
    w("-- de elegibilidad por existencia completa (RN12) nunca se ejercita.")
    for clave, _n, _d, _la, _lo, _r, _c, est in MICROHUBS:
        if est != "activo":
            continue
        for cl, *_ in PRODUCTOS:
            existencia = rnd.choice([0, 3, 8] + list(range(12, 90)))
            minimo = rnd.choice([5, 8, 10])
            w("INSERT INTO inventario (microhub_id, producto_id, existencia, minimo) "
              "SELECT m.id, p.id, %d, %d FROM microhub m, producto p "
              "WHERE m.clave = '%s' AND p.clave_interna = '%s';"
              % (existencia, minimo, clave, cl))
            if existencia > 0:
                w("INSERT INTO movimiento_inventario (microhub_id, producto_id, tipo, cantidad, "
                  "existencia_resultante, referencia_tipo, motivo) "
                  "SELECT m.id, p.id, 'recepcion', %d, %d, 'carga_inicial', 'Carga inicial de semilla' "
                  "FROM microhub m, producto p WHERE m.clave = '%s' AND p.clave_interna = '%s';"
                  % (existencia, existencia, clave, cl))
    w("")

    # --- demanda no atendida histórica ---
    w("-- ---------- Demanda no atendida (RN06, HU01, HU08) ----------")
    fuera = [("Alianza Real", "64102"), ("Fomerrey 112", "64114"),
             ("Valle de Infonavit", "64118"), ("Sierra Ventana", "64158")]
    for _ in range(60):
        col, cp = rnd.choice(fuera)
        w("INSERT INTO demanda_no_atendida (tipo, colonia_texto, cp_texto, origen, fecha) "
          "VALUES ('fuera_cobertura', '%s', '%s', '%s', now() - interval '%d days');"
          % (esc(col), cp, rnd.choice(["web", "android"]), rnd.randint(0, args.dias)))
    for _ in range(35):
        cl = rnd.choice(PRODUCTOS)[0]
        zi = rnd.randrange(len(ZONAS))
        w("INSERT INTO demanda_no_atendida (tipo, zona_id, producto_id, cantidad_solicitada, origen, fecha) "
          "SELECT 'sin_existencia', z.id, p.id, %d, 'web', now() - interval '%d days' "
          "FROM zona z, producto p WHERE z.clave = '%s' AND p.clave_interna = '%s';"
          % (rnd.randint(1, 6), rnd.randint(0, args.dias), ZONAS[zi][0], cl))
    for _ in range(18):
        zi = rnd.randrange(len(ZONAS))
        w("INSERT INTO demanda_no_atendida (tipo, zona_id, origen, fecha) "
          "SELECT 'bajo_ticket_minimo', z.id, 'web', now() - interval '%d days' "
          "FROM zona z WHERE z.clave = '%s';" % (rnd.randint(0, args.dias), ZONAS[zi][0]))
    w("")

    w("COMMIT;")
    w("")
    w("-- Resumen de la carga")
    w("SELECT 'zonas' AS entidad, count(*) FROM zona")
    w("UNION ALL SELECT 'microhubs', count(*) FROM microhub")
    w("UNION ALL SELECT 'productos', count(*) FROM producto")
    w("UNION ALL SELECT 'usuarios', count(*) FROM usuario")
    w("UNION ALL SELECT 'clientes', count(*) FROM cliente")
    w("UNION ALL SELECT 'inventario', count(*) FROM inventario")
    w("UNION ALL SELECT 'permisos', count(*) FROM permiso")
    w("UNION ALL SELECT 'transiciones', count(*) FROM transicion_permitida")
    w("UNION ALL SELECT 'demanda_no_atendida', count(*) FROM demanda_no_atendida;")

    with open(args.salida, "w", encoding="utf-8") as f:
        f.write("\n".join(o) + "\n")
    print("Generado %s (%d líneas)" % (args.salida, len(o)))


if __name__ == "__main__":
    main()
