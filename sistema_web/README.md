# Bloque C — Modelo de datos

**Plataforma de Microhubs y Comercio de Proximidad**
Codex Innovations · Equipo 04 · Primer Parcial

Cubre las tareas 9 a 12: modelo PostgreSQL, colecciones MongoDB, claves Redis y script de seed.

El documento del entregable es `Modelo_de_Datos.docx` (24 páginas). Esta carpeta contiene los artefactos que ese documento describe.

Todo lo que está aquí se ejecutó y se validó contra PostgreSQL 16.15 y Redis reales. No es diseño en papel.

---

## Orden de ejecución

```bash
createdb microhubs_p1

psql -d microhubs_p1 -v ON_ERROR_STOP=1 -f sql/01_esquema.sql        # tablas y restricciones
psql -d microhubs_p1 -v ON_ERROR_STOP=1 -f sql/02_logica.sql         # funciones y triggers
psql -d microhubs_p1 -v ON_ERROR_STOP=1 -f sql/03_semilla.sql        # datos maestros
psql -d microhubs_p1 -v ON_ERROR_STOP=1 -f sql/04_operacion_demo.sql # operación histórica
```

Los tres primeros son idempotentes: `01` recrea el esquema desde cero y `02` usa `CREATE OR REPLACE` en todo, incluidos los triggers.

## Verificación

```bash
psql -d microhubs_p1 -f sql/05_pruebas_reglas.sql   # VR-01 a VR-16  -> 26 aserciones
./scripts/06_prueba_concurrencia.sh                 # VR-08 con dos sesiones simultáneas
./redis/05_pruebas_redis.sh                         # 25 aserciones sobre claves y bloqueos
```

Resultado actual: **26/26**, **VR-08 PASA**, **25/25**.

`05_pruebas_reglas.sql` corre dentro de una transacción que termina en `ROLLBACK`; se puede ejecutar cuantas veces se quiera sin ensuciar los datos.

---

## Contenido

### `sql/`

| Archivo | Qué contiene |
|---|---|
| `01_esquema.sql` | 24 tablas, 8 tipos enumerados, 41 restricciones CHECK propias, 37 claves foráneas, 66 índices. |
| `02_logica.sql` | 19 funciones, 5 triggers de negocio más 17 de auditoría automática, 3 vistas, 2 roles de base. |
| `03_semilla.sql` | Generado. No editar a mano: volver a generar con `scripts/generar_semilla.py`. |
| `04_operacion_demo.sql` | 180 pedidos pasados por el motor real de asignación. |
| `05_pruebas_reglas.sql` | Los 16 casos VR del entregable de reglas, ejecutables. |

### `mongo/`

`01_colecciones.js` — 6 colecciones con validadores JSON Schema y 19 índices.

```bash
mongosh "mongodb://localhost:27017/microhubs_eventos" mongo/01_colecciones.js
```

### `redis/`

`01_claves.md` es el catálogo de claves con TTL y justificación. Los tres `.lua` son los scripts de bloqueo y revocación.

### `diagramas/`

`conceptual.png` es el modelo conceptual completo. Los seis `logico_*.png` son el modelo lógico partido por área temática. El área del pedido se dividió en dos porque junta resultaba ilegible en tamaño carta.

`generar_logico.py` construye los diagramas **leyendo el catálogo de PostgreSQL**, no un archivo escrito a mano. Si alguien agrega una columna y no regenera, la diferencia se nota.

### `scripts/`

`generar_semilla.py` regenera el seed. Es determinista (semilla 2604): la misma invocación produce el mismo archivo.

```bash
python3 scripts/generar_semilla.py --clientes 40 --pedidos 180 --dias 45
```

Requiere `bcrypt` (`pip install bcrypt`).

---

## Datos del seed

Cuatro colonias del sector San Bernabé, con códigos postales verificados contra el Catálogo Nacional:

| Zona | Colonia | CP |
|---|---|---|
| ZN-SB01 | San Bernabé | 64100 |
| ZN-SB02 | Valles de San Bernabé | 64103 |
| ZN-SB03 | Paseo de San Bernabé | 64103 |
| ZN-SB04 | San Bernabé X (F-113) | 64105 |

Valles y Paseo comparten el 64103. Por eso la zona se identifica por la pareja (colonia, código postal) y la consulta pública de cobertura acepta ambos criterios. Las coordenadas son aproximaciones del centroide de colonia y deben sustituirse por coordenadas levantadas en campo antes de operar.

Volumen cargado: 4 zonas, 4 microhubs, 51 productos, 48 usuarios, 40 clientes, 153 renglones de inventario, 36 permisos, 18 transiciones y 149 eventos de demanda no atendida.

## Imágenes del catálogo

Las fotografías están en `static/productos/` y se relacionan con el catálogo
mediante la clave interna del producto, por ejemplo `AB-001.jpg` o
`HI-004.webp`. Para agregar o sustituir una imagen basta con usar la misma clave
y una extensión compatible (`jpg`, `jpeg`, `png` o `webp`) y reconstruir el
contenedor. Si un producto no tiene fotografía se muestra automáticamente
`sin-imagen.svg`.

Contraseña de todas las cuentas demo: `Codex#2026` (hash bcrypt real, coste 10).

Cuentas principales:

| Correo | Rol |
|---|---|
| `admin@codex.mx` | Administrador |
| `operador.mh01@codex.mx` | Operador de MH-01 |
| `planeador@codex.mx` | Planeador |
| `auditor@codex.mx` | Auditor |
| `repartidor1@codex.mx` | Repartidor |

---

## Pendientes antes de congelar el DDL

1. **Reversión administrativa de un pedido entregado.** La sección 6 del entregable de reglas la exige con motivo y bitácora, pero no define el estado destino. No se inventó una transición: hay que decidirla y agregarla a `transicion_permitida`.
2. **Cancelación desde `pendiente_asignacion`.** RN21 solo menciona los estados creado y asignado. Hoy únicamente el Administrador puede cancelar desde pendiente. Confirmar si el Cliente también debería poder.
3. **Umbral de envío gratuito.** El parámetro de $250 aparece en la tabla 4.6 del entregable de reglas pero no tiene una RN que lo defina. O se agrega la regla o se quita el parámetro.
4. **Coordenadas reales** de las cuatro colonias y de los microhubs.
5. **RF38 (manifiestos)** sigue sin historia de usuario ni caso de uso, como ya señalaba la propia matriz de trazabilidad.
