# Microservicios · contrato v1 (Segundo Parcial)

**Codex Innovations · Equipo 04**

Ocho servicios Flask, cada uno en su contenedor y su puerto, que atienden a la app Android (JSON) y a la app de escritorio (XML
validado con los XSD oficiales de `app_escritorio/contratos/`). Comparten PostgreSQL, Redis y MongoDB con el sistema web, que
sigue funcionando por su cuenta.

| Servicio | Puerto | Responsabilidad | Rutas (`/api/v1/…`) | Datos |
|---|---|---|---|---|
| auth | 5101 | Sesión común JWT + Redis | `auth/login`, `auth/renovar`, `auth/salir`, `auth/validar` | PostgreSQL, Redis |
| usuarios | 5102 | Perfil y consulta de usuarios | `usuarios/yo` (GET, PATCH), `usuarios`, `usuarios/{id}` | PostgreSQL |
| catalogos | 5103 | Productos, zonas, microhubs (solo lectura) | `productos[/{id}]`, `zonas[/{id}]`, `microhubs[/{id}]` | PostgreSQL, caché Redis |
| pedidos | 5104 | Consulta y cambio de estado | `pedidos`, `pedidos/{id}`, `pedidos/{id}/historial`, `pedidos/{id}/estado` | PostgreSQL |
| entregas | 5105 | Reparto: paradas, cierre, GPS | `entregas/mias`, `entregas[/{id}]`, `entregas/{id}/resultado`, `entregas/{id}/ubicaciones`, `entregas/{id}/recorrido` | PostgreSQL, MongoDB |
| planeacion | 5106 | Viabilidad de microhubs | `candidatos[/{id}]`, `candidatos/{id}/decision`, `candidatos/{id}/simular`, `simulaciones`, `simulaciones/resumen`, `escenarios[/{id}]` | PostgreSQL, MongoDB |
| documentos | 5107 | Evidencias y archivos | `documentos`, `documentos/{id}`, `documentos/{id}/contenido`, `documentos/resumen` | MongoDB |
| notificaciones | 5108 | Bandeja de avisos (misma tabla que el web) | `notificaciones`, `notificaciones/conteo`, `notificaciones/{id}/leer` | PostgreSQL |

Cada servicio publica `GET /api/v1/salud` y su documentación en **`http://localhost:51XX/api/v1/docs`** (Swagger UI) y
`/api/v1/openapi.json`. Los ejemplos de Swagger son los archivos oficiales del contrato.

## Lo que comparten (`comun/`)

| Pieza | Archivo | Qué hace |
|---|---|---|
| Formatos | `formatos.py`, `esquemas.py` | `Accept` decide JSON o XML; todo XML de entrada se valida con los 9 XSD; DTD y entidades rechazadas |
| Autenticación | `base.py` | JWT HS256 con la misma llave que el web; Redis confirma la sesión (`auth:sesion:{id}`) y la revocación (`auth:jti:revocado:{jti}`) en cada petición |
| Autorización | `datos.py` | Permisos de la tabla `rol_permiso` (caché `cache:permisos:{rol}`, 5 min), los mismos del web |
| Errores | `base_errores.py`, `validar.py` | `{codigo, mensaje, detalles[campo, mensaje], traza_id}`; todos los errores de validación juntos |
| Límites | `base.py` | 240 solicitudes/min por IP y servicio (30 para login) en Redis; 429 con `Retry-After` |
| Registro | `base.py` | Cada petición: `logs_tecnicos` y `metricas_servicio` en MongoDB, sin tokens ni contraseñas |
| Auditoría | PostgreSQL | El servicio declara quién actúa (`app.usuario_id`, `app.rol`); los triggers del motor auditan y validan transiciones |

Los cálculos de planeación **no se duplican**: el servicio usa `sistema_web/planeacion_calc.py` y las consultas de
`sistema_web/planeacion.py`. Web, servicio y escritorio dan los mismos números.

## Datos que agrega este parcial

- `bloque_c/sql/08_microservicios.sql` (idempotente): cierre idempotente de entregas (`entrega.id_cliente_local`), evidencias y
  ubicación del cierre, tipo y referencia en `web_notificacion`, y el trigger que avisa al repartidor cuando se le asigna una entrega.
- `bloque_c/mongo/02_microservicios.js`: colecciones `documentos` y `ubicaciones_entrega` (índice 2dsphere, TTL de 180 días).
- MongoDB en uso: `documentos` (insertar, consultar, agregar), `ubicaciones_entrega` (insertar en lote, agregación del recorrido),
  `sincronizaciones_moviles` (upsert por UUID: cada reintento actualiza el mismo documento), `ejecuciones_analiticas` (cada
  simulación; resumen con `$group`), `logs_tecnicos` y `metricas_servicio`.

## Levantar todo

Desde la raíz del repositorio:

```bash
docker compose -f docker-compose.integrado.yml up --build -d
docker compose -f docker-compose.integrado.yml ps            # todos healthy; migraciones termina con código 0
docker compose -f docker-compose.integrado.yml exec entregas python pruebas/preparar_entregas.py --cantidad 2
```

Web: `http://localhost:5000`. Servicios: puertos 5101 a 5108. Cuentas: `sistema_web/README.md` (clave `Codex#2026`).
Con un volumen de PostgreSQL ya existente, el contenedor `migraciones` aplica 06, 07 y 08 sin borrar datos.

## Pruebas

Las pruebas corren los ocho servicios contra PostgreSQL y Redis reales (MongoDB en memoria con mongomock, o real si se define
`MONGO_URL`). Reproducen los recorridos con los que se probaron las apps y además validan cada XML contra los XSD y cada JSON
contra las llaves de los ejemplos oficiales. **Cambian datos: úsenlas en una base de pruebas.**

```bash
pip install -r servicios/requirements.txt mongomock
cd servicios && python -m unittest -v pruebas.test_contrato          # 7 pruebas
```

Para probar las apps contra estos servicios, ver `INSTRUCCIONES_PARTE_B.md` en la raíz.

## Decisiones

- **HTTP en los puertos locales.** Las apps permiten HTTP solo hacia `localhost` (escritorio) y `10.0.2.2` o el host fijado al
  compilar (Android debug). TLS con proxy inverso queda para el despliegue en nube del Tercer Parcial.
- **Token de renovación opaco** (`rt_…`) que se guarda en Redis como hash y sirve una sola vez; no puede usarse como acceso.
- **Notificaciones automáticas por trigger**, no por llamada entre servicios: llegan aunque el cambio lo haga el web, un servicio
  o un script.
- **MongoDB no bloquea la operación de pedidos**: si no responde, el cierre de entrega se aplica en PostgreSQL y solo se pierde
  el rastro analítico; los servicios cuyo almacén es MongoDB (documentos, recorrido, resumen) responden 503.

## Límites conocidos

- Las pruebas automáticas usan MongoDB simulado; los validadores `$jsonSchema` solo los aplica un MongoDB real.
- La contraseña de demostración es común a todas las cuentas y `SECRET_KEY` tiene un valor por omisión: cambiar ambos fuera
  de desarrollo.
- Catálogo en caché hasta 5 minutos: un cambio hecho en el web tarda ese tiempo en verse en las apps.
