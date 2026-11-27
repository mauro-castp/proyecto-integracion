# Manual de usuario · Plataforma de Microhubs

Codex Innovations · Equipo 04 · Entrega final

La plataforma surte pedidos de abarrotes desde cuatro microalmacenes de barrio («microhubs») del sector San Bernabé, en Monterrey.
Cada perfil ve solo lo que le corresponde. Se entra en **https://34-51-89-253.sslip.io** (en local: http://localhost:5000).

| Perfil | Qué hace | Dónde |
|---|---|---|
| Cliente | Compra y sigue sus pedidos | Portal web |
| Operador de microhub | Prepara pedidos, cuida el inventario, repone y despacha | Portal web |
| Repartidor | Entrega, toma evidencia y cierra | App Android |
| Planeador | Analiza viabilidad, planea rutas y reportes | Portal web y app de escritorio |
| Administrador | Usuarios, catálogos, aprobaciones, monitoreo | Portal web |
| Auditor | Consulta la bitácora y la trazabilidad, sin modificar nada | Portal web y app de escritorio |

**Inicio de sesión.** Correo y clave. Después de 5 intentos fallidos la cuenta se bloquea un rato (RN). Desde una misma conexión se
permiten hasta 30 inicios de sesión por minuto. La sesión dura 15 minutos y se renueva sola mientras se usa. «Salir» la cierra en
todos los servicios.

---

## Cliente

1. **Catálogo.** Busca productos por nombre o categoría. El precio es el de tu zona.
2. **Carrito.** El sistema avisa si no se alcanza el ticket mínimo de tu zona o si un producto no tiene existencia.
3. **Confirmar pedido.** El motor asigna el microhub más cercano que tenga todo y queda el folio `PED-AAAAMMDD-NNNNNN`.
4. **Mis pedidos.** Muestra el estado (asignado, en preparación, en ruta, entregado) y su historial. Al entregarse llega un aviso a la
   campana de **Notificaciones**.
5. **Cancelar.** Solo mientras el pedido no se prepara (RN21).

## Operador de microhub

- **Bandeja.** Pedidos de tu microhub: pasar a preparación y marcar «listo para despacho». No ves pedidos de otros microhubs (RN22).
- **Inventario.** Existencias, mínimos y movimientos: recepción, merma, ajuste y conteo.
- **Abastecimiento** (`/web/servicios/abastecimiento`). Es el proceso integral P2:
  1. Revisa las **alertas** (agotado o bajo mínimo) y las **necesidades**, con la mejor oferta de proveedor y el costo estimado.
  2. Marca los productos, ajusta las cantidades y pulsa **Crear solicitud de compra**. El planeador recibe un aviso.
  3. Cuando el administrador aprueba y emite la orden, la ves en «Órdenes de compra».
  4. Cuando llega la mercancía, adjunta la **remisión o factura** (PDF, JPG o PNG, hasta 5 MB) y pulsa **Recibir todo**. La existencia
     sube en inventario y el comprobante queda guardado en la nube. Para descargarlo, haz clic en su nombre: el enlace dura 5 minutos.
  5. Si inventario no respondía, la recepción queda pendiente. Repetir «Recibir» la aplica una sola vez.
- **Rutas** (`/web/servicios/rutas`). Abre el plan que propuso el planeador y pulsa **Confirmar y despachar a los repartidores**.
  Cada repartidor recibe «Nueva entrega asignada» y ve sus paradas en orden en la app.

## Repartidor (app Android)

1. **Acceso.** Servidor `https://34-51-89-253.sslip.io/servicios`, tu correo y tu clave.
2. **Mis entregas.** Las paradas del día en el orden de la ruta, con dirección, distancia y total a cobrar.
3. **Entrega.** Escanea el QR del pedido, toma la **foto de evidencia** y obtén el **GPS**. Elige el resultado:
   - **Entregado:** se cobra el total exacto (RN27).
   - **Parcial:** por cada línea, cuántas unidades regresan y por qué (RN28).
   - **Fallida:** se escribe la incidencia y no se cobra (RN29).
