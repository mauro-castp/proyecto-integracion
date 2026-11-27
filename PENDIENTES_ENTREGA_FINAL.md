# Pendientes de la entrega final

Estado al 27 de noviembre de 2026. Aquí queda **solo lo que necesita a una persona**: un teléfono, grabar, probar con usuarios, aceptar términos o entregar.

> **La entrega es individual** (quien no entrega por su cuenta tiene cero) y hay tres preguntas individuales sobre **todo** el proyecto. El reparto sirve
> para avanzar el trabajo común; cada integrante entrega lo suyo, escribe su propia reflexión y estudia las dos partes.

## Lo que ya está listo (no rehacer)

| Tema | Dónde está |
|---|---|
| 26 microservicios, altas y cambios, pedidos, entregas y despacho de rutas por API | `servicios/README.md`, `servicios/INVENTARIO_ENDPOINTS.md` |
| Despliegue en GCP, bucket, URL firmadas, HTTPS con certificado de Let's Encrypt (vence el 25-02-2027) y registros | `deploy/gcp/LEEME.md`, `evidencias/nube/LEEME.md` |
| Panel de monitoreo con historial por servicio y pantallas web de los procesos | portal, `/web/servicios/monitoreo` |
| Procesos de principio a fin (por API y por el portal web) | `evidencias/nube/flujos/`, `evidencias/nube/procesos/` |
| Datos de alto volumen, Locust, fallos y seguridad | `evidencias/nube/` (local: `evidencias/volumen/`, `evidencias/carga/`) |
| Algoritmos documentados con tiempos medidos | `docs/ALGORITMOS.md`, `entrega/ALGORITMO_RUTAS.md` |
| App Android: avisos y cierre sin red; compila, genera la APK y pasa sus pruebas contra los servicios | `app_movil/`, `entrega/PRUEBAS_APPS_ENTREGA_FINAL.md` |
| App de escritorio: reportes y pantallas de análisis; compila, se publica y pasa sus pruebas contra los servicios | `app_escritorio/` |
| Expediente técnico (también en Word), manuales, plan de pruebas, registro de incidencias, runbook de fallos, guía de estudio y guion | `docs/`, `reporte_tecnico/`, `bloque_d/` |

Para levantar todo en local:

```bash
docker compose -f docker-compose.integrado.yml up -d --build        # si el puerto 5000 está ocupado: WEB_PORT=5050
```

Con una base de MongoDB creada antes de la entrega final, una sola vez:

```bash
docker compose -f docker-compose.integrado.yml exec -T mongo mongosh --quiet < bloque_c/mongo/03_documentos_nube.js
```

## Parte de Mauro · aplicaciones, pruebas con personas y video

Trabaja en una rama propia a partir de `main` y toca solo `app_movil/`, `app_escritorio/` y `entrega/`.

Estado al 27 de noviembre (detalle y resultados en `entrega/PRUEBAS_APPS_ENTREGA_FINAL.md`, sección 7):

- [ ] ~~**Ensayo sin red en un teléfono real**~~ **No se hará:** el equipo no tiene un Android físico. Queda documentado como no probado.
- [x] **Emulador:** `connectedDebugAndroidTest` 7/7 en un emulador API 36 contra los servicios locales.
- [x] **Escritorio:** las 7 ventanas abiertas a mano; pruebas 176/176 contra los servicios locales. Se arreglaron 2 errores (Comparar métodos).
- [x] **Apps contra la nube:** el teléfono (en el emulador) inició sesión, vio entregas, tomó foto y GPS; el lector de QR cerraba la app y se
      arregló. El escritorio, ver la sección 7.2.
- [x] **Capturas:** las de escritorio y `movil_avisos`. Faltan las cuatro del ensayo sin red (no hay teléfono).
- [x] **Instaladores:** publicados desde `main` en el *Release* `v1.0-entrega-final`.
- [x] **Pruebas de usabilidad:** 3 personas, una tarea cada una (27-nov); resultados al final de `entrega/FORMATO_USABILIDAD.md`. Hallazgo: en el escritorio cuesta llegar al PDF del reporte.
- [x] **Video:** <https://youtu.be/Q1Rm-Kr09Vw> (guion en `docs/GUION_VIDEO_Y_PRESENTACION.md`, parte A, y `entrega/GUION_VIDEO.md`).

**Revisión contra el enunciado del Proyecto 11 (27-nov, rama `mauro-faltantes`).** Faltaban funciones que pide el enunciado; se agregaron:

- [x] **Android, perfil cliente:** catálogo (y catálogo ligero sin red), pedido (también sin red), estatus y confirmar recepción.
- [x] **Android, repartidor:** «Navegar al domicilio».
- [x] **Escritorio para operadores:** inventario, preparar pedidos, asignar repartidores, manifiestos, revisar surtido y configurar capacidad.
- [x] **Algoritmos M/M/1 y M/M/c** (servicio de capacidad, documentados en `docs/ALGORITMOS.md` §3).
- [x] **Perfil proveedor con cuenta:** portal web `/proveedor` (órdenes y oferta), rol y permiso en `17_perfil_proveedor.sql`.
- [x] **Recuperación de contraseña** en el portal (`/recuperar`), enlace de un solo uso de 30 minutos.
- [x] **Servicios independientes del portal**, **monitor** con tiempo promedio y último error, prueba de **token vencido** y
      Locust sobre los 26 servicios.
- [x] **Probado en la PC de Mauro:** Docker con `16_apps_cliente.sql`, Android 8/8 en el emulador, escritorio 218/218 y prueba a mano.
- [x] **Después de unir:** nube desplegada de nuevo, instaladores publicados desde `main` y Word del expediente regenerado.

## Parte de Ruth · entrega

- [ ] **Presentación** con las 16 partes (`docs/GUION_VIDEO_Y_PRESENTACION.md`, parte B).
- [ ] **Ubiquitous:** subir con Cyberduck la carpeta web (presentación, enlaces, documentos y capturas) y poner el enlace en el README.
- [ ] **Bitácora de participación** (`docs/BITACORA_PARTICIPACION.md`): la llena el equipo a partir de `git log`.

## Cada integrante, por su cuenta

- [ ] Su entrega individual.
- [ ] Reflexión individual con sus palabras (`docs/REFLEXION_INDIVIDUAL_PLANTILLA.md`).
- [ ] Estudiar todo el proyecto: `docs/GUIA_ESTUDIO_PREGUNTAS.md` y `docs/RUNBOOK_FALLOS.md`.

## Opcionales que suman

- Plazo total por petición o cortacircuitos en `comun/clientes.py` (incidencia I-20).
- Más procesos (`-w 4`) en la VM para pedidos, productos y auth, que son los primeros en hacer fila según Locust.
