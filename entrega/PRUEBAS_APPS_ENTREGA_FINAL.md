# Apps de la entrega final · qué se hizo, qué se probó y qué falta

**Rama:** `mauro-apps` (sale de `ruth-entrega-final`, commit `5b8cca0`) · **Fecha:** 26 de noviembre de 2026 (corridas finales a las 21:25, hora de Monterrey) ·
**Quién:** Claude, trabajando para Mauro en un entorno Linux en la nube. Mauro compila, prueba en su PC con Windows y sube la rama.

Este archivo alimenta la bitácora. Todo lo que dice «aprobado» se ejecutó; las salidas completas están en
[`salidas_pruebas/`](salidas_pruebas/). Lo que no se pudo ejecutar aquí está en la sección «Lo que NO se comprobó».

## 1. Qué se hizo (commits)

| Commit | Qué |
|---|---|
| `b6e047d` | **Android, lógica sin red y avisos.** Cola en archivos privados de la app; `operacion_uuid` y `creada_en` (con zona) fijos desde que se crea la operación; el uuid del cierre es el mismo `id_cliente_local`; la foto se sube primero a `POST /documentos` (5107) y su id va en `evidencia_ids`; luego `POST /sincronizacion/lotes` (5125) en lotes de hasta 200; aplicada sale, conflicto y rechazada se muestran y no se reintentan, pendiente se reenvía igual. Copias de la lista y del detalle para trabajar sin señal. Avisos (5124): bandeja, conteo, leer y leer todos (leer sin red va a la cola). 21 pruebas. |
| `c601935` | **Android, pantallas.** Avisos (con el número de no leídos en el inicio), «Sin enviar» (estado y motivo de cada operación, «Enviar ahora»), formulario que guarda sin red, sincronización sola al volver la red (aviso de conectividad del sistema), aviso al salir con algo pendiente. |
| `3a10e06` | **Escritorio, lógica.** `Api.Download` (descarga binaria aparte: tipo, firma del archivo y SHA-256 del encabezado `X-Reporte-SHA256`; errores en XML validados), raíz esperada en `Api.Call`, puertos 5116–5121 y 5123. `Tablas`, `Modulos` y `Plantillas` sin Windows Forms. Proyecto de pruebas multiplataforma. 37 comprobaciones nuevas sin red y 68 contra los servicios. |
| `bbdd10d` | **Escritorio, ventanas.** Reportes (catálogo, indicadores, tabla, gráfica, exportaciones, CSV/Excel/PDF) y una ventana por módulo: cobertura, rutas, costos, capacidad, punto de equilibrio y simulación. |
| `8af74eb` | **Android contra los servicios reales:** cierre sin red enviado por la sincronización, reenvío duplicado, uuid reutilizado rechazado, conflicto; avisos. |
| (este) | `entrega/`: este registro, salidas de las pruebas, formato de usabilidad, guion del video e instrucciones de instaladores. |

Solo se tocaron `app_movil/`, `app_escritorio/` y `entrega/`. No hay claves, llaves, keystores ni binarios en los commits.

## 2. Entorno donde se probó

- Linux (Ubuntu 24.04) sin Docker. Los **26 microservicios** de esta rama corriendo con gunicorn, igual que en sus contenedores, más
  PostgreSQL 16, MongoDB 7 y Redis. La base se creó desde cero con `bloque_c/sql/01…12` y `bloque_c/mongo/01…03` **de esta rama**.
- Entregas en ruta para `repartidor1@codex.mx` con `servicios/pruebas/preparar_entregas.py`; para rutas, 4 pedidos «listos» en el microhub 1
  con un script local que usa las mismas funciones de ese archivo (no se sube: `servicios/` no es de esta parte; ver la sección 6).
- **Android (JVM):** `kotlinc` 2.1.0, JUnit 4.13.2 y `org.json` compilado de su fuente (la misma biblioteca que usa Gradle en las pruebas),
  porque aquí no se puede descargar de Google Maven ni de Maven Central. Es la misma lógica y las mismas pruebas que corre
  `gradle testDebugUnitTest`, compiladas sin Gradle.