4. **Registrar resultado.** Reintentar no duplica el cierre. Si responde «otra operación ya cerró la entrega», avisa al operador.
5. **Sin conexión.** El botón cambia a **Guardar resultado (sin red)**: el cierre, la foto y el recorrido quedan en el teléfono y se
   envían solos al volver la red. En **Sin enviar** se ve cada operación (por enviar, reintentando, conflicto o rechazada) con su
   motivo, y está el botón **Enviar ahora**. Si hay un conflicto, gana lo que ya tiene el servidor.
6. **Avisos.** La bandeja muestra las asignaciones y demás avisos; tocar uno lo marca como leído y, si es de una entrega, la abre.
7. Al cerrar, el domicilio del cliente deja de mostrarse (RN26).

## Planeador

- **Planeación** (portal y app de escritorio):
  - candidatos a nuevo microhub y simulación de viabilidad;
  - punto de equilibrio paso a paso;
  - escenarios guardados y comparables;
  - simulación Monte Carlo (la respuesta llega en unos segundos, porque corre en segundo plano);
  - decisión humana, siempre con un motivo.
- **App de escritorio.** Además de candidatos y escenarios, tiene la ventana **Reportes** (indicadores, tabla, gráfica y descarga en
  CSV, Excel o PDF) y una ventana para cobertura, rutas, costos, capacidad, punto de equilibrio y simulación.
- **Rutas.** Con los pedidos listos del microhub, pulsa **Proponer plan**. Elige el método: el *automático* usa el recorrido exacto
  hasta 8 paradas. Revisa las rutas, los minutos (en rojo, las paradas que pasan de 30 min) y el costo. El operador o el administrador
  lo despachan.
- **Reportes en la nube** (`/web/servicios/reportes`):
  1. Elige el reporte y el periodo.
  2. Pulsa **Descargar y archivar** en CSV, Excel o PDF.
  3. El archivo queda guardado y aparece en «Exportaciones archivadas», desde donde se vuelve a bajar con un enlace temporal.

## Administrador

- **Usuarios, productos, categorías, zonas, microhubs y parámetros.** Cada cambio queda en la bitácora.
- **Abastecimiento.** Aprueba o rechaza solicitudes (con motivo) y **emite la orden de compra**. Si el proveedor tiene un pedido
  mínimo que no se alcanza, el sistema lo dice. Para concentrar las líneas en un solo proveedor, escribe su número.
- **Monitoreo** (`/web/servicios/monitoreo`). Muestra el estado de los 26 servicios: sano, degradado o caído. Para cada uno se ve la
  última verificación, los ms, los errores 5xx por hora, la disponibilidad de 24 h, el p95, las dependencias caídas y las alertas.
  «Verificar ahora» fuerza una ronda. «Reconocer» marca que ya viste una alerta; la alerta se cierra sola cuando el servicio vuelve.
- **Microservicios** (`/web/servicios`). Muestra la salud de cada servicio y una respuesta XML real.

## Auditor

- **Bitácora.** Quién hizo qué, cuándo y desde qué IP, con filtros por módulo, entidad, usuario, fechas y éxito. Incluye los
  inicios de sesión fallidos.
- **Trazabilidad de un pedido.** Une sus estados, la bitácora, los movimientos de inventario y los archivos, sin mostrar su contenido.
- El auditor no puede modificar nada. Si intenta guardar, el servicio responde «sin permiso».

## Mensajes frecuentes

| Mensaje | Qué significa | Qué hacer |
|---|---|---|
| «La sesión venció o fue cerrada» | Pasaron 15 min sin renovar, alguien cerró la sesión o se reinició Redis | Volver a entrar |
| «Máximo N solicitudes por minuto. Espera X segundos» | Límite de consumo | Esperar los segundos indicados |
| «El servicio X no responde. Intenta más tarde» | Una parte del sistema está caída; lo demás sigue | Reintentar; el administrador lo ve en Monitoreo |
| «No se pudo validar la sesión» | Redis no responde (por seguridad no se deja pasar a nadie) | Esperar; el administrador lo ve en Monitoreo |
| Cualquier error | Trae un código de traza | Dárselo al administrador: con él encuentra el error en los registros |
