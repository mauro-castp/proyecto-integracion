# Registro de incidencias

Codex Innovations · Equipo 04 · Tercer Parcial y entrega final

Cada incidencia indica qué se vio, por qué pasaba, qué se hizo y cómo se comprobó. Las I-01 a I-08 salen de lo documentado durante
las olas (`CAMBIOS_TERCER_PARCIAL.md`). Las I-09 en adelante las encontraron las pruebas de volumen, carga, fallos e integración de
la entrega final.

| ID | Fecha | Dónde | Síntoma | Causa | Corrección | Comprobación | Severidad |
|---|---|---|---|---|---|---|---|
| I-01 | Ola 1 | `sistema_web/migrar_web.py` | Los avisos de cierre de pedido perdían su tipo y su referencia; la evidencia ENT-05 salía vacía | Cada arranque del web volvía a aplicar `07_web_ampliado.sql` y deshacía la `08` | `migrar_web.py` ya no reaplica la 07 | ENT-05 con aviso; prueba en `test_ola1` | Alta |
| I-02 | Ola 1 | PostgreSQL | Una lista de precios que empieza «hoy» empezaba mañana después de las 6 p. m. | `current_date` en UTC | `fn_hoy()` en hora de Monterrey; en la 11, zona horaria de la base | `test_ola3`: «la base cuenta los días en hora de Monterrey» | Media |
| I-03 | Ola 2 | `servicios/planeacion/app.py` | El servicio de rutas importaba el `rutas.py` del web | `sistema_web/` estaba al principio de `sys.path` | Se agrega al final de `sys.path` | `test_ola2` | Media |
| I-04 | Ola 2 | costos ↔ configuración | Cambiar `costo_km_reparto` no movía el costo por entrega | Dos fuentes del mismo supuesto | Se separaron y se documentaron (`SUPUESTOS.md`, «Dos valores que se parecen») | Escenarios de la Ola 2 | Media |
| I-05 | Ola 2 | pruebas | 84 pedidos cancelados sin devolver inventario | Las pruebas cancelaban con `UPDATE` directo | Se repuso el inventario; el ayudante de pruebas usa `fn_devolver_inventario` | Conteo de inventario | Media |
| I-06 | Ola 2 | inventario | `inventario/quiebres?dias=0` se tomaba como «sin indicar» | Validación permisiva | Rechaza `dias=0` | `test_ola2` | Baja |
| I-07 | Ola 2 | pedidos | `pedidos/resumen` sumaba la demanda no atendida de toda la red a cualquier perfil | Faltaba revisar el permiso | Solo con `reportes.ver` y sin filtro de microhub | `test_ola2` | Media |
| I-08 | Ola 2 | evidencias | `evidencias/ola2/fallo_servicios.md` se citaba pero no estaba en el repositorio | Archivo no subido | Se generó la demostración completa de fallos en `evidencias/fallos/` y se actualizaron las referencias | Revisión de enlaces | Baja |
| I-09 | 26-nov | `fn_pedidos_visibles` | Con 100 k pedidos, «la página 1» y «el pedido 5» tardaban 57 ms y 32 ms en la base, y crecían con la tabla | Función PL/pgSQL: PostgreSQL la ejecuta entera y filtra después | Función SQL de un solo `SELECT` (12_rendimiento.sql); las listas usan la tabla con la misma regla | Mismos resultados para 98 usuarios; 0.2 ms por id; `evidencias/volumen` | **Alta** |
| I-10 | 26-nov | `pedidos/resumen`, `pedidos/ventas` | `demanda/sincronizacion` de 170 días: 5 s con 10 k pedidos y **37.5 s** con 100 k; reportes de 1.1 s | Filtro `::date BETWEEN` sin índice y todo el periodo recalculado **dos veces por página**, en ~70 páginas | Rango de `creado_en`, un solo cálculo por petición, copia en Redis para las páginas 2 en adelante e índices nuevos | 1.1 s y 212 ms (`evidencias/volumen`) | **Alta** |
| I-11 | 26-nov | `demanda/sincronizacion` | Miles de `INSERT` de uno en uno | Bucle fila por fila | `executemany` | Incluido en I-10 | Baja |
| I-12 | 26-nov | servicios y web detrás de Nginx | En la nube **todos los usuarios compartían un solo límite** (240/min por servicio y 30 inicios de sesión/min) y la bitácora guardaba la IP del proxy | `request.remote_addr` es Nginx; no había ProxyFix | `DETRAS_DE_PROXY=1` (ProxyFix con 1 proxy de confianza), puesto por `instalar_vm.sh` | Dos IP de `X-Forwarded-For`: dos IP en la bitácora y dos contadores | **Alta** |
| I-13 | 26-nov | `docker-compose.integrado.yml` | `LIMITE_POR_MINUTO` y `LIMITE_LOGIN_POR_MINUTO` no se podían cambiar en Docker, aunque el README decía que sí | No estaban en `x-entorno` | Agregadas, junto con `DETRAS_DE_PROXY` | Revisión del compose | Media |
| I-14 | 26-nov | MongoDB caído | `documentos/resumen` respondía **500** tras 6 s, y **todas** las peticiones de todos los servicios tardaban 4.5 s | Sin manejador para `PyMongoError`; cada petición esperaba 2 s × 2 para registrar en MongoDB y 2 s más reintentando índices | 503 para `PyMongoError` y un cortacircuitos de 30 s para las escrituras accesorias | `demo_fallos_infra`: 503 y el catálogo en 3 ms desde la segunda petición | **Alta** |
| I-15 | 26-nov | rutas → entregas | Confirmar un plan de rutas no creaba las entregas: el flujo de la planeación a la entrega estaba incompleto | Faltaba la operación de asignación en el servicio dueño | `POST entregas/asignaciones` (todo o nada) y saga con compensación en `rutas/confirmar {despachar: true}` | P3 de `procesos_integrales`; prueba de compensación (403 → el plan vuelve a «propuesto») | **Alta** |
| I-16 | 26-nov | caché de resúmenes | `test_ola3` detectó totales viejos en los reportes tras crear pedidos | La primera versión de la corrección I-10 también servía la página 1 desde la caché | La página 1 siempre se calcula y la caché solo sirve el resto del recorrido | `test_ola3` 74 OK | Media |
| I-17 | 26-nov | archivos | Los reportes exportados no quedaban en el bucket y no había dónde guardar el comprobante de una orden de compra | No estaba en el alcance anterior | Archivo de exportaciones (`reportes/AAAA/MM/…`, 13_entrega_final.sql) con URL firmada; tipo de referencia `orden_compra` en documentos, XSD y validador | P2 y P3 de `procesos_integrales` | Media |
| I-18 | 26-nov | `app_escritorio/pruebas/test_contratos.py` | 1 falla desde la Ola 1 | La prueba esperaba exactamente los 9 XSD del Segundo Parcial | Comprueba que existan todos (2.º parcial + olas) | 10 OK | Baja |
| I-19 | 26-nov | Redis | Al reiniciar Redis se cierran todas las sesiones | Redis sin persistencia + cierre seguro | **Decisión aceptada** y documentada (runbook) | `demo_fallos_infra` | — |
| I-20 | 26-nov | reportes con saturación | Con 450+ usuarios, una cadena de llamadas puede tardar más de 60 s antes de responder 503 | Cada salto espera hasta 4 s y no hay plazo total | **Pendiente**: plazo total por petición o cortacircuitos en `comun/clientes.py` | Locust, escenario de estrés | Media |
| I-21 | 26-nov | GCP y apps | Las apps instalables no podían conectarse a la nube | Dos causas: el certificado era autofirmado y las apps buscaban cada servicio por su puerto, cerrado en la nube | Certificado de Let's Encrypt; con ruta en el servidor las apps llaman por nombre (`/servicios/<nombre>/`) | Pruebas de ambas apps por una puerta única local y 401 del contrato contra la nube | **Alta** |
| I-22 | 26-nov | archivos | Subir, descargar y borrar archivos no quedaba en la bitácora | Se usaban acciones que no existen en el catálogo | Acciones válidas y la nueva `descarga` | Casos de evidencia DOC | Media |
| I-23 | 26-nov | GCP | El agente de registros respondía «permiso denegado» | Los roles tardan en propagarse | Esperar y comprobar en Cloud Logging | `evidencias/nube/cloud_logging.txt` | Baja |
| I-24 | 26-nov | GCP | Las claves de demostración de la nube eran las del repositorio público | El instalador no las cambiaba | `cambiar_claves_demo.py` genera una en la VM | `seguridad.md` | **Alta** |
| I-25 | 26-nov | `instalar_vm.sh` | Fallaba si Nginx estaba detenido | Se recargaba un servicio apagado | `reload-or-restart` | Reinstalación en la VM | Baja |
| I-26 | 26-nov | `docker-compose.integrado.yml` | Los archivos locales se perdían al recrear el contenedor (documentos y, después, las exportaciones de reportes) | Sin volumen | Volumen `datos_archivos` en documentos y reportes | `correr.sh procesos`: 32 de 32 | Media |
| I-27 | 26-nov | MongoDB ya existente | No se podía adjuntar el comprobante de una orden de compra | El validador anterior no conocía `orden_compra` | `instalar_vm.sh` corre `03_documentos_nube.js`; en local se corre una vez | P2 de `procesos_integrales` | Media |
| I-28 | 26-nov | pruebas | Unas pruebas hacían fallar a otras | Dejaban entregas abiertas y dependían del tráfico previo | Limpieza al terminar y pruebas autónomas | `test_ola3` y `test_ola4` | Baja |
| I-29 | 26-nov | pruebas en la nube | La corrida de evidencias se detenía con un 429 | Más de 30 inicios de sesión por minuto | La corrida espera lo que pide el servicio | 436 de 436 | Baja |
| I-30 | 26-nov | app Android | Las pruebas nuevas no compilaban con Gradle | Usaban métodos que el `org.json` de Android no tiene | Funciones propias en la prueba | `build.ps1` y `BackendRealTest` | Baja |
| I-31 | 27-nov | GCP | Al encender la máquina los 26 servicios quedaban degradados | PostgreSQL, Redis y MongoDB no tenían política de reinicio; no se notaba porque siempre se corría el instalador | `restart: unless-stopped` en las tres bases | Reinicio de la VM: 26 de 26 sanos sin correr el instalador | **Alta** |
| I-32 | 27-nov | portal | La pantalla «Archivos» guardaba el archivo dentro de PostgreSQL | Se escribió antes de tener el almacén de objetos y no se migró | Usa el servicio `documentos` (bucket); `15_archivos_bucket.sql` y `migrar_web_archivo.py` | `prueba_e2e_web` 6 de 6 y prueba en la nube | **Alta** |
| I-33 | 27-nov | salud | Solo 5 servicios informaban MongoDB y 1 el bucket | Cada servicio revisaba únicamente sus dependencias | Los 26 informan las cuatro y publican `/health/*` | `test_almacen` y los 26 en la nube | Media |
| I-34 | 27-nov | pruebas | Dos pruebas de la Ola 2 fallaban según los datos acumulados | Suponían cantidades y borraban planes con entregas | Pruebas independientes de los datos | `test_ola2` 102 OK | Baja |

Plantilla para nuevas incidencias:

```
| I-NN | fecha | componente | qué se vio (con traza si hay) | por qué pasaba | qué se cambió (archivo) | cómo se comprobó | Alta/Media/Baja |
```