- **Escritorio:** SDK de .NET 8.0.134 para Linux. Windows Forms no existe en Linux, así que las pruebas corren con el proyecto
  `pruebas/multiplataforma` (todo menos abrir la ventana).

## 3. Qué se ejecutó y su resultado

| Prueba | Comando | Resultado | Salida |
|---|---|---|---|
| Android, JVM sin red | `testDebugUnitTest` equivalente (ver 2) | **67 aprobadas**, 5 omitidas a propósito (las de backend real, sin variables) | `android_jvm_sin_red.txt` |
| Android, JVM contra los servicios reales | `MICROHUBS_BACKEND_HOST=127.0.0.1 MICROHUBS_CLAVE=…` | **72 aprobadas, 0 omitidas**: las 67 anteriores más las 5 de backend real (las 3 que el registro anterior dejó omitidas y 2 nuevas) | `android_jvm_backend_real.txt` |
| Escritorio sin red | `dotnet run --project pruebas/multiplataforma/…` | **71 comprobaciones aprobadas** | `escritorio_sin_red.txt` |
| Escritorio contra los servicios reales | `MICROHUBS_BACKEND=http://localhost MICROHUBS_CLAVE=…` | **168 aprobadas** (71 + las 29 de antes + 68 nuevas) | `escritorio_backend_real.txt` |
| XSD con validador independiente | `python -m unittest discover -s pruebas -v` | **10 aprobadas** (una fallaba en la rama base; ver 5.5) | `escritorio_xsd_lxml.txt` |
| Tipos de las pantallas | kotlinc contra `android.jar` API 35; compilador de .NET 8 contra el Windows Forms de Mono | Android sin errores; escritorio solo con el error esperado de `PlaceholderText` (ver el archivo) | `verificacion_tipos.txt` |

Contra los servicios reales, en particular:
- **Android:** un cierre guardado sin red se envió con la sincronización: la foto llegó a MongoDB por `documentos`, el lote aplicó el
  recorrido (seguimiento) y el cierre (entregas), y la entrega dejó de aparecer en «Mis entregas». Reenviar el mismo sobre dio
  *duplicada* (aplicada, sin repetir nada); el mismo uuid con otra evidencia, *rechazada* (`UUID_REUTILIZADO`); otro cierre de la entrega ya
  cerrada, *conflicto* con el mensaje del servidor. La bandeja de avisos trajo los avisos de asignación y marcar uno bajó el conteo.
- **Escritorio:** las 24 consultas de las seis pantallas de análisis devolvieron XML válido con la raíz esperada; detalle de capacidad desde
  la fila; evaluar ubicación, simular capacidad y sensibilidad con las plantillas oficiales; dos escenarios de equilibrio guardados, abiertos y
  comparados; una simulación creada, terminada y repetida con **la misma huella**; rutas: comparar métodos, proponer y guardar, abrir y
  cancelar; alta y baja de un concepto de costo; **los 8 reportes** con su tabla y su gráfica; indicadores; las **tres descargas** (CSV
  1,544 bytes, XLSX 6,618 bytes, PDF 5,621 bytes en la última corrida) con SHA-256 verificado y registradas en la bitácora de
  exportaciones; 404 y 400 en XML; el auditor descarga y consulta costos, y en simulación recibe 403.

## 4. Lo que NO se comprobó aquí (y cómo hacerlo en la PC de Mauro)

No se pudo porque este entorno no llega a Google Maven, Maven Central, plugins de Gradle, NuGet ni Docker Hub, y no tiene Windows ni emulador:

