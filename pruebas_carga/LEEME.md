# Pruebas de carga con Locust

Contenido de la carpeta:

- `locustfile.py`: seis perfiles de usuario y una forma de carga por escalones (estrés y recuperación).
- `muestrear_recursos.py`: toma la CPU y la memoria del equipo cada 5 s mientras corre la prueba.
- `resumir.py`: junta los CSV de Locust en `evidencias/carga/RESULTADOS.md`.

Las tablas completas de la corrida del 26 de noviembre de 2026 están en
[`evidencias/carga/RESULTADOS.md`](../evidencias/carga/RESULTADOS.md). Ahí también quedaron el reporte HTML de Locust y los CSV de cada escenario.

## Perfiles

| Perfil | Peso | Simula | Peticiones |
|---|---|---|---|
| `ClienteConsultando` | 40 % | 5 000 clientes distintos en el web o la app | búsqueda y detalle en el catálogo, zonas, microhubs, sus pedidos, sus avisos |
| `RepartidorAndroid` | 20 % | la app del repartidor (JSON) | sus entregas, detalle, **GPS en lotes de 10 puntos** a MongoDB, perfil |
| `OperadorRegistrando` | 15 % | operador del MH-01 | inventario, alertas, pedidos del microhub, **solicitud de reposición** |
| `PlaneadorEscritorio` | 10 % | la app de escritorio (**XML**) | reportes en XML, punto de equilibrio, **simulación Monte Carlo** (202, en segundo plano) |
| `AdministradorPanel` | 10 % | administrador mirando el panel | estado y disponibilidad del monitoreo, bitácora |
| `ProcesoAutomatico` | 5 % | una app que recupera la red | lotes de sincronización y **reenvío del mismo lote** (no debe duplicar) |

Cada usuario inicia sesión y espera entre 1 y 8 s entre acciones, según el perfil. Si su token vence (15 min), vuelve a entrar, como lo
haría la app.

## Cómo se corrió

```bash
python bloque_c/scripts/generar_volumen.py --pedidos 100000 --clientes 5000       # datos de alto volumen y los 5 000 clientes
python servicios/pruebas/preparar_entregas.py --correo repartidor1@codex.mx --cantidad 6
python servicios/pruebas/preparar_entregas.py --correo repartidor2@codex.mx --cantidad 6

# Capacidad: sin el límite por IP (todo Locust sale de una sola IP; ver «Límites de consumo»)
export LIMITE_POR_MINUTO=1000000 LIMITE_LOGIN_POR_MINUTO=1000000      # y reiniciar los servicios
locust -f pruebas_carga/locustfile.py --headless --host http://localhost -u 50  -r 5  -t 180s --csv evidencias/carga/normal --csv-full-history --html evidencias/carga/normal.html
locust -f pruebas_carga/locustfile.py --headless --host http://localhost -u 150 -r 10 -t 180s --csv evidencias/carga/alta   --csv-full-history --html evidencias/carga/alta.html
FORMA=escalones MAX_USUARIOS=500 PASO_USUARIOS=50 ESCALON_S=40 \
locust -f pruebas_carga/locustfile.py --headless --host http://localhost --csv evidencias/carga/estres_recuperacion --csv-full-history --html evidencias/carga/estres_recuperacion.html

# Protección: con los límites normales (240 por minuto y 30 inicios de sesión por minuto)
unset LIMITE_POR_MINUTO LIMITE_LOGIN_POR_MINUTO                       # y reiniciar los servicios
locust -f pruebas_carga/locustfile.py --headless --host http://localhost -u 80 -r 10 -t 150s --csv evidencias/carga/proteccion_limites --csv-full-history --html evidencias/carga/proteccion_limites.html

python pruebas_carga/resumir.py
```

**Ambiente de esta corrida:** una estación Linux con **2 vCPU y 7 GB**, con los 26 servicios, el web, PostgreSQL 16, MongoDB 7, Redis 7
**y Locust en la misma máquina**, sobre la base con 100 000 pedidos y 1.4 millones de puntos GPS. La VM de GCP (e2-standard-4) tiene
el doble de CPU, así que estos números son un piso.

**En la nube** se corre desde otra computadora, contra Nginx:

```bash
export MICROHUBS_PLANTILLA="https://34-51-89-253.sslip.io/servicios/{servicio}" MICROHUBS_CLAVE="<la del .env de la VM>"
locust -f pruebas_carga/locustfile.py --headless --host https://34-51-89-253.sslip.io -u 150 -r 10 -t 180s --csv evidencias/carga/nube_alta --html evidencias/carga/nube_alta.html
```

Para medir capacidad en la nube hay que hacer dos cosas, durante la prueba y no después:

