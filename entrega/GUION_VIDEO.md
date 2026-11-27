# Guion del video de la entrega final

**Duración objetivo:** 9 a 10 minutos. **Formato:** grabación de pantalla con voz; cada bloque lo puede narrar una persona distinta.
**Antes de grabar:** plataforma arriba en local (`docker compose -f docker-compose.integrado.yml up -d`), `servicios/pruebas/preparar_entregas.py
--cantidad 3`, la app Android en el emulador apuntando a `10.0.2.2`, la app de escritorio publicada y la VM de Google Cloud encendida solo
durante el bloque de nube (después se apaga: cuesta por hora). Ninguna clave se dice ni se muestra en pantalla: se escribe con la cámara fuera
del campo o con el campo de clave ya lleno.

Los números que se citan salen de los documentos del repositorio; si al grabar se vuelve a correr algo y cambia, se dice el número nuevo.

| # | Bloque | Tiempo | Qué se ve en pantalla | Qué se dice (idea, no texto para leer) |
|---|---|---|---|---|
| 1 | **Problema** | 0:00–0:45 | Mapa o diapositiva de las cuatro colonias de San Bernabé (`presentacion/`) | Tiendas de barrio y vecinos que piden abarrotes; la red de microhubs surte rápido y cerca. Qué decide el sistema: dónde abrir, cuánto cuesta, si conviene, cómo repartir. |
| 2 | **Arquitectura** | 0:45–1:45 | Diagrama de contenedores y de despliegue (`bloque_d/`) | Portal web (Flask), 26 microservicios con una responsabilidad cada uno (puertos 5101–5126), PostgreSQL, MongoDB y Redis; dos apps: Android solo JSON y escritorio solo XML validado contra XSD. JWT con renovación. |
| 3 | **Sistema web** | 1:45–2:45 | `http://localhost:5000`: sitio público → entrar → hacer un pedido → panel de planeación | El pedido entra al motor de asignación y queda en un microhub; el operador lo prepara y lo deja listo. |
| 4 | **App móvil** | 2:45–4:00 | Emulador: entrar → «Avisos» (la entrega asignada) → «Mis entregas» → abrir → QR, foto, GPS → registrar. Luego **modo avión**: registrar otra → «Sin enviar» → quitar el modo avión → la operación se envía sola | Solo JSON. Cierre idempotente: el mismo identificador nunca se aplica dos veces. Sin red el cierre, la foto y el recorrido se guardan; al volver la red primero sube la foto y luego manda el lote a sincronización. Si el servidor ya tenía otro cierre, gana el servidor y la app lo muestra. |
| 5 | **App de escritorio** | 4:00–5:15 | Entrar como planeador → *Reportes* → «Pedidos por día» → *Ver reporte* → *Descargar PDF* (abrirlo) → *Punto de equilibrio* → *Calcular* → *Simulación* → *Nueva simulación* → *Ver ejecución* | Solo XML; toda petición y respuesta se valida con el XSD antes de usarse. La descarga del reporte verifica el SHA-256 que manda el servicio. El auditor puede consultar y descargar, no escribir. |
| 6 | **Microservicios** | 5:15–6:00 | `servicios/README.md` (tabla de servicios) y una terminal con `docker compose ps` | Cada servicio con su base de datos, su contrato y sus pruebas; se llaman entre sí con el JWT de quien pidió (p. ej. reportes arma sus tablas con pedidos, inventario y equilibrio). |
| 7 | **Swagger** | 6:00–6:30 | `http://localhost:5107/api/v1/docs` (documentos) y probar un `GET` con el token | Cada servicio publica su contrato con ejemplos JSON y XML. |
| 8 | **Monitoreo** | 6:30–7:10 | Portal → `/web/servicios/monitoreo`; detener un servicio (`docker compose stop rutas`), ver cómo aparece caído y su historial; volver a encenderlo | Salud de los 26 servicios, PostgreSQL, Redis, MongoDB y el bucket; alertas e historial de disponibilidad. |
| 9 | **Nube** | 7:10–8:00 | Consola de Google Cloud: VM `microhubs-vm`, IP fija, bucket privado; el portal por HTTPS en `34-51-89-253.sslip.io`; un documento subido y su URL firmada | Despliegue en GCP (`deploy/gcp/LEEME.md`): Nginx, bucket privado sin acceso público y URL firmadas, registros en Cloud Logging. Mencionar el costo (~0.13 USD/h) y que se apaga. La nube tiene certificado de Let's Encrypt y las apps se conectan a `https://34-51-89-253.sslip.io/servicios`: en los bloques 4 y 5 se muestran contra la nube solo si la prueba con sesión real salió bien; si no, contra la PC. |
| 10 | **Algoritmo** | 8:00–8:45 | `entrega/ALGORITMO_RUTAS.md`, tabla de la sección 10; en escritorio *Rutas* → *Comparar métodos* | Asignar pedidos a repartidores y ordenar paradas es ruteo de vehículos (NP-difícil). Exacto hasta 8 paradas; con más, vecino más cercano mejorado con 2-opt: con 9 paradas tarda 1.29 ms contra 3,913 ms del exacto, a 0.2 % del óptimo; con 50 paradas ahorra 78 % de distancia contra el orden de llegada. |
| 11 | **Pruebas de carga** | 8:45–9:20 | `evidencias/nube/carga/informe_carga.md` y su gráfica (`carga.html`) | Locust en la VM e2-standard-4: 10,412 peticiones, 0.14 % de errores; máximo 51.2 peticiones/s con 200 usuarios, donde se satura (p95 4.5 s). Los puntos más lentos: indicadores y comparación de microhubs en reportes. |
| 12 | **Pruebas de integración** | 9:20–10:00 | `evidencias/nube/ola4/pruebas.md` (436 de 436 casos en la nube, 26 de noviembre de 2026) y la salida de las pruebas de las apps contra los servicios (`entrega/salidas_pruebas/`) | Casos de petición y respuesta con lo que quedó en cada base; las apps se probaron contra los servicios reales. Cierre: qué falta y qué sigue. |

## Lista de verificación al grabar

- [ ] Ningún token, clave, llave o correo personal visible (los correos `@codex.mx` son de demostración y sí pueden verse).
- [ ] En el bloque 4 se ve el cambio de «Sin conexión» a «En línea» en la barra y la desaparición de «Sin enviar».
- [ ] En el bloque 5 el PDF descargado se abre.
- [ ] En el bloque 8 el servicio detenido se vuelve a encender antes de seguir.
- [ ] La VM se apaga al terminar el bloque 9 (`gcloud compute instances stop microhubs-vm --zone northamerica-south1-c`).
- [ ] Duración final y enlace del video anotados en el `README.md` (lo actualiza quien lleva los documentos).