1. **Compilar con Gradle, lint y generar la APK:** `cd app_movil; .\build.ps1` (debe terminar con las pruebas en verde y lint sin errores).
2. **Pruebas JVM con Gradle contra Docker:** levantar `docker-compose.integrado.yml`, preparar 3 entregas
   (`docker compose -f docker-compose.integrado.yml exec entregas python pruebas/preparar_entregas.py --cantidad 3`) y
   `$env:MICROHUBS_BACKEND_HOST='127.0.0.1'; $env:MICROHUBS_CLAVE='…'; gradle testDebugUnitTest --tests "*BackendRealTest*"`.
3. **Pruebas en el emulador** (`connectedDebugAndroidTest`, ahora también recorre «Avisos») y **ensayo manual sin red**: modo avión, cerrar
   una entrega, ver «Sin enviar», quitar el modo avión y ver que se envía sola. Esto es lo más importante de probar a mano: el aviso de
   conectividad del sistema y la cámara real solo existen en el teléfono.
4. **Escritorio en Windows:** `dotnet build Microhubs.csproj` y `dotnet run --project pruebas/Microhubs.Pruebas.csproj` (sin red: 71 + 3 de
   ventanas; con las variables: 168 + 3). Abrir cada ventana nueva a mano una vez.
5. **Instaladores** y su publicación: [`INSTALADORES.md`](INSTALADORES.md).
6. **Capturas** (abajo). No se generaron aquí: no hay pantalla de Android ni de Windows en este entorno, y no se inventan.
7. **Nube:** no se probó contra la VM (certificado autofirmado; la consigna es probar en local y no desactivar la validación).
   **Actualización del 27 de noviembre:** la nube ya tiene certificado de Let's Encrypt y las apps enrutan por nombre cuando el servidor trae
   ruta. Verificado en Windows: Android 68 unitarias y 5 contra los servicios por puertos y por una puerta única como la de la nube; escritorio
   76 sin red y 173 contra los servicios por las dos vías. Contra la nube, el código de ambas apps recibió el 401 del contrato **sin
   credenciales**; falta iniciar sesión de verdad desde un teléfono y una PC.

### Capturas (`entrega/capturas/`)

Estado al 27 de noviembre. Todas se tomaron en la PC de Mauro; ninguna muestra claves.

| Archivo | Qué se ve | Estado |
|---|---|---|
| `movil_avisos.png` | Bandeja de avisos (emulador API 36 contra los servicios locales, sale de `connectedDebugAndroidTest`) | ✅ |
| `movil_sin_red_guardado.png`, `movil_sin_enviar.png`, `movil_sincronizado.png`, `movil_conflicto.png` | Ensayo sin red en un teléfono | ❌ **No se hizo:** el equipo no tiene un Android físico (ver 7.3) |
| `escritorio_reportes.png` | Catálogo de los 8 reportes | ✅ |
| `escritorio_pdf.png` | El PDF «Pedidos por día» descargado (7 pedidos, 46 unidades, 1,080.80), página convertida a imagen | ✅ |
| `escritorio_equilibrio.png` | Punto de equilibrio · Calcular: escenario 3 guardado, equilibrio mensual 11,538.46 | ✅ (tomada antes del arreglo 7.4.2: la tabla grande muestra los supuestos) |
| `escritorio_simulacion.png` | Simulación · una corrida de 200 réplicas y 30 días, aún `en_cola` en ese momento | ✅ (la prueba automática sí la ve terminar) |
| `escritorio_rutas.png` | Rutas · Comparar métodos: 4 métodos, el mejor «TSP exacto» (2.36 km, 15.7 % de mejora) | ✅ |
| `escritorio_rutas_aviso_pedidos.png` | El aviso legible cuando la lista trae pedidos que no están listos (antes tronaba, 7.4.1) | ✅ extra |
| `escritorio_cobertura.png`, `escritorio_costos.png`, `escritorio_capacidad.png` | Zonas (4), conceptos (21) y microhubs (4) | ✅ extra |
| `nube_escritorio_reportes.png`, `nube_escritorio_pdf.png`, `nube_escritorio_rutas.png` | Las mismas pantallas contra la nube (en la de rutas se ve el servidor `https://34-51-89-253.sslip.io/servicios`) | ✅ |
| `nube_movil_inicio.png`, `nube_movil_entregas.png`, `nube_movil_entrega_foto_gps.png` | Android en el emulador contra la nube: inicio (54 avisos), 8 paradas y una entrega con la foto ya capturada | ✅ (recortes de capturas de pantalla de la PC) |

