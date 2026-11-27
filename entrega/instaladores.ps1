# Genera los dos instaladores y anota su tamaño y SHA-256. No publica nada y no deja binarios en carpetas que Git suba.
#
#   .\entrega\instaladores.ps1                         APK para el emulador (HTTP a 10.0.2.2) y ZIP del escritorio
#   .\entrega\instaladores.ps1 -DebugHttpHost 192.168.1.50   APK para un teléfono en la misma red que la PC
#
# Deja:
#   app_movil\app\build\outputs\apk\debug\app-debug.apk         (ignorado por Git: **/build/)
#   app_escritorio\bin\Microhubs_Escritorio_win-x64.zip          (ignorado por Git: bin/)
#   app_escritorio\bin\notas_release.md                          notas para el Release, con los SHA-256
#   entrega\instaladores_generados.md                            el mismo registro, para subirlo al repositorio (solo texto)
param([string]$DebugHttpHost = '')
$ErrorActionPreference = 'Stop'
$raiz = Split-Path -Parent $PSScriptRoot
Set-Location $raiz

# 1. APK (compila, corre las pruebas unitarias y lint)
$argsApk = @(); if ($DebugHttpHost) { $argsApk = @('-DebugHttpHost', $DebugHttpHost) }
& (Join-Path $raiz 'app_movil\build.ps1') @argsApk
if ($LASTEXITCODE -ne 0) { throw "build.ps1 terminó con código $LASTEXITCODE" }
$apk = Join-Path $raiz 'app_movil\app\build\outputs\apk\debug\app-debug.apk'
if (-not (Test-Path -LiteralPath $apk)) { throw "No se encontró la APK en $apk" }

# 2. Escritorio autónomo para Windows x64 y su ZIP
$escritorio = Join-Path $raiz 'app_escritorio'
$publicacion = Join-Path $escritorio 'bin\Publicacion'
if (Test-Path -LiteralPath $publicacion) { Remove-Item -LiteralPath $publicacion -Recurse -Force }
dotnet publish (Join-Path $escritorio 'Microhubs.csproj') -c Release -r win-x64 --self-contained true -o $publicacion
if ($LASTEXITCODE -ne 0) { throw "dotnet publish terminó con código $LASTEXITCODE" }
if (-not (Test-Path -LiteralPath (Join-Path $publicacion 'contratos'))) { throw 'La publicación no trae la carpeta contratos (los XSD)' }
$zip = Join-Path $escritorio 'bin\Microhubs_Escritorio_win-x64.zip'
Compress-Archive -Path (Join-Path $publicacion '*') -DestinationPath $zip -Force

# 3. Registro: commit, tamaño y SHA-256
$commit = (git rev-parse --short HEAD).Trim()
$sucio = (git status --porcelain -- app_movil app_escritorio) -ne $null
$fecha = Get-Date -Format 'yyyy-MM-dd HH:mm'
$hostApk = if ($DebugHttpHost) { $DebugHttpHost } else { '10.0.2.2 (emulador)' }
$filas = foreach ($f in @($apk, $zip)) {
    $i = Get-Item -LiteralPath $f
    $sha = (Get-FileHash -LiteralPath $f -Algorithm SHA256).Hash.ToLowerInvariant()
    '| `{0}` | {1:N0} bytes ({2:N1} MB) | `{3}` |' -f $i.Name, $i.Length, ($i.Length / 1MB), $sha
}
$texto = @"
# Instaladores generados

Commit ``$commit``$(if ($sucio) { ' **con cambios sin commit en las apps**' }) · $fecha · equipo $env:COMPUTERNAME

| Archivo | Tamaño | SHA-256 |
|---|---|---|
$($filas -join "`n")

- APK: variante debug (la única que acepta HTTP); host de depuración $hostApk; Android 8.0 o superior (API 26).
- Escritorio: Windows 10/11 x64, autónomo (.NET 8 incluido). Descomprimir completo y abrir ``Microhubs.exe``.
- Comprobar en Windows: ``Get-FileHash <archivo> -Algorithm SHA256``.
"@
$texto | Set-Content -LiteralPath (Join-Path $escritorio 'bin\notas_release.md') -Encoding utf8
$texto | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'instaladores_generados.md') -Encoding utf8
Write-Host $texto
if ($sucio) { Write-Warning 'Hay cambios sin commit en app_movil o app_escritorio: el instalador no corresponde exactamente al commit anotado.' }
