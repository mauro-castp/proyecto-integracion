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

### Capturas que faltan (guardar en `entrega/capturas/`)

| Archivo sugerido | Qué debe verse |
|---|---|
| `movil_avisos.png` | Bandeja de avisos con «Nueva entrega asignada» (sale sola en `connectedDebugAndroidTest`: `13_avisos_real`) |
| `movil_sin_red_guardado.png` | Barra «Sin conexión» y el formulario con «Guardar resultado (sin red)» |
| `movil_sin_enviar.png` | Pantalla «Sin enviar» con la operación «Por enviar» |
| `movil_sincronizado.png` | De vuelta «En línea» y el aviso «… enviada(s)» |
| `movil_conflicto.png` (opcional) | Una operación en «Conflicto» con el mensaje del servidor |
| `escritorio_reportes.png` | Ventana Reportes con «Pedidos por día» y su tabla con totales |
| `escritorio_pdf.png` | El PDF descargado abierto |
| `escritorio_equilibrio.png` | Punto de equilibrio · Calcular (tabla de pasos y resumen con la decisión) |
| `escritorio_simulacion.png` | Simulación · Ver ejecución terminada |
| `escritorio_rutas.png` | Rutas · Comparar métodos |

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
