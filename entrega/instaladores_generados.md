# Instaladores generados

> **Ya no vigentes:** estos archivos salieron de `acabf89`, antes de los arreglos del 27 de noviembre (Comparar métodos y lector de QR).
> Se regeneran con `entrega\instaladores.ps1` desde `main` cuando se una el PR de `mauro-pendientes`, y esta tabla se reemplaza.

Commit `acabf89` · 2026-11-27 01:28 · equipo VTMAU

| Archivo | Tamaño | SHA-256 |
|---|---|---|
| `app-debug.apk` | 1,391,916 bytes (1.3 MB) | `fb73aa09832dbd24f70d8209fbca6f8fcd8c253789f5f9981cba5e95f3607673` |
| `Microhubs_Escritorio_win-x64.zip` | 70,148,181 bytes (66.9 MB) | `bd5da801fd787e04fa8dd7016557b41362fdd0ab479492e7b590546a4095c5e8` |

- APK: variante debug (la única que acepta HTTP); host de depuración 10.0.2.2 (emulador); Android 8.0 o superior (API 26).
- Escritorio: Windows 10/11 x64, autónomo (.NET 8 incluido). Descomprimir completo y abrir `Microhubs.exe`.
- Comprobar en Windows: `Get-FileHash <archivo> -Algorithm SHA256`.