1. Poner `LIMITE_POR_MINUTO=1000000` y `LIMITE_LOGIN_POR_MINUTO=1000000` en el `.env` y volver a levantar los contenedores.
2. Subir `rate=20r/s` de Nginx en `nginx-microhubs.conf`.

Al terminar se quitan las dos cosas.

## Resultados

| Escenario | Usuarios | RPS | Mediana | p95 | p99 | Errores |
|---|---|---|---|---|---|---|
| Carga normal | 50 | 15.9 | 17 ms | 75 ms | 290 ms | 0 % |
| Carga alta | 150 | 47.0 | 22 ms | 110 ms | 710 ms | 0 % |
| Estrés (escalones de 50 hasta 500) | 500 | 65.8 promedio, **98 pico** | 96 ms | 5.6 s | 9.4 s | 0.20 % (503) |
| Protección (límites activos) | 80 | 16.9 | 17 ms | 98 ms | 320 ms | 12.5 % (429 a propósito) |

**Hasta 250 usuarios el sistema escala casi en línea recta.** Cada 50 usuarios suman unas 15 peticiones/s y el p95 del tramo estable
se queda entre 54 y 210 ms.

**Saturación desde 300–350 usuarios.** El rendimiento se estanca en ~95 peticiones/s y la CPU del equipo llega al 100 %
(`estres_recuperacion_recursos.csv`). Desde ahí el p95 crece de 0.8 s a 8 s. A partir de 450 usuarios aparecen los primeros **503**, en
los reportes y la simulación: son las llamadas en cadena (reportes → pedidos, simulación → punto de equilibrio y capacidad) que no
reciben respuesta en los 4 s de `MICROSERVICIOS_TIEMPO`. **Ningún 500**: el servicio dice que no pudo y no guarda nada a medias.

**Recuperación en 8 s.** Al bajar de 500 a 50 usuarios, el p95 vuelve a su nivel normal (≤ 2 × 54 ms) 8 s después. No se reinició nada
y no quedaron errores.

**Endpoints más lentos:**

- `POST auth/login`. Es lento a propósito: bcrypt cuesta CPU, unos 300 ms sin carga y 2 s con 150 usuarios que entran al mismo
  tiempo. Por eso cada escalón empieza con un pico de p95.
- Los reportes (`pedidos_por_dia`, `ventas_por_producto`), porque arman su respuesta llamando a pedidos.
- Con saturación, las listas de pedidos: el servicio de pedidos, con 2 workers síncronos, es el primero en hacer fila.

**Protección.** Con los límites normales, la ráfaga de 80 inicios de sesión desde una sola IP recibe **429 con `Retry-After`** después
del número 30 de cada minuto. El catálogo también responde 429 después de 240 peticiones por minuto. Los usuarios rechazados vuelven a
intentar al minuto y entran.

## Qué se corrigió y qué queda

- **Corregido: la IP del cliente detrás de Nginx.** Los servicios y el web tomaban la IP de la conexión. En la nube esa IP es la de
  Nginx, así que **todos los usuarios de Internet compartían un solo límite de 240 peticiones por minuto por servicio y 30 inicios de
  sesión por minuto**, y la bitácora guardaba la IP del proxy. Bastaba con que 31 alumnos entraran en el mismo minuto para que
  alguno recibiera 429. Ahora, con `DETRAS_DE_PROXY=1` (lo pone `instalar_vm.sh`), la IP sale del `X-Forwarded-For` que agrega Nginx.
  Se probó: dos IPs distintas quedan en la bitácora como dos IPs y cuentan por separado. Los servicios solo escuchan en 127.0.0.1, así
  que nadie más que Nginx puede mandar ese encabezado.
- **Corregido antes de estas corridas** (con los datos de alto volumen): la lista de pedidos, los resúmenes, las ventas y la
  sincronización de demanda. Ver [`evidencias/volumen/LEEME.md`](../evidencias/volumen/LEEME.md). Las corridas de Locust se hicieron
  con una versión en la que la caché de resúmenes también servía la página 1. Después se cambió para que la página 1 siempre se
  calcule, porque así lo pidieron las pruebas de reportes. Los reportes por servicio pueden costar ahora unos 100–200 ms más por
  llamada: conviene repetir la corrida «alta» en la VM.
- **Recomendación para la VM:** subir a 4 los workers de pedidos, productos y auth (`-w 4`), o usar workers `gthread`. Son los que
  hacen fila primero.
- **Pendiente:** los reportes no tienen un tiempo límite total. Con saturación, una cadena de llamadas de 4 s cada una puede tardar más
  de un minuto en responder 503. Un plazo total por petición (por ejemplo, 10 s) o un cortacircuitos en `comun/clientes.py` haría que
  fallaran antes.
