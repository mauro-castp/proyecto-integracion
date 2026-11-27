# Plan de pruebas y resultados · Entrega final

Codex Innovations · Equipo 04

## 1. Objetivo y alcance

Comprobar que la plataforma cumple cuatro cosas:

- sus reglas de negocio;
- sus contratos JSON y XML;
- la seguridad;
- los tres procesos integrales.

Además, que soporta volumen y carga y que se recupera de fallas parciales. El plan cubre los 26 microservicios, el portal web, las dos
apps, las tres bases de datos, el almacén de objetos y el despliegue en GCP.

## 2. Ambientes

| Ambiente | Para qué |
|---|---|
| **Local con Docker** (`docker-compose.integrado.yml`) | Desarrollo, unitarias, integración y evidencias de petición y respuesta |
| **Local sin Docker** (2 vCPU y 7 GB, PostgreSQL 16, MongoDB 7, Redis 7) | Corrida de la entrega final: volumen, carga, fallos, procesos y regresión. Ver [`MANUAL_INSTALACION.md`](MANUAL_INSTALACION.md#anexo--sin-docker-como-se-corrieron-las-pruebas-de-rendimiento) |
| **GCP** (VM e2-standard-4, Cloud Storage) | Pruebas en la nube: 401 casos, bucket real y URL firmadas (`evidencias/nube/`) |
| **Emulador Android / Windows** | Pruebas de las apps (las corrió el equipo; ver `app_escritorio/PRUEBAS_APPS.md`) |

## 3. Criterios de aceptación

- 100 % de las pruebas automatizadas en verde. Una falla solo se acepta si es del ambiente y queda explicada.
- Carga normal (50 usuarios): p95 < 500 ms y 0 % de errores. Carga alta (150): p95 < 800 ms y menos de 1 % de errores.
- Ante la caída de cualquier dependencia:
  - ningún 500;
  - respuesta 503 con `traza_id`;
  - nada a medias;
  - recuperación sin reiniciar otros servicios.
- Los tres procesos integrales completos, con su comprobación en las bases y en el almacén.

## 4. Matriz de pruebas y resultado de la corrida final (26 de noviembre de 2026)

| Tipo | Qué cubre | Cómo se corre | Resultado |
|---|---|---|---|
| **Unitarias** | formatos, validación, XSD, OpenAPI, precios, reposición, fórmulas de la Ola 2 (equilibrio, capacidad, cobertura, rutas, simulación, surtido) | `pruebas.test_unitarias`, `pruebas.test_unitarias_ola2` | **37 + 65 OK** |
| **Almacén de archivos** | URL firmada, caducidad, manipulación, bucket caído, servicios que no usan bucket | `pruebas.test_almacen` | **31 OK** |
| **Contratos** | los 26 servicios: recorridos de escritorio (XML vs XSD) y de Android (JSON vs ejemplos) | `pruebas.test_contrato` | **7 OK** |
| **Contratos (validador independiente)** | los XSD y los ejemplos con lxml | `app_escritorio/pruebas/test_contratos.py` | **10 OK** (se corrigió una prueba que seguía esperando los 9 XSD del 2.º parcial) |
| **Integración por ola** | servicios contra PostgreSQL, Redis y MongoDB reales, con permisos por perfil | `pruebas.test_ola1`, `test_ola2`, `test_ola3` | **24 + 102 + 74 OK** |
| **Integración web ↔ servicios** | el web llamando por HTTP real, panel de monitoreo, adjuntar documento | `pruebas.test_web_integracion` | **8 OK** |
| **Reglas en la base** | 26 verificaciones de las RN en triggers y funciones | `bloque_c/sql/05_pruebas_reglas.sql` | **26 de 26 PASA** |
| **Portal web** | planeación, CRUD, CSRF, exportaciones, ámbito | `sistema_web/test_planeacion`, `test_web_ampliado`, `test_planeacion_local` | **16 + 13 + 6 OK** |
| **Portal web e2e** | contra PostgreSQL y Redis reales | `sistema_web/prueba_e2e_web.py` | 5 de 6. La sexta busca `/app/07_web_ampliado.sql` (ruta de Docker): es del ambiente |
| **Sistema (procesos integrales)** | P1 cierre de entrega, P2 reabastecimiento, P3 despacho con rutas y reporte archivado, de punta a punta | `pruebas/procesos_integrales.py` | **32 de 32 pasos** ([`evidencias/procesos/`](../evidencias/procesos/procesos_integrales.md)) |
| **Petición y respuesta** | 403 casos (correctos, inválidos, inexistentes, sin permiso, token inválido o revocado, reglas, límite) | `pruebas/evidencias.py` | **403 de 403** (corrida de la Ola 3) y **401 de 401** en la nube |
| **Regresión** | todo lo anterior después de cada corrección | mismas órdenes; ver sección 6 | Sin regresiones tras las correcciones de la entrega final |
| **Seguridad** | ver sección 5 | casos AUTH, USR, DOC, SEG, ENT y PED + pruebas dirigidas | OK (sección 5) |
| **Carga** | 6 perfiles, 50 y 150 usuarios | Locust ([`pruebas_carga/`](../pruebas_carga/LEEME.md)) | 50 u.: p95 75 ms, 0 % de errores · 150 u.: p95 110 ms, 0 % de errores |
| **Estrés** | escalones de 50 hasta 500 usuarios | Locust `FORMA=escalones` | Pico de 98 peticiones/s; saturación desde 350 u. (CPU al 100 %); 0.2 % de 503 controlados, ningún 500 |
| **Recuperación** | caer de 500 a 50 usuarios; caída de dependencias | Locust + `pruebas/demo_fallos_infra.py` | p95 normal 8 s después de bajar la carga · 6 de 6 casos de falla, 33 de 33 comprobaciones ([`evidencias/fallos/`](../evidencias/fallos/fallos_infraestructura.md)) |
| **Datos masivos** | 100 000 pedidos, 279 000 líneas, 397 000 auditorías, 1.4 M de puntos GPS | `generar_volumen.py` + `medir_volumen.py` | Índices, caché, inserción y escalabilidad medidos; 4 consultas lentas corregidas ([`evidencias/volumen/`](../evidencias/volumen/LEEME.md)) |
| **Algoritmos** | calidad y tiempo de rutas y Monte Carlo | `pruebas/benchmark_algoritmos.py` | [`evidencias/algoritmos/benchmark.md`](../evidencias/algoritmos/benchmark.md) |
| **Roles** | cada perfil contra cada servicio | casos `*-0x` «sin permiso» de las evidencias + `test_ola*` (permisos por perfil) | OK |
| **Archivos** | firma real del tipo (PDF disfrazado de JPEG), tamaño, ámbito, bucket caído, URL firmada | DOC-01 a DOC-11, `test_almacen`, `test_nube` | OK |
| **Apps** | Android: 46 unitarias + 3 contra el backend + 7 instrumentadas. Escritorio: 64 comprobaciones | `./build.ps1`, `dotnet run --project pruebas` | Corridas por el equipo en el 2.º parcial (`app_escritorio/PRUEBAS_APPS.md`). **Repetir contra la nube con HTTPS** |
| **Usabilidad** | 5 personas por perfil, tareas cronometradas, cuestionario SUS | protocolo de la sección 7 | **Pendiente de aplicar** (requiere personas) |

## 5. Pruebas de seguridad

| Amenaza | Prueba | Resultado |
|---|---|---|
| Token alterado | AUTH-07: firma modificada | 401 |
| Token revocado | AUTH-10/11: `salir` y reusar en otro servicio | 401 en todos |
| Refresh reutilizado | AUTH-09 | 401 (un solo uso, con rotación) |
| Sin permiso | USR-06 y casos «sin permiso» de cada servicio | 403 y queda en la bitácora |
| Acceso a recurso ajeno (IDOR) | PED-06, SEG-03, ENT-03, DOC-04 | 404 o 403: no se revela que existe |
| XXE / DTD | AUTH-05 y el runbook | 400 XML_INVALIDO |
| Archivo disfrazado | DOC-03: PDF declarado como JPEG | 422 (se valida la firma real) |
| Fuerza bruta | intentos fallidos auditados; bloqueo a los 5; 30 inicios de sesión/min por IP | 401 → 423 · 429 con `Retry-After` |
| Inyección de fórmulas en exportaciones | `test_ola3`: neutraliza `= + - @` | OK |
| Redis caído | `demo_fallos_infra` | 503: no se deja pasar a nadie sin poder revisar la revocación |
| IP real detrás de Nginx | prueba dirigida con dos `X-Forwarded-For` | La bitácora guarda cada IP y cada una cuenta aparte (antes todo el tráfico compartía la IP del proxy) |
| Secretos | `.env` solo en la VM (permiso 600); la clave demo se cambia al instalar; la cuenta de servicio no tiene llaves; el bucket es privado | Revisado (`evidencias/nube/recursos_gcp.txt`) |
| Puertos | solo 80 y 443 abiertos; servicios y bases en 127.0.0.1 o en la red interna | `evidencias/nube/puertos.txt` |

## 6. Cómo repetir la regresión completa

```bash
C=servicios/pruebas/correr.sh                          # dentro de la red de Docker
$C test pruebas.test_unitarias pruebas.test_unitarias_ola2 pruebas.test_almacen pruebas.test_contrato
$C test pruebas.test_ola1 pruebas.test_ola2 pruebas.test_ola3
$C evidencias ola3
docker compose -f docker-compose.integrado.yml exec -T postgres psql -U microhubs -d microhubs_p1 -f /docker-entrypoint-initdb.d/05_pruebas_reglas.sql
python servicios/pruebas/procesos_integrales.py
(cd app_escritorio && python -m unittest discover -s pruebas)
```

## 7. Protocolo de usabilidad (pendiente de aplicar)

- **Participantes:** 5 por perfil principal: cliente, operador y repartidor. No pueden ser del equipo.
- **Tareas cronometradas:**

  | Perfil | Tarea | Tiempo máximo |
  |---|---|---|
  | Cliente | comprar 3 productos y ver el estado del pedido | 4 min |
  | Operador | pasar un pedido a listo y pedir reposición de un producto agotado | 4 min |
  | Repartidor | cerrar una entrega parcial con foto | 3 min |

- **Medidas:**
  - éxito sin ayuda (sí o no);
  - tiempo;
  - errores;
  - cuestionario **SUS** de 10 preguntas. La meta es 68 o más.
- **Entregable:** una tabla por persona, el SUS promedio, los tres problemas más frecuentes y qué se cambió.