## 5. Problemas encontrados (para la bitácora)

1. **Editor de plantillas del escritorio (existía antes):** en un cuerpo con una lista (`<pedido_ids><id>…</id><id>…</id></pedido_ids>`) todos
   los `<id>` compartían la misma clave, así que al guardar todos tomaban el valor del último cuadro. Ahora una lista se edita como «1, 2, 3» y
   se rearma; vacía, no se manda. Prueba: «Plantilla: la lista se rearma…».
2. **Campos nulos (`xsi:nil`):** al darle valor a un campo que venía nulo en el ejemplo (p. ej. `capacidad_fisica`) seguía marcado como nulo y
   el XSD lo rechazaba; y al vaciarlo de nuevo ya no se podía volver a nulo. Se conserva el atributo en `false`/`true`. Lo encontró la prueba.
3. **Reportes y filtros:** cada reporte rechaza (400) un filtro que no admite (p. ej. el inventario no depende del periodo). La app manda
   solo los que el catálogo dice que admite el reporte elegido.
4. **Ids de simulación:** son UUID, no números; las acciones sobre una fila solo aceptaban enteros. Ahora aceptan entero o UUID (y nada más).
5. **`pruebas/test_contratos.py` fallaba ya en la rama base:** esperaba exactamente los 9 XSD originales y hoy hay 30. Ahora exige los
   del escritorio y que carguen todos.
6. **Mismo uuid, otro contenido:** el servicio guarda una huella del sobre (tipo, datos y `creada_en`); si la foto se volviera a subir y
   cambiara su id, el mismo uuid se rechazaría (`UUID_REUTILIZADO`). Por eso el id de la evidencia se fija una sola vez, antes del primer
   envío, y una operación sin foto subida no sale en ningún lote. Comprobado contra el servicio real.
7. **Rutas sin pedidos listos:** en una base recién creada no hay pedidos «listos» sin entrega, y comparar o proponer rutas necesita al menos
   dos; la prueba lo dice y omite esa parte si no los hay.
8. **Límite conocido:** si una foto se sube pero la respuesta se pierde, al reintentar se sube otra vez (queda un documento huérfano en
   MongoDB; el cierre usa solo el último id).

## 6. Sugerencias para la parte de servicios (no se tocaron)

- `servicios/pruebas/preparar_entregas.py` podría tener una opción `--solo-listos --microhub N` que deje pedidos listos sin entrega, para
  demostrar y probar rutas (aquí se hizo con un script local que importa sus funciones).
- En la prueba de carga, `GET /reportes/indicadores` y `comparacion_microhubs` son los más lentos (p95 de 43 s y 37 s): la ventana de
  reportes del escritorio los llama solo cuando la persona pulsa el botón.

## 7. Pruebas en la PC de Mauro (Windows, 27 de noviembre de 2026)

Rama `mauro-pendientes` sobre `main` con el PR #21 (las apps ya enrutan hacia la nube). Docker Desktop con `docker-compose.integrado.yml`
reconstruido después de #21: 26 servicios, portal y las 3 bases sanos. Datos: entregas 141–143 (pedidos 163–165) para `repartidor1` con
`preparar_entregas.py --cantidad 3` y pedidos listos 166–169 en el microhub 1 con `pruebas.preparar_listos --cantidad 4 --microhub 1`.
Salidas completas en `entrega/_local/` de la PC (no se suben: traen rutas locales).

### 7.1 Resultados

