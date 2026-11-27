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

- [ ] **Ensayo sin red en un teléfono real:** modo avión, cerrar una entrega, ver «Sin enviar», quitar el modo avión y comprobar que se envía sola.
- [ ] **Emulador:** `connectedDebugAndroidTest`.
- [ ] **Escritorio:** abrir a mano cada ventana nueva (reportes, cobertura, rutas, costos, capacidad, punto de equilibrio y simulación).
- [ ] **Apps contra la nube:** iniciar sesión desde el teléfono y desde la app de escritorio con el servidor
      `https://34-51-89-253.sslip.io/servicios` (la máquina encendida y la clave de la nube, que se pide por un canal privado).
- [ ] **Capturas** en `entrega/capturas/`: `movil_avisos`, `movil_sin_red_guardado`, `movil_sin_enviar`, `movil_sincronizado`, `movil_conflicto` (opcional),
      `escritorio_reportes`, `escritorio_pdf`, `escritorio_equilibrio`, `escritorio_simulacion`, `escritorio_rutas` (`.png`).
- [ ] **Instaladores** (`entrega/INSTALADORES.md`): APK y ZIP del escritorio, publicados como *Release* de GitHub o en ubiquitous. Nunca el keystore ni binarios en el repositorio.
- [ ] **Pruebas de usabilidad** con personas (`entrega/FORMATO_USABILIDAD.md`).
- [ ] **Video** (`docs/GUION_VIDEO_Y_PRESENTACION.md`, parte A, y `entrega/GUION_VIDEO.md`).

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
