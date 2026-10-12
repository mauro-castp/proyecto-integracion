$ErrorActionPreference = 'Stop'
$javaPath = 'C:\Program Files\Eclipse Adoptium\jdk-21.0.9.10-hotspot'
if (-not $env:JAVA_HOME -and (Test-Path -LiteralPath $javaPath)) { $env:JAVA_HOME = $javaPath }
if (-not $env:ANDROID_HOME) { $env:ANDROID_HOME = Join-Path $env:LOCALAPPDATA 'Android\Sdk' }
$toolsPath = Join-Path $PSScriptRoot '.tools'
$gradlePath = Join-Path $toolsPath 'gradle-8.11.1\bin\gradle.bat'
if (-not (Test-Path -LiteralPath $gradlePath)) {
    New-Item -ItemType Directory -Force -Path $toolsPath | Out-Null
    $archive = Join-Path $toolsPath 'gradle.zip'
    Invoke-WebRequest 'https://services.gradle.org/distributions/gradle-8.11.1-bin.zip' -OutFile $archive
    $expected = (Invoke-RestMethod 'https://services.gradle.org/distributions/gradle-8.11.1-bin.zip.sha256').Trim()
    if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expected) { throw 'Checksum Gradle incorrecto' }
    Expand-Archive -LiteralPath $archive -DestinationPath $toolsPath -Force
}
& $gradlePath --project-dir $PSScriptRoot --gradle-user-home (Join-Path $toolsPath 'cache') assembleDebug lintDebug
exit $LASTEXITCODE
