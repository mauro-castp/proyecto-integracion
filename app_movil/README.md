# Microhubs · Android (parte B)

Cliente Kotlin nativo, exclusivamente JSON. Integra auth (5101), usuarios (5102), entregas (5105), documentos (5107) y pedidos (5104). Incluye login, restauración segura, renovación ante 401, perfil, menú por rol, paginación de entregas, consulta de pedido, QR, foto de cámara, GPS y registro del resultado por PUT. Tokens reales cifrados AES-GCM mediante Android Keystore; no se guardan contraseñas ni sesiones demo y el backup está deshabilitado.

## Compilar y ejecutar

Requiere JDK 17 o 21, Android SDK 35, acceso a Google Maven/Maven Central y Gradle 8.11.1. Abre esta carpeta en Android Studio o ejecuta:

```powershell
./build.ps1
```

El script descarga Gradle y verifica su SHA-256 oficial; conserva herramientas/caché en `.tools/` ignorado por Git. Si tu JDK/SDK está en otro lugar, configura `JAVA_HOME` y `ANDROID_HOME`. El APK se genera en `app/build/outputs/apk/debug/app-debug.apk`; el script también ejecuta lint. La compilación ya se verificó y el APK está disponible en esa ruta. `build.ps1` ejecuta compilación, pruebas unitarias y lint. Ver los resultados y límites en [PRUEBAS_APPS.md](../app_escritorio/PRUEBAS_APPS.md).

## Demostración

1. Deja «Usar ejemplos locales» marcado; entra con correo válido y clave no vacía.
2. Consulta perfil y «Mis entregas». Selecciona pedido 101.
3. Concede permiso de cámara y vuelve a pulsar escanear. Escanea un QR cuyo contenido sea exactamente `101` (sin URL).
4. Captura foto. Concede ubicación precisa, activa GPS y vuelve a pulsar obtener GPS; espera señal.
5. Selecciona entregado/parcial/fallido. Para parcial/fallido se requieren observaciones. Registra y vuelve a consultar: cambia el estado en memoria.
6. Cierra sesión. Los ejemplos se reinician al reiniciar el proceso; no simulan bases de datos.

La foto actual es la miniatura JPEG devuelta por la aplicación de cámara, adecuada para ensayar, pendiente de captura a resolución completa para producción. GPS y cámara son reales incluso en modo local. La ubicación debe tener menos de dos minutos. La app muestra disponibilidad de red y errores; no implementa cola offline. No ingresar credenciales reales en modo demo.

## Contrato provisional: pendiente de parte A

Las estructuras de autenticación siguen la sección 3 del plan. Las siguientes rutas/payloads se proponen porque aún no existe `contratos/`; hay que acordarlas antes de integrar:

- POST `auth/login` `{correo,clave}` y POST `auth/renovar` `{token_renovacion}` devuelven sesión completa con usuario.
- POST `auth/salir` `{token_renovacion}` devuelve 204 o JSON.
- GET `usuarios/yo` devuelve usuario; GET `entregas?pagina=1&por_pagina=20` devuelve `ejemplos/entregas.json`. El servidor debe limitar las entregas al repartidor autenticado.
- GET `pedidos/{pedido_id}` devuelve pedido.
- POST `documentos` `{nombre,tipo,contenido_base64}` devuelve `{id}`. Evidencia JPEG en base64; no multipart.
- PUT `entregas/{id}` recibe `ejemplos/resultado.json` y devuelve la entrega actualizada.

`Accept` y `Content-Type`: `application/json`. Configura un host HTTPS sin puerto/ruta; se usan los puertos del plan. Android bloquea HTTP y requiere certificado confiable. En emulador, localhost es el propio emulador: usa el nombre/IP del servidor y un certificado válido para él. No se desactiva TLS.

El backend debe validar JWT, rol, pertenencia del pedido, transiciones de estado y revocación Redis, y persistir en PostgreSQL/MongoDB. Esos componentes están fuera de esta entrega cliente. Si falla el PUT tras subir la foto puede quedar un documento huérfano: falta acordar idempotencia y limpieza con A.

## Pruebas adicionales pendientes de dispositivo físico e integración

- Login real, renovación expirada y revocación; cierre con red caída debe borrar credenciales locales.
- Permisos denegados, GPS apagado, QR distinto al pedido, cancelación de cámara, ausencia de cámara.
- Resultado parcial sin observaciones bloqueado; evidencia y GPS obligatorios; consulta tras actualizar.
- Rotación/recreación: el formulario y evidencia se reinician; las credenciales reales pueden restaurarse. No se conservan borradores.
- Verificar rol repartidor/administrador y que otros perfiles no tengan el menú entregas.
- Confirmar servicios reales, persistencia e historial web antes de declarar completa la demostración integrada.