| Prueba | Resultado |
|---|---|
| Android: `build.ps1` (Gradle, lint, APK, unitarias) | ✅ 68 aprobadas, 5 omitidas (las de backend real), lint sin errores |
| Android: `connectedDebugAndroidTest` en emulador (AVD `Microhubs_API_36`, imagen `android-36` google_apis x86_64, WHPX) | ✅ **7/7** en 24 s, contra los servicios locales en `10.0.2.2` |
| Escritorio: `dotnet publish` self-contained win-x64 | ✅ |
| Escritorio: pruebas sin red (multiplataforma) | ✅ 76 (eran 73; +3 de los arreglos de 7.4) |
| Escritorio: pruebas contra los servicios locales (`MICROHUBS_BACKEND=http://localhost`) | ✅ **176/176** (eran 173) |
| Escritorio: abrir a mano cada ventana nueva | ✅ reportes, PDF, cobertura, rutas, costos, capacidad, punto de equilibrio y simulación (capturas arriba) |
| Instaladores: `entrega/instaladores.ps1` | ✅ generados; ver [`instaladores_generados.md`](instaladores_generados.md). **Se regeneran antes del Release** porque 7.4 cambió las apps |

### 7.2 Nube (`https://34-51-89-253.sslip.io/servicios`, certificado de Let's Encrypt, validación de certificados activa)

| App · cuenta | Qué funcionó | Qué no |
|---|---|---|
| Android en el emulador · `repartidor1` | Inicio de sesión, inicio con 54 avisos, «Mis entregas» con 8 paradas, foto de evidencia (cámara emulada, 25 KB) y GPS | El lector de QR cerraba la app (7.4.3). Arreglado; no se volvió a probar el cierre completo con QR en el emulador |
| Escritorio · `planeador` | Inicio de sesión; «Pedidos por día» con 30 días (28-oct a 27-nov); PDF de 2 páginas descargado (generado 02:13:37); Comparar métodos con los 4 pedidos listos de la nube: mejor «Vecino más cercano + 2-opt» y «TSP exacto» empatados (3.09 km, 18 % de mejora) | Nada |

### 7.3 Lo que no se hizo

- **Ensayo sin red en un teléfono real** (modo avión → «Sin enviar» → se envía sola): el equipo no tiene un Android físico. La lógica está
  cubierta por las pruebas JVM y contra los servicios (sección 3) y, en el emulador, `elCierrePendienteSobreviveAlReinicioDeLaApp`; pero el
  aviso de conectividad del sistema y la cámara real no se probaron en un dispositivo.
- **Cierre de una entrega con QR en el emulador:** después del arreglo 7.4.3 no se repitió (habría que poner el QR en la escena virtual de la
  cámara del emulador). La prueba `elLectorDeQrAbreSinCerrarLaApp` abre el lector en el emulador.
- **Usabilidad con 3 personas y video:** pendientes (ver `FORMATO_USABILIDAD.md` y `GUION_VIDEO.md`).

### 7.4 Problemas encontrados y arreglados

1. **Escritorio · Comparar métodos tronaba** con «An item with the same key has already been added. Key: pedido_ids». La plantilla trae
   pedidos de ejemplo (163, 168, 169, 176); el servicio responde 422 con **un `<detalle>` por cada pedido** no listo, todos con el campo
   `pedido_ids`, y `Api.ToError` los metía en un diccionario. Ahora se juntan por campo («…; …»). Prueba nueva sin red. Captura:
   `escritorio_rutas_aviso_pedidos.png`.
2. **Escritorio · la tabla principal mostraba los supuestos** en vez del resultado cuando la respuesta traía más supuestos que filas
   (Comparar métodos: 6 supuestos y 4 métodos; también en punto de equilibrio y otras). `Tablas.Coleccion` elegía la colección más grande;
   ahora `supuestos_usados` solo es la tabla si no hay otra. **La prueba contra el servicio contaba los 6 supuestos como «6 métodos»** (falso
   positivo): ahora exige la columna `metodo`. 2 pruebas nuevas sin red; se comprobó que la nueva falla sin el arreglo.
