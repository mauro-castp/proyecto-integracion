# Pendientes de la entrega final · dividido en dos partes

Estado al 26 de noviembre de 2026. Rama de trabajo: **`ruth-entrega-final`**.

> **La entrega es individual** (quien no entrega por su cuenta tiene cero) y hay tres preguntas individuales sobre **todo** el proyecto. Este reparto
> es para avanzar el trabajo común; cada integrante entrega lo suyo, escribe su propia reflexión y estudia las dos partes.

## Lo que ya está listo (no rehacer)

| Tema | Dónde está |
|---|---|
| 26 microservicios, altas y cambios, pedidos y entregas por API | `servicios/README.md`, `servicios/INVENTARIO_ENDPOINTS.md` |
| Despliegue en GCP, bucket, URL firmadas, HTTPS autofirmado, registros | `deploy/gcp/LEEME.md`, `evidencias/nube/LEEME.md` |
| Panel de monitoreo con historial por servicio | portal, `/web/servicios/monitoreo` |
| Tres procesos de principio a fin (40 pasos) | `evidencias/nube/flujos/` |
| Datos de alto volumen, Locust y análisis | `evidencias/nube/volumen/`, `evidencias/nube/carga/` |
| Fallos (32/32) y seguridad (23/23) en la nube | `evidencias/nube/fallos.md`, `evidencias/nube/seguridad.md` |
| Algoritmo documentado con tiempos medidos | `entrega/ALGORITMO_RUTAS.md` |
| Capturas del panel, historial, microservicios y Swagger | `entrega/capturas/` |
| App de escritorio: compila, se publica y pasa 64 de 64 contra los servicios locales | `app_escritorio/` |
| App Android: compila y pasan sus pruebas (las 3 contra el servidor real se omitieron) | `app_movil/` |

Para levantar todo en local:

```bash
docker compose -f docker-compose.integrado.yml up -d --build        # si el puerto 5000 está ocupado: WEB_PORT=5050
```

Documentación de cada ruta: `http://localhost:PUERTO/api/v1/docs`.

---

## Parte 1 — Aplicaciones, instaladores y demostración (Mauro)

Tocar solo `app_movil/`, `app_escritorio/` y `entrega/` para no chocar con la parte 2.

- [ ] **Android: trabajo sin conexión.** Guardar el cierre de entrega y el GPS sin red y mandarlos con `POST /api/v1/sincronizacion/lotes` (5125) al reconectar;
      mostrar pendientes y conflictos. Pantalla de avisos (5124).
- [ ] **Escritorio: reportes** (5123) con descarga CSV, Excel y PDF, y pantallas de cobertura, rutas, costos, capacidad, punto de equilibrio y simulación.
- [ ] **Instaladores.** APK: `app_movil/build.ps1`. Escritorio: `dotnet publish Microhubs.csproj -c Release -r win-x64 --self-contained true -o bin/Publicacion`
      y comprimir la carpeta. Los binarios no van al repositorio: súbelos como *Release* de GitHub o a ubiquitous.
- [ ] **Ejecución real con evidencia** (lo pidió el profesor): Android con `BackendRealTest` contra Docker y capturas en emulador o teléfono; escritorio con
      `MICROHUBS_BACKEND=http://localhost` y `MICROHUBS_CLAVE`, y capturas.
- [ ] **Pruebas de usabilidad:** 3 personas, 5 tareas (entrar, ver entregas, cerrar una, consultar un reporte, ver el monitoreo); anotar tiempo, errores y mejoras.
- [ ] **Video** breve donde se vea: problema, arquitectura, sistema web, app móvil, app de escritorio, microservicios, Swagger, monitoreo, nube, algoritmo,
      pruebas de carga e integración.

## Parte 2 — Documentos y entrega (Ruth)

- [ ] **Expediente técnico** (32 puntos): portada, resumen ejecutivo, problema, objetivos, alcance, usuarios, requerimientos, reglas de negocio, arquitectura,
      diagramas, modelo relacional, MongoDB, Redis, buckets, microservicios, contratos JSON, contratos XML, Swagger, seguridad, algoritmos, infraestructura GCP,
      contenedores, monitoreo, plan de pruebas, resultados de Locust, resultados de rendimiento, manual de instalación, manual técnico, manual de usuario,
      limitaciones, trabajo futuro y conclusiones. Fuentes: `bloque_a/` a `bloque_d/`, los README, `deploy/gcp/LEEME.md` y `evidencias/nube/`.
      Falta actualizar los diagramas de `bloque_d/`, que muestran la versión de 10 servicios.
- [ ] **Presentación:** problema, usuarios, solución, arquitectura, demostración web, móvil y escritorio, microservicios, seguridad, datos, algoritmo,
      infraestructura, monitoreo, pruebas, resultados y conclusiones.
- [ ] **Bitácora de participación** (sale del historial de Git) y **registro de incidencias** (base abajo).
- [ ] **Ubiquitous:** carpeta web con la presentación del proyecto, enlaces, documentos y capturas; subirla con Cyberduck.
- [ ] **Ensayo de tolerancia a fallos** para la presentación (detener un servicio, revocar un token, apagar Redis, respuesta inválida, archivo inexistente,
      sobrecarga, intento sin permisos, explicar un error en los logs): `rendimiento/fallos_y_seguridad.py`.
- [ ] Opcional: HTTPS con certificado reconocido (Let's Encrypt) y caché de reportes (el cuello de botella medido).
- [ ] Pull request de `ruth-entrega-final` hacia `main`.

## Cada integrante, por su cuenta

- [ ] Su entrega individual.
- [ ] Reflexión individual, con sus palabras.
- [ ] Repasar todo el proyecto para las tres preguntas.

---

## Base para el registro de incidencias (problemas reales ya resueltos, salvo el último)

| Incidencia | Causa | Solución |
|---|---|---|
| Las entregas del turno desaparecían a las 18:00 | La base contaba los días en UTC | Zona horaria de la base en Monterrey (`11_ola3_observabilidad.sql`) |
| Subir, descargar y borrar archivos no quedaba en la bitácora | Se usaban acciones que no existen en el catálogo | Acciones válidas y la nueva `descarga` |
| Subir un archivo fallaba en una base ya existente | El validador de MongoDB exigía el contenido | `bloque_c/mongo/03_documentos_nube.js` |
| Las pruebas contra el bucket no tenían Internet | La red de datos es interna | Segunda red con salida en `correr.sh` |
| El agente de registros negaba permisos | Los roles tardan en propagarse en GCP | Esperar y comprobar en Cloud Logging |
| Pruebas nuevas hacían fallar a otras | Dejaban entregas abiertas y dependían del tráfico previo | Limpieza al terminar y pruebas autónomas |
| El instalador fallaba si Nginx estaba detenido | Se recargaba un servicio apagado | `reload-or-restart` |
| Las claves de demostración eran públicas | El repositorio es público | El instalador las cambia en la nube |
| Los archivos locales se perdían al recrear el contenedor | No había volumen | Volumen `datos_archivos` |
| Una corrida de evidencias quedó con sesiones vencidas | La computadora se suspendió a la mitad | Mantenerla activa y repetir |
| **Abierta:** reportes lentos y algunos 503 con 200 usuarios | Cada reporte encadena muchas llamadas | Propuesta: caché en Redis y resúmenes agregados (`evidencias/nube/carga/ANALISIS.md`) |
