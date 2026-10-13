# Probar las apps (parte B) contra los microservicios

**Codex Innovations · Equipo 04 · Segundo Parcial**

Pasos para la demostración integrada: la app Android y la de escritorio contra los ocho servicios reales de `servicios/`.

## 1. Levantar el backend

Requiere Docker Desktop. Desde la raíz del repositorio:

```powershell
docker compose -f docker-compose.integrado.yml up --build -d
docker compose -f docker-compose.integrado.yml ps
```

Esperar a que los servicios aparezcan `healthy` y `migraciones` como `exited (0)`. Comprobar en el navegador:

- `http://localhost:5101/api/v1/salud` … `http://localhost:5108/api/v1/salud` → `"estado": "ok"`
- `http://localhost:5105/api/v1/docs` → Swagger del servicio de entregas (igual para los demás puertos)
- `http://localhost:5000` → portal web

Cuentas de demostración: `admin@codex.mx`, `planeador@codex.mx`, `auditor@codex.mx`, `operador.mh02@codex.mx`,
`repartidor1@codex.mx`. Clave de todas: `Codex#2026`.

## 2. Preparar entregas en ruta

El repartidor necesita paradas abiertas **del día**. Cada cierre las consume, así que se repite antes de cada ensayo:

```powershell
docker compose -f docker-compose.integrado.yml exec entregas python pruebas/preparar_entregas.py --cantidad 2
```

También se puede hacer desde el portal: el operador marca pedidos «listos para despacho» y los despacha en Planeación → Entregas.
En ambos casos el repartidor recibe el aviso «Nueva entrega asignada».

## 3. App de escritorio (XML)

```powershell
cd app_escritorio
dotnet run                                   # host http://localhost, entrar como planeador@codex.mx
$env:MICROHUBS_BACKEND='http://localhost'; $env:MICROHUBS_CLAVE='Codex#2026'
dotnet run --project pruebas/Microhubs.Pruebas.csproj      # 33 sin red + 29 contra los servicios
```

## 4. App Android (JSON)

Emulador: el servidor es `http://10.0.2.2` (ya viene en la pantalla de acceso en debug). Teléfono físico: compilar con la IP de
la PC (`./build.ps1 -DebugHttpHost 192.168.1.20`) y abrir los puertos 5101–5108 en el Firewall de Windows.

```powershell
cd app_movil
$env:MICROHUBS_BACKEND_HOST='127.0.0.1'; $env:MICROHUBS_CLAVE='Codex#2026'
./.tools/gradle-8.11.1/bin/gradle.bat --gradle-user-home .tools/cache testDebugUnitTest --tests "*BackendRealTest*"
./.tools/gradle-8.11.1/bin/gradle.bat --gradle-user-home .tools/cache connectedDebugAndroidTest "-Pandroid.testInstrumentationRunnerArguments.clave=Codex#2026"
```

`BackendRealTest` cierra las dos entregas preparadas en el paso 2: repetir ese paso antes de volver a correrlo.

## 5. Guion de la demostración integrada

1. **Escritorio** (planeador): candidatos → crear → simular → decidir con motivo → resumen de simulaciones (MongoDB).
2. **Portal web** (operador MH-02): despachar pedidos listos, o correr el paso 2.
3. **Android** (repartidor): aviso de entrega → Mis entregas → QR → foto → GPS → registrar resultado.
4. **Portal web** (cliente del pedido): aviso de pedido entregado; (operador) el pedido aparece cerrado con su historial.
5. **Escritorio**: Pedidos → filtro `entregado` → detalle e historial del mismo folio, en XML validado con XSD.
6. **Swagger** (`http://localhost:5105/api/v1/docs`): el contrato de `POST /entregas/{id}/resultado` que usó la app.

## Problemas comunes

| Síntoma | Causa y solución |
|---|---|
| Android: «Usa HTTPS o el host HTTP habilitado…» | El host no coincide con el de la compilación debug: usar `http://10.0.2.2` o recompilar con `-DebugHttpHost`. |
| Android: «No hay entregas en ruta» | Repetir el paso 2 (las entregas son del turno de hoy). |
| 423 «Cuenta bloqueada» | Cinco claves incorrectas seguidas: esperar 15 minutos o `docker compose … exec redis redis-cli DEL auth:bloqueo:<correo>`. |
| 429 | Más de 240 solicitudes por minuto desde la misma IP; la app respeta `Retry-After`. |
| `salud` en `degradado` | Alguna base no responde: `docker compose -f docker-compose.integrado.yml logs mongo postgres redis`. |