3. **Android · el lector de QR cerraba la app** en cualquier dispositivo: `NoClassDefFoundError: androidx/core/content/ContextCompat` en
   `com.journeyapps.barcodescanner.CaptureManager`. `zxing-android-embedded` 4.3.0 usa `ContextCompat` pero no trae `androidx.core`, y la app
   no lo tenía. Se agregó `androidx.core:core:1.13.1` y la prueba de emulador `elLectorDeQrAbreSinCerrarLaApp`. Ninguna prueba abría el lector;
   se encontró al probar a mano contra la nube.

## 8. Lo que faltaba del enunciado (27 de noviembre, rama `mauro-faltantes`)

Al revisar el proyecto contra el enunciado del Proyecto 11 faltaban funciones de las apps y dos algoritmos. Se hicieron en el entorno de
Claude (Linux, los 26 servicios con la base recreada desde `bloque_c/sql/01…16`) y después se comprobaron en la PC de Mauro (abajo).

| Qué | Dónde | Pruebas (todas aprobadas) |
|---|---|---|
| Escritorio para operadores: inventario, preparación, despacho (asignar y **manifiesto**), surtido; cambiar personal | `app_escritorio/Modulos.cs`, `Operacion.cs`, `Ventanas.cs` | sin red **89** (eran 76); contra los servicios **213** (con el operador: preparar, marcar listo, asignar, manifiesto, movimiento de inventario) |
| Botones según los **permisos** de la sesión (no solo el rol) | `Api.cs`, `Accion.Habilitada` | incluidas arriba |
| **Colas M/M/1 y M/M/c** (Erlang C) | `servicios/comun/colas.py`, `POST capacidad/colas`, escritorio «Colas M/M/c» | 7 unitarias con valores calculados a mano; 1 de servicio (JSON, XML, permisos) |
| Contrato XML para cambiar el estado y asignar paradas desde el escritorio | `servicios/contratos/ola5.py` → `operacion.xsd`, `colas.xsd` | los ejemplos validan; validador lxml 10/10 |
| **Android cliente:** catálogo y catálogo ligero sin red, carrito, pedido (sin red por sincronización), mis pedidos, cancelar, confirmar recepción | `app_movil/.../Cliente.kt`, `MainActivity.kt` | JVM **85** (11 nuevas); `flujoDelCliente` contra los servicios reales |
| **Navegar** del repartidor (`geo:`) | `Entregas.kt` (`destinoMapa`), `MainActivity.kt` | JVM |
| Servicios: `POST entregas/recepciones`, tipo `pedido_nuevo` en sincronización, `16_apps_cliente.sql` | `servicios/entregas`, `servicios/sincronizacion`, `bloque_c/sql` | `test_apps_cliente` 4/4; suites completas sin fallas: unitarias 37 + 72, contrato 7, ola1 24, ola2 103, ola3 74, ola4 12 |

**En la PC de Mauro (27-nov, 03:25–03:32, rama `mauro-faltantes`):** Docker reconstruido (aplicó `16_apps_cliente.sql`); Android
`build.ps1` con lint y unitarias sin fallas (79 aprobadas, 6 omitidas por no tener las variables del backend); `connectedDebugAndroidTest`
**8/8** en el emulador API 36; escritorio en Windows **218/218** contra los servicios, incluido el recorrido del operador (pedido 29: a
preparación, listo, asignado al repartidor 7 y manifiesto de 7 paradas). A mano: el cliente compró desde el emulador y vio su pedido en
«Mis pedidos»; el operador generó el manifiesto y calculó las colas M/M/c en el escritorio. Todo funcionó.

**Qué no se hizo:** perfil **proveedor** con cuenta (sería un portal propio); el ensayo sin red en teléfono real; las pantallas del cliente
no tienen prueba automática de emulador (las cubren la lógica en JVM, el recorrido real `flujoDelCliente` y la prueba a mano).

