# Verificación de las apps (segundo parcial) · 12 de octubre de 2026

Las apps se adaptaron al **contrato v1 definitivo** (rutas, campos, XSD oficiales) y se probaron contra los microservicios reales
(JWT, Redis, PostgreSQL, MongoDB) levantados con `docker-compose.integrado.yml`. Las herramientas locales (`.tools/`) están
ignoradas por Git.

## Escritorio (C# / Windows Forms · solo XML)
- **Compilación:** `dotnet build` sin errores ni advertencias; publicación autónoma Windows x64 generada (`bin/Publicacion/`, incluye
  el runtime y `contratos/`); la ventana arranca.
- **Pruebas C# (`pruebas/`):** 62 comprobaciones aprobadas: 33 sin red (46 ejemplos XML oficiales + rechazos; protocolo con
  transporte simulado: 401→renovación única, concurrencia, 429, errores XML, JSON y HTTP rechazados) y 29 contra el backend real
  (ver README).
- **Pruebas Python (`pruebas/test_contratos.py`, lxml):** 10 aprobadas con un validador independiente de los XSD.

## Android (Kotlin · solo JSON)
- **APK debug:** `app/build/outputs/apk/debug/app-debug.apk`. Lint: 0 errores y 14 advertencias (versiones de dependencias, recursos
  sin usar, icono, `ExifInterface`, `DataExtractionRules`, `ApplySharedPref`; `InsecureBaseConfiguration` es el HTTP permitido solo
  en debug). No se afirma que el análisis esté libre de advertencias.
- **Unitarias (JVM): 39 aprobadas** — protocolo (cabeceras, puertos, errores, renovación única y concurrente, 429, reglas de HTTP/HTTPS,
  JSON obligatorio), contrato (los 53 ejemplos oficiales, estructura de la sesión y de los errores, cuerpo de cierre idéntico en claves
  al ejemplo oficial) y entregas (reglas RN28/RN29 antes de enviar, orden documento → GPS → cierre, **reintento con el mismo UUID sin
  duplicar ni volver a subir la foto**, 200 duplicado = éxito, 422 conserva el UUID, 409 lo descarta, GPS en lotes de 500).
- **Contra el backend real (JVM): 2 aprobadas** — acceso, perfil, clave incorrecta, mis entregas, detalle, evidencia (Base64 → MongoDB),
  GPS, cierre «entregado», segundo cierre con otro UUID → 409, **reintento con el mismo UUID → 200 `duplicado`**, notificaciones
  (listar, contador, marcar leída) y cierre de sesión con revocación (el token anterior da 401).
- **Instrumentadas en emulador (Android 14, Medium_Phone): 7 aprobadas** — cifrado y restauración con Android Keystore, descarte de
  datos corruptos, persistencia del cierre pendiente (UUID + evidencia), redimensión de la foto a ≤ 1600 px y firma JPEG, arranque,
  recorrido de pantallas con ejemplos locales (acceso → entregas → entrega → validación de QR → notificaciones → salida) y recorrido
  de pantallas **contra el backend real vía 10.0.2.2** (acceso, perfil, entregas, notificaciones, salida).

## Hallazgo corregido durante la integración
- La regla `contratos/` de exclusión privada del repositorio también ignoraba `app_escritorio/contratos/` (los XSD que la app necesita
  en ejecución). Se acotó a la raíz del repositorio.

## Qué NO está comprobado
- **Cámara real, QR físico y precisión del GPS** en un teléfono: en emulador solo se probaron el recorrido de pantallas y el
  procesamiento de la imagen; no se tomó una foto con la cámara ni se escaneó un QR.
- El cierre de entrega **desde la pantalla** (con QR, foto y GPS) no se automatizó; el cierre completo se probó a nivel de cliente
  contra el backend real. Falta un ensayo manual en el teléfono antes de la demostración.
- Sin cola offline: sin red no se puede cerrar la entrega; al volver la red el reintento no duplica.
- Las pruebas instrumentadas pueden fallar si el emulador con GPU por software se cae (`DeadSystemException`); basta repetir.
- La app de escritorio solo se ejecutó en Windows 11.
