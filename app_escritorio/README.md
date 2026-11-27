# Microhubs · cliente de escritorio (parte B)

Aplicación C# / Windows Forms para **operador, planeador, administrador y auditor**. Habla **solo XML** (espacio de nombres
`urn:microhubs:v1`) con los microservicios del contrato v1: auth (5101), productos (5103), pedidos (5104), entregas (5105), planeación
(5106), zonas (5108), microhubs (5109), inventario (5111), cobertura (5116), capacidad (5117), rutas (5118), costos (5119), punto de
equilibrio (5120), simulación (5121), surtido (5122) y reportes (5123).

**Operación del microhub** (entrega final; `Modulos.cs` y `Operacion.cs`): *inventario* (existencias, alertas, movimientos, reservas,
registrar movimiento con un `operacion_uuid` nuevo cada vez, transferir), *preparación* (por preparar, pasar a preparación, marcar listo),
*despacho* (pedidos listos, repartidores, **asignar repartidor** y **manifiesto** de salida imprimible por repartidor) y *surtido* (ABC,
análisis, recomendaciones, restricciones). En capacidad: **cambiar personal** y **colas M/M/c**. El cambio de estado y la asignación usan
el contrato `operacion.xsd`; las colas, `colas.xsd`. Los botones que escriben se habilitan con los **permisos de la sesión** (p. ej.
`pedidos.cambiar_estado`, `entregas.asignar`); los que no los declaran siguen siendo de planeación y administración.

- Los **XSD oficiales** (carpeta `contratos/`, uno por servicio más `comun.xsd`) se cargan juntos: **toda petición se valida antes de
  enviarse y toda respuesta antes de usarse**. Se rechazan DTD y entidades externas, respuestas que no sean `application/xml`,
  raíces desconocidas y HTTP hacia hosts que no sean locales.
- Pantallas: acceso, catálogo (productos, zonas, microhubs), pedidos (filtros por estado y fechas, detalle, historial), candidatos
  (crear, editar con los 14 campos, simular con explicación, **decisión humana con motivo**), simulación libre, escenarios y
  resumen de simulaciones (agregación de MongoDB). Exporta a XML la última consulta.
- **Reportes** (ventana propia): catálogo, indicadores, cada reporte como tabla (con totales) o como datos de gráfica, bitácora de
  exportaciones y **descarga en CSV, Excel y PDF**. Solo se mandan los filtros que el reporte admite según el catálogo (periodo, zona,
  microhub). La descarga va por un método aparte (`Api.Download`) porque no es XML: revisa el tipo, la firma del archivo (`%PDF-`, ZIP
  del XLSX) y que el SHA-256 coincida con el encabezado `X-Reporte-SHA256`; los errores sí llegan en XML y se validan.
- **Análisis** (una ventana por módulo, definidas en `Modulos.cs`): *cobertura* (zonas, resumen, punto, candidatos, escenarios de
  radio, evaluar una ubicación), *rutas* (planes, proponer, abrir, confirmar, cancelar, comparar métodos), *costos* (conceptos,
  resumen, unitarios, rentabilidad, sensibilidad, alta de concepto), *capacidad* (microhubs, detalle, personal, cargas, simular),
  *punto de equilibrio* (por microhub, calcular, sensibilidad, escenarios, comparar) y *simulación* (ejecuciones, nueva, ver,
  repetir, cancelar, comparar); todas con sus supuestos. La colección principal de la respuesta va a la tabla de la izquierda y el
  resto (totales, decisión, supuestos usados) a la de la derecha. Los envíos parten del ejemplo oficial y se editan campo por campo
  (las listas de ids, separadas por coma; vacía = no se manda) y solo salen si validan contra el XSD.
- Permisos: `planeador` y `administrador` escriben; `auditor` solo consulta (el servidor responde 403 y la app muestra el motivo). En
  las ventanas de análisis los botones que escriben quedan deshabilitados para quien no es de planeación.
- Sesión: tokens solo en memoria; ante un 401 se renueva **una vez** (peticiones simultáneas comparten la renovación) y se repite;
  `Retry-After` de un 429 se respeta; salir revoca la sesión en el servidor y borra las credenciales aunque falle la red.

## Ejecutar

Requiere Windows y el **SDK de .NET 8** (el runtime no basta). Con el backend arriba
(`docker compose -f docker-compose.integrado.yml up --build -d`):

```powershell
cd app_escritorio
dotnet run
```

Host por omisión `http://localhost` (HTTP solo se permite hacia el equipo local; cualquier otro host exige HTTPS). Para la nube:
`https://34-51-89-253.sslip.io/servicios` (con ruta en la dirección se llama por nombre de servicio; sin ruta, a cada puerto). Cuentas de
demostración: `sistema_web/README.md` (planeador: `planeador@codex.mx`, auditor: `auditor@codex.mx`).
«Ejemplos oficiales» usa las respuestas de `contratos/ejemplos/` sin red (entra como planeador).

