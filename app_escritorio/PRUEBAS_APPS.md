# Verificación de las apps del PR #3

Se descargaron Gradle 8.11.1 y el SDK oficial .NET 8.0.425 dentro de las carpetas `.tools/`, ignoradas por Git. El backend todavía no está publicado en el repositorio; estas comprobaciones no requieren los microservicios de Claude.

## Escritorio

- Compilación .NET: aprobada, cero errores y cero advertencias.
- 17 comprobaciones de C#: login de ejemplo, captura/modificación de candidatos, simulación del ID seleccionado, catálogo y pedidos XML, rechazo de XML incompleto y DTD, JWT vigente/vencido, preservación de query/puerto y `Accept`, renovación ante 401, rechazo de JSON, limpieza de sesión y construcción de Windows Forms.
- 5 pruebas adicionales de contratos XSD aprobadas.
- Publicación autónoma para Windows x64 generada en `bin/Publicacion/`; incluye el runtime y se inicia con `Microhubs.exe`. Para moverla a otro equipo, copiar **toda esa carpeta**, no solo el ejecutable.

Corrección: una sesión inválida ahora deja las credenciales vacías; antes se asignaban antes de comprobar la expiración.

Repetir:

```powershell
dotnet build Microhubs.csproj
dotnet run --project pruebas/Microhubs.Pruebas.csproj
python -m unittest discover -s pruebas -v
dotnet publish Microhubs.csproj -c Release -r win-x64 --self-contained true -o bin/Publicacion
```

En el equipo de implementación puede sustituirse `dotnet` por `./.tools/dotnet/dotnet.exe`.

## Android

- APK debug generado en `app/build/outputs/apk/debug/app-debug.apk`.
- 12 pruebas unitarias aprobadas: sesión/perfil demo, listado paginado, actualización, pedidos, documentos, limpieza de credenciales, rutas inválidas, ausencia de persistencia demo, URL/puerto/JSON, renovación 401, rechazo de HTTP y de XML.
- Lint: cero errores y 14 advertencias (versiones, textos, APIs y preferencias). Se mantienen como tareas de mantenimiento; no se afirma que el análisis esté libre de advertencias.
- 4 pruebas instrumentadas aprobadas en emulador Android 14: cifrado y restauración con Android Keystore, descarte de datos corruptos, arranque de Activity y flujo en pantalla de login, listado de entregas y cierre de sesión.

Corrección: el formulario usaba la propiedad `layout` de EditText por ambigüedad de receptor, lo que impedía compilar. Ahora referencia explícitamente el contenedor de MainActivity.

Repetir:

```powershell
./build.ps1
./.tools/gradle-8.11.1/bin/gradle.bat --gradle-user-home .tools/cache connectedDebugAndroidTest
```

El segundo comando requiere emulador o teléfono conectado con depuración habilitada y `JAVA_HOME`/`ANDROID_HOME` configurados. Reportes en `app/build/reports/tests/`, `app/build/reports/androidTests/connected/` y `app/build/reports/lint-results-debug.html`.

## Lo que aún depende del backend o del dispositivo físico

Las pruebas de HTTP/XML/JSON usan un transporte simulado para reproducir errores y renovación; no prueban JWT/Redis/PostgreSQL/MongoDB reales. Hay que acordar los contratos definitivos, ejecutar login/renovación/revocación contra los servicios e integrar el flujo de entrega con el web.

La captura de foto, el escaneo de un QR real y la precisión/actualización del GPS requieren ensayo en teléfono. No se consideran comprobadas esas capacidades por generar el APK o probar el arranque en emulador. La foto sigue siendo miniatura JPEG; no hay cola offline ni recuperación de borradores tras recrear la Activity.
