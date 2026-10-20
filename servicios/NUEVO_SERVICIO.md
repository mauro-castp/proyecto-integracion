# Cómo agregar un microservicio

Los cinco servicios de la Ola 1 se hicieron con estos pasos. Cada paso nombra el archivo que se toca. Para ver un ejemplo completo,
mirar `abastecimiento/` (el que usa más piezas) o `proveedores/` (el más sencillo con escritura).

## 1. Una sola responsabilidad

Antes de escribir código, una frase: «este servicio es el dueño de ___». Si la frase lleva una «y», son dos servicios. Un servicio es dueño
de sus tablas y **no lee las de otro**: lo que no es suyo se lo pide por HTTP (paso 4).

## 2. Tablas, permisos y parámetros

Un archivo SQL nuevo en `bloque_c/sql/` (`10_…`, `11_…`), idempotente: `CREATE TABLE IF NOT EXISTS`, `ON CONFLICT DO NOTHING`, y los
permisos nuevos otorgados solo si una marca en `web_migracion` no existe (así una migración repetida no devuelve permisos que el
administrador retiró). Agregarlo a `SCRIPTS` en `servicios/migrar.py`. Reglas que ya cumplen las tablas existentes:

- Nada de constantes en el código: los umbrales viven en `configuracion` y se leen con `parametro()`.
- Toda tabla de negocio con trigger `fn_auditar_cambio` (RN30).
- Llaves foráneas con **nombre** (`fk_pp_producto`) para poder traducir el error en `comun/datos.py` (`TRADUCCIONES`).

## 3. El servicio

`servicios/<nombre>/app.py` (más `__init__.py` y `Dockerfile`, que se copia de otro servicio cambiando nombre y puerto):

```python
app = crear_app("<nombre>", "Microhubs · <Título>", "<descripción>", <puerto>)

@app.get(f"{P}/<recurso>")
@requiere("<recurso>.ver")                  # al menos uno de los permisos
def lista():
    pagina, por, desde = leer_paginacion()
    ...
    return lista(filas, paginacion(pagina, por, total), "<item>", "<raiz>", transformar)
```

Lo que `crear_app` ya da: JWT con sesión en Redis, JSON o XML según `Accept`, errores con traza, límite de consumo, registro en MongoDB,
`/salud` y Swagger. Ayudas de `comun/base.py`: `leer_cuerpo`, `validar` + `Campo` (`comun/validar.py`), `limitar_microhub` (operador y
supervisor solo ven el suyo), `documentar` (OpenAPI). El **orden de las llaves** de cada respuesta es el orden del XSD.

## 4. Hablar con otro servicio

```python
from comun.clientes import exigir, mapa
alertas = exigir("inventario", "GET", "inventario/alertas", params={"microhub_id": 1})   # error del otro = error propio
productos = mapa("productos", "productos")                                               # {id: registro}, con caché
```

Lleva el JWT y la traza de quien hizo la petición, así que el otro servicio aplica sus permisos. Si el otro no responde, `llamar` lanza 503.
Si la operación puede quedar a medias, guardar primero y reintentar con una `operacion_uuid` (ver `abastecimiento/recepcion`).

## 5. Puerto, Compose y portal

- `comun/config.py` → `PUERTOS`.
- `docker-compose.integrado.yml` → un bloque como el de `inventario` (`<<: *servicio`, `build`, `environment: *entorno`, `ports`).
- `sistema_web/integracion.py` → `PUERTOS`, para que el tablero de Microservicios lo vigile.
- `servicios/pruebas/evidencias.py` y `test_web_integracion.py` → su propio `PUERTOS`.

## 6. Contrato XML y JSON

Describir los tipos y los ejemplos en `servicios/contratos/olaN.py` (copiar `ola1.py`) y correr:

```bash
cd servicios && python contratos/generar.py olaN
```

Escribe el XSD, un ejemplo XML y uno JSON por cada respuesta o cuerpo, y comprueba que **cada XML valida contra el conjunto completo de
XSD**. Después agregar el nombre del XSD a `ARCHIVOS` en `comun/esquemas.py`. El `documentar(...)` del servicio nombra esos ejemplos
(`respuestas={200: ("…", "Existencia.ok")}`).

## 7. Pruebas y evidencia

1. `pruebas/test_unitarias.py`: la lógica pura (sin base de datos) y que el servicio esté en `SERVICIOS`.
2. `pruebas/test_ola1.py` o un archivo nuevo: un recorrido contra PostgreSQL y Redis reales, con los permisos de cada perfil, JSON y XML.
3. `pruebas/evidencias_ola1.py` o uno nuevo: casos de petición y respuesta con lo que quedó en PostgreSQL. Cada operación debe tener al
   menos un caso; `python pruebas/generar_inventario.py` lo comprueba (las que no tienen caso salen en la lista «sin caso»).

## 8. Documentos

`servicios/README.md` (tabla y responsabilidad), `servicios/INVENTARIO_ENDPOINTS.md` (lo escribe `generar_inventario.py`), y al cerrar la
ola, el reporte técnico y la presentación.