Publicación autónoma para Windows x64 (incluye el runtime; copiar **toda** la carpeta):

```powershell
dotnet publish Microhubs.csproj -c Release -r win-x64 --self-contained true -o bin/Publicacion
```

## Verificación

```powershell
dotnet build Microhubs.csproj
dotnet run --project pruebas/Microhubs.Pruebas.csproj          # sin red: 73 comprobaciones + 3 que abren las ventanas
python -m pip install lxml; python -m unittest discover -s pruebas -v    # 10 pruebas de los XSD con un validador independiente
$env:MICROHUBS_BACKEND='http://localhost'; $env:MICROHUBS_CLAVE='<clave de las cuentas de demostración>'
dotnet run --project pruebas/Microhubs.Pruebas.csproj          # +97 contra los servicios reales
$env:MICROHUBS_DESCARGAS='C:\temp\reportes'                    # opcional: guarda ahí el CSV, el Excel y el PDF descargados
```

Sin Windows (Linux o macOS con el SDK de .NET 8, sin paquetes de NuGet) corren las mismas pruebas salvo abrir las ventanas:
`dotnet run --project pruebas/multiplataforma/Microhubs.Pruebas.Multiplataforma.csproj` (73 sin red; con las mismas variables, 170).
Para «Rutas · proponer» hacen falta al menos dos pedidos listos en el microhub 1; si no los hay, esa parte se omite y lo dice.

Qué comprueba cada bloque:
1. **Contrato:** los 46 ejemplos XML oficiales validan; se rechazan sesión incompleta, otro espacio de nombres, accesibilidad fuera de
   1–10, motivo corto, correo sin formato, decisión inventada, DTD/entidades y raíces desconocidas.
2. **Protocolo (transporte simulado):** `Accept: application/xml`, puerto por servicio, token `Bearer`, 401 → renovación única (también
   con dos peticiones en paralelo), errores XML con campos y traza, 429 con `Retry-After`, HTTP solo local, JSON rechazado.
3. **Análisis y reportes (sin red):** cada acción de cada módulo tiene su ejemplo oficial con la raíz esperada, sus plantillas validan y
   su tabla se arma; editor de plantillas (listas y campos nulos); rutas por fila (número o UUID) y consultas editables sin rutas
   escondidas; tabla de reporte y de gráfica; filtros según el catálogo; descarga con transporte simulado (puerto, `Accept`, token,
   SHA-256 distinto, firma de PDF, tipo distinto, nombre con carpetas, error XML, 401 → renovación); puertos 5116 a 5123.
4. **Backend real:** inicio de sesión, catálogo, pedidos (detalle, historial, filtros), candidatos (crear, duplicado 409, editar,
   simular con los costos fijos del candidato, decisión con motivo, filtros), simulación libre, escenarios, resumen en MongoDB,
   permisos de auditor (403), renovación con token inválido y revocación al cerrar sesión. Además verifica que la tabla de cada
   pantalla se arma con las respuestas reales. Además, con los servicios de análisis: todas las consultas de las seis pantallas
   (XML válido y tabla), detalle de capacidad desde la fila, evaluar ubicación, simular capacidad, sensibilidad, dos escenarios de
   equilibrio guardados, abiertos y comparados, una simulación creada, terminada y repetida con la misma huella, rutas (comparar,
   proponer y guardar, abrir y cancelar), alta y baja de un concepto de costo, los 8 reportes con su gráfica, indicadores, las tres
   descargas con su SHA-256 y su registro en la bitácora, 404 y 400 en XML, y permisos del auditor (descarga sí; simulación, 403).

Resultados y límites en [PRUEBAS_APPS.md](PRUEBAS_APPS.md).

## Ensayo manual sugerido
0. *Reportes* → elegir «Pedidos por día», periodo del último mes → *Ver reporte*, *Gráfica* y *Descargar PDF* (abrirlo).
   *Simulación* → *Nueva simulación* → *Ejecuciones* → elegir la fila → *Ver ejecución*.
1. Entrar como planeador → *Candidatos* → *Crear candidato* (clave nueva) → *Editar* → *Simular selección* (decisión y explicación).
2. *Decidir* con un motivo de al menos 3 caracteres → la tabla refleja la decisión; *Guardar escenario* → *Escenarios* → *Detalle*.
3. *Resumen* (total de simulaciones y promedios por decisión).
4. Entrar como auditor: puede consultar y exportar, no crear (mensaje del servidor).
5. *Salir*: tabla y credenciales quedan vacías; el token anterior ya no funciona.
