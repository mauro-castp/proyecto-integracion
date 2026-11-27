# Instaladores de las apps

Los binarios **no van al repositorio** (es público): se generan en la PC con Windows, se comprueban y se publican como *Release* de GitHub
(o en ubiquitous). Aquí queda cómo se generan, dónde quedan y qué se anota.

**Con un solo comando** (desde la raíz del repositorio, en PowerShell): `.\entrega\instaladores.ps1` genera la APK y el ZIP, y anota commit,
tamaño y SHA-256 en `entrega/instaladores_generados.md` (texto, sí se sube) y en `app_escritorio/bin/notas_release.md` (para el Release).
Abajo está lo que hace, paso por paso.

## Android (APK)

```powershell
cd app_movil
.\build.ps1                                   # emulador: el host HTTP de depuración es 10.0.2.2
.\build.ps1 -DebugHttpHost 192.168.1.50       # teléfono físico en la misma red: la IP de la PC
```

`build.ps1` descarga Gradle 8.11.1 (con su SHA-256) en `app_movil/.tools/`, compila, corre las pruebas unitarias y lint.

- Sale en: `app_movil/app/build/outputs/apk/debug/app-debug.apk`
- Es la variante **debug**, la única que acepta HTTP hacia la PC (`BuildConfig.HTTP_HOST`). La variante release solo acepta HTTPS con un
  certificado válido: la nube ya tiene uno de Let's Encrypt y se usa el servidor `https://34-51-89-253.sslip.io/servicios`.
- No hay keystore de firma en el repositorio: la APK debug va firmada con la llave de depuración local de Android Studio. Si algún día se
  firma una release, la keystore y su clave se quedan fuera de Git.

## Escritorio (Windows x64, autónomo)

```powershell
cd app_escritorio
dotnet publish Microhubs.csproj -c Release -r win-x64 --self-contained true -o bin/Publicacion
Compress-Archive -Path bin/Publicacion/* -DestinationPath bin/Microhubs_Escritorio_win-x64.zip -Force
```

- Sale en: `app_escritorio/bin/Publicacion/` (incluye el runtime de .NET 8 y la carpeta `contratos/` con los XSD) y el zip en
  `app_escritorio/bin/` (dentro de `bin/` para que Git no lo vea).
- Se ejecuta con `Microhubs.exe`; hay que copiar la carpeta completa (los XSD se cargan al arrancar).
- `bin/` y `obj/` están en `app_escritorio/.gitignore`; el zip se sube al *Release*, no al repositorio.

## Comprobar antes de publicar

```powershell
Get-FileHash app_movil\app\build\outputs\apk\debug\app-debug.apk -Algorithm SHA256
Get-FileHash app_escritorio\bin\Microhubs_Escritorio_win-x64.zip -Algorithm SHA256
```

1. Instalar la APK en el emulador (`adb install -r app-debug.apk`), entrar con `repartidor1@codex.mx` y abrir «Mis entregas» y «Avisos».
2. Descomprimir el zip en otra carpeta, abrir `Microhubs.exe`, entrar como `planeador@codex.mx` y abrir *Reportes*.
3. Anotar en la tabla de abajo y en la descripción del *Release*.

## Publicar (GitHub Release)

Desde `main`, que ya tiene las apps unidas (PR #20 y #21). Que el commit anotado en `instaladores_generados.md` sea el de `main`
(o una rama sin cambios en `app_movil/` ni `app_escritorio/` respecto a `main`).

```powershell
gh release create v1.0-entrega-final app_movil\app\build\outputs\apk\debug\app-debug.apk app_escritorio\bin\Microhubs_Escritorio_win-x64.zip `
   --repo mauro-castp/proyecto-integracion --target main --title "Entrega final · apps" --notes-file app_escritorio\bin\notas_release.md
```

(o desde la página del repositorio: *Releases → Draft a new release*). En las notas: commit, fecha, SHA-256 de cada archivo, versión de Android
mínima (8.0, API 26), que la APK es debug y para qué host, y que el escritorio requiere Windows 10/11 x64.

| Archivo | Commit | Fecha | Tamaño | SHA-256 | Probado en |
|---|---|---|---|---|---|
| `app-debug.apk` |  |  |  |  |  |
| `Microhubs_Escritorio_win-x64.zip` |  |  |  |  |  |

**Estado:** Ruth comprobó en Windows que Android compila y el escritorio se publica; los instaladores para el Release se generan en la PC de
Mauro con `instaladores.ps1` y su registro queda en `instaladores_generados.md`.
