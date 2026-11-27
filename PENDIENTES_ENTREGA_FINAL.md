# Pendientes para la entrega final · estado al 26 de noviembre de 2026

La primera versión de este archivo listaba lo que faltaba en el repositorio. Este documento parte de esa lista, la actualiza con lo que
ya se resolvió y deja **solo lo que necesita al equipo**: acceso a GCP, Windows y Android Studio, personas o grabación.

## ✅ Resuelto en el repositorio

| Lineamiento | Qué se hizo | Dónde |
|---|---|---|
| Pruebas de carga con Locust | 6 perfiles; normal, alta, estrés por escalones, recuperación y protección; resultados con p95, p99, RPS, saturación y endpoints lentos | `pruebas_carga/`, `evidencias/carga/` |
| Grandes volúmenes | 100 000 pedidos y 1.4 M de puntos GPS; inserción, índices, caché con y sin Redis, escalabilidad y recursos; 4 consultas lentas corregidas | `bloque_c/scripts/generar_volumen.py`, `evidencias/volumen/` |
| Algoritmo documentado | Los 11 elementos y un benchmark de rutas y Monte Carlo | `docs/ALGORITMOS.md`, `evidencias/algoritmos/` |
| Demostración de fallos | Servicio, Redis, MongoDB, PostgreSQL, bucket y tiempo excedido: 6 de 6 | `servicios/pruebas/demo_fallos_infra.py`, `evidencias/fallos/`, `docs/RUNBOOK_FALLOS.md` |
| 3 procesos integrales | P1 (Android), P2 y P3 (web) de punta a punta: 32 de 32 pasos; nuevas pantallas web y saga rutas → entregas | `sistema_web/procesos.py`, `evidencias/procesos/` |
| Archivos en el bucket | Comprobantes de orden de compra y reportes exportados, con URL firmada | servicios documentos y reportes, `13_entrega_final.sql` |
| Seguridad | IP real detrás de Nginx (`DETRAS_DE_PROXY`) y límites configurables en Docker | `comun/base.py`, compose, `instalar_vm.sh` |
| Documentación | Expediente (31 secciones, también en Word), manuales de instalación, técnico y de usuario, plan de pruebas, incidencias, guía de estudio, guion del video y de la presentación, diagramas 18–21 | `docs/`, `reporte_tecnico/`, `bloque_d/` |
| Coherencia del repositorio | README, CAMBIOS (Ola 3 y final), índices de evidencias, inventario de endpoints, prueba de XSD corregida | raíz y carpetas |

## ⏳ Lo que tiene que hacer el equipo (en este orden)

1. **Desplegar esta versión en la VM** (`docs/MANUAL_INSTALACION.md` §2). Después, en MongoDB:
   `mongosh microhubs_eventos < bloque_c/mongo/03_documentos_nube.js`.
2. **Activar HTTPS**: `bash deploy/gcp/instalar_vm.sh --sin-construir --https <correo>`. Sin esto las apps instalables no se conectan
   (I-21).
3. **Repetir en la nube**, contra HTTPS:
   - `test_nube`;
   - `procesos_integrales.py` (con `GCS_BUCKET`);
   - `demo_fallos_infra.py` (con `DETENER=…docker compose…`);
   - la corrida «alta» de Locust **desde una laptop** (`pruebas_carga/LEEME.md`, sección de la nube).

   Guarda las salidas en `evidencias/nube/`.
4. **APK release firmado** y **ZIP de la app de escritorio** apuntando a la URL HTTPS (`MANUAL_INSTALACION.md` §3 y §4). Prueba la
   instalación en un teléfono y en una PC limpia. **No subas el keystore.**
5. **Video de la entrega final** con `docs/GUION_VIDEO_Y_PRESENTACION.md` (parte A). Pon el enlace en el README.
6. **Presentación final** con las 16 partes de la parte B del guion.
7. **Pruebas de usabilidad**: 5 personas por perfil y SUS (`docs/PLAN_DE_PRUEBAS.md` §7).
8. **Bitácora de participación** (`docs/BITACORA_PARTICIPACION.md`), a partir de `git log`.
9. **Reflexión individual de cada integrante** (`docs/REFLEXION_INDIVIDUAL_PLANTILLA.md` → `docs/reflexiones/`), escrita por cada quien.
10. **Confirmar con el profesor qué es «desplegado en ubiquitous»**. En el repositorio no hay nada al respecto.
11. **Entrega individual**: cada integrante sube la suya. Quien no la suba tiene 0.
12. **Ensayo** con `docs/GUIA_ESTUDIO_PREGUNTAS.md` y `docs/RUNBOOK_FALLOS.md`: cada integrante debe poder explicar todo, no solo su parte.

## Opcionales que suman

- **Android**:
  - bandeja de avisos (`notificaciones`, 5124);
  - cola sin conexión que mande los cierres al servicio `sincronizacion`. Hoy la app dice «sin cola offline».
- **Escritorio**: pantallas de punto de equilibrio, simulación y rutas en XML (los XSD ya existen).
- **Plazo total por petición** o cortacircuitos en `comun/clientes.py` (I-20).
- **Más workers** para pedidos, productos y auth en la VM (`-w 4`), que son los primeros en hacer fila según Locust.
