# Instaladores generados

Commit `43a45e1` (`main`, PR #23) · 27-nov-2026 · equipo VTMAU

| Archivo | Tamaño | SHA-256 |
|---|---|---|
| `app-debug.apk` | 3,581,313 bytes (3.4 MB) | `dbf7656e201cdc8b538c3723a8123f0db5af19f5d9106dea3e3231920f8ea851` |
| `Microhubs_Escritorio_win-x64.zip` | 70,148,342 bytes (66.9 MB) | `b62bbad0c5cb539ce9afd6150cdbf3887dd79ab11803a467182992a8f5a79ad5` |

Cómo se obtuvieron, en la PC de Mauro: la APK es la que generó `app_movil\build.ps1` después del arreglo del lector de QR (es la que pasó
`connectedDebugAndroidTest` 8/8); el ZIP comprime la carpeta `app_escritorio\bin\Publicacion` que dejó `dotnet publish -c Release -r win-x64
--self-contained` después de los arreglos de Comparar métodos (la que pasó 176/176 y se probó contra la nube). Se comprobó que el código de
`app_movil/` y `app_escritorio/` de esa PC es idéntico al de `main` en `43a45e1` (mismos árboles de Git) y que ningún archivo fuente es
posterior a los binarios.

Release de GitHub: `v1.0-entrega-final`, con `--target main`. Si se une el PR #24 (cliente en Android, escritorio para operadores), se
regeneran con `entrega\instaladores.ps1` y se publica otra versión.

Los binarios no van al repositorio: solo esta tabla.
