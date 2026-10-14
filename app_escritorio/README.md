# Microhubs · cliente de escritorio (parte B)

Aplicación C# / Windows Forms para **planeador, administrador y auditor**. Habla **solo XML** (espacio de nombres
`urn:microhubs:v1`) con los microservicios del contrato v1: auth (5101), productos (5103), pedidos (5104), planeación (5106), zonas (5108) y microhubs (5109).

- Los **XSD oficiales** (carpeta `contratos/`, uno por servicio más `comun.xsd`) se cargan juntos: **toda petición se valida antes de
  enviarse y toda respuesta antes de usarse**. Se rechazan DTD y entidades externas, respuestas que no sean `application/xml`,
  raíces desconocidas y HTTP hacia hosts que no sean locales.
- Pantallas: acceso, catálogo (productos, zonas, microhubs), pedidos (filtros por estado y fechas, detalle, historial), candidatos
  (crear, editar con los 14 campos, simular con explicación, **decisión humana con motivo**), simulación libre, escenarios y
  resumen de simulaciones (agregación de MongoDB). Exporta a XML la última consulta.
- Permisos: `planeador` y `administrador` escriben; `auditor` solo consulta (el servidor responde 403 y la app muestra el motivo).
- Sesión: tokens solo en memoria; ante un 401 se renueva **una vez** (peticiones simultáneas comparten la renovación) y se repite;
  `Retry-After` de un 429 se respeta; salir revoca la sesión en el servidor y borra las credenciales aunque falle la red.

## Ejecutar

Requiere Windows y el **SDK de .NET 8** (el runtime no basta). Con el backend arriba
(`docker compose -f docker-compose.integrado.yml up --build -d`):

```powershell
cd app_escritorio
dotnet run
```

Host por omisión `http://localhost` (HTTP solo se permite hacia el equipo local; cualquier otro host exige HTTPS). Cuentas de
demostración: `sistema_web/README.md` (planeador: `planeador@codex.mx`, auditor: `auditor@codex.mx`).
«Ejemplos oficiales» usa las respuestas de `contratos/ejemplos/` sin red (entra como planeador).

Publicación autónoma para Windows x64 (incluye el runtime; copiar **toda** la carpeta):

```powershell
dotnet publish Microhubs.csproj -c Release -r win-x64 --self-contained true -o bin/Publicacion
```

## Verificación

```powershell
dotnet build Microhubs.csproj
dotnet run --project pruebas/Microhubs.Pruebas.csproj          # 35 comprobaciones sin red
python -m pip install lxml; python -m unittest discover -s pruebas -v    # 10 pruebas de los XSD con un validador independiente
$env:MICROHUBS_BACKEND='http://localhost'; $env:MICROHUBS_CLAVE='<clave de las cuentas de demostración>'
dotnet run --project pruebas/Microhubs.Pruebas.csproj          # +29 contra los servicios reales (64 en total)
```

Qué comprueba cada bloque:
1. **Contrato:** los 46 ejemplos XML oficiales validan; se rechazan sesión incompleta, otro espacio de nombres, accesibilidad fuera de
   1–10, motivo corto, correo sin formato, decisión inventada, DTD/entidades y raíces desconocidas.
2. **Protocolo (transporte simulado):** `Accept: application/xml`, puerto por servicio, token `Bearer`, 401 → renovación única (también
   con dos peticiones en paralelo), errores XML con campos y traza, 429 con `Retry-After`, HTTP solo local, JSON rechazado.
3. **Backend real:** inicio de sesión, catálogo, pedidos (detalle, historial, filtros), candidatos (crear, duplicado 409, editar,
   simular con los costos fijos del candidato, decisión con motivo, filtros), simulación libre, escenarios, resumen en MongoDB,
   permisos de auditor (403), renovación con token inválido y revocación al cerrar sesión. Además verifica que la tabla de cada
   pantalla se arma con las respuestas reales.

Resultados y límites en [PRUEBAS_APPS.md](PRUEBAS_APPS.md).

## Ensayo manual sugerido
1. Entrar como planeador → *Candidatos* → *Crear candidato* (clave nueva) → *Editar* → *Simular selección* (decisión y explicación).
2. *Decidir* con un motivo de al menos 3 caracteres → la tabla refleja la decisión; *Guardar escenario* → *Escenarios* → *Detalle*.
3. *Resumen* (total de simulaciones y promedios por decisión).
4. Entrar como auditor: puede consultar y exportar, no crear (mensaje del servidor).
5. *Salir*: tabla y credenciales quedan vacías; el token anterior ya no funciona.
