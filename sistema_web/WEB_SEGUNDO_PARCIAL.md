# Web ampliado · parte C

Implementación de la parte asignada a Vanessa en `PLAN_SEGUNDO_PARCIAL.md`. Cambios limitados al sistema web y a `bloque_c/sql/07_web_ampliado.sql`. La rama es `codex/vanessa-web-ampliado`, independiente de las aplicaciones cliente.

## Funciones disponibles

- Paginación SQL y búsqueda en productos, categorías, microhubs, zonas, usuarios, mis pedidos, bandeja, pendientes y bitácora. Las listas administrativas admiten filtro de estatus; las páginas mantienen los filtros.
- `/web/reportes`: filtro por fechas, estado, folio y microhub; indicadores de cantidad e importe; gráficas de estados y pedidos por día; acceso al historial del pedido. El importe incluye los estados seleccionados: no es una medida de ingresos cobrados.
- `/web/reportes.csv`: exporta todos los resultados del filtro, independientemente de la página. Límite de 10 000 pedidos; al superarlo pide reducir filtros. CSV UTF-8 con BOM y protección contra fórmulas de hoja de cálculo.
- `/web/archivos`: carga de PDF, PNG y JPEG de hasta 5 MB; valida extensión y firma inicial, genera ID aleatorio y descarga como adjunto. Cada usuario puede consultar únicamente sus propios archivos. El contenido se almacena en PostgreSQL `bytea`, sin depender de discos efímeros de contenedores.
- `/web/notificaciones`: bandeja personal, filtro de pendientes y marcado como leído. El administrador puede enviar avisos a usuarios activos. Un trigger genera un aviso al cliente cuando un pedido pasa a entregado, parcial, fallido o cancelado, incluso si lo cambia otro componente que usa la misma base.
- `/web/roles`: el administrador puede consultar perfiles y asignar permisos del nuevo módulo; conserva los permisos de operación anteriores y no puede quitar el perfil administrador. Las asignaciones actualizadas invalidan su caché en Redis. No se delega administración de roles ni envío de avisos desde esta pantalla.
- Dos perfiles nuevos: `analista` (consulta/exportación sin modificar pedidos) y `supervisor` (consulta/exportación restringida al microhub asignado). Aparecen en el CRUD de usuarios existente. No se crean credenciales nuevas automáticamente.

Las rutas nuevas comprueban permisos en el servidor y los POST exigen CSRF. El ámbito del supervisor se aplica a reportes, CSV e historial, aunque cambie el filtro en la URL. El módulo sigue funcionando sin los ocho microservicios.

## Arranque

Desde `sistema_web/`:

```powershell
docker compose up --build -d
```

El primer arranque carga el SQL 07 desde `initdb`. Con volúmenes existentes, `migrar_web.py` lo aplica después de la migración de planeación y antes de Gunicorn. Reaplicar no borra datos ni repone permisos retirados. No modificar ni volver a ejecutar el SQL 01 sobre una base que quieras conservar.

Para aplicarlo fuera de Docker, configura `PG_DSN`, `REDIS_URL` y `SECRET_KEY`, y ejecuta `python migrar_web.py` después de los scripts 01–06. El SQL de migración es transaccional.

Demo sin infraestructura:

```powershell
python -m pip install -r requirements.txt
python app_local.py
```

El modo local no autentica: usa el administrador demo y SQLite, con 65 pedidos de ejemplo señalados expresamente en el reporte. No usarlo como despliegue real. Archivos, avisos y asignaciones de permisos locales se conservan en la base SQLite.

## Pruebas y evidencia

```powershell
python -m unittest -v test_planeacion.py test_planeacion_local.py test_web_ampliado.py
```

Resultado: **35 pruebas aprobadas** (22 de regresión + 13 nuevas). Cubren páginas, paginación y filtros, entradas inválidas, CSV, permisos, CSRF, aislamiento entre propietarios/destinatarios, archivos inválidos/grandes y persistencia de cambios de permisos.

Pruebas PostgreSQL/Redis, exclusivamente sobre un entorno aislado:

```powershell
$env:WEB_PORT='5055'
docker compose -p microhubs-web-prueba up --build -d
docker compose -p microhubs-web-prueba exec -T -e WEB_PRUEBA_AISLADA=1 web python prueba_e2e_web.py
```

Resultado: **6 pruebas de integración aprobadas**. Verifican salud, listas existentes, reportes/CSV/historial, descarga `bytea` y aislamiento, avisos reales, trigger de cierre y reaplicación de migración sin restituir permisos. Las pruebas de archivos y avisos dejan datos de ensayo en esa base aislada; las de cierre y reaplicación hacen rollback. No ejecutar este script en la base del equipo.

Se verificaron en el navegador el reporte, el filtro de entregados, ambas gráficas y la disposición en pantalla estrecha, sin errores JavaScript. Evidencia: [reporte-web.png](evidencias/reporte-web.png).

## Ensayo de demostración

1. Entrar con la cuenta demo `admin@codex.mx`, clave `Codex#2026`.
2. Abrir Reportes, seleccionar entregados, cambiar de página y exportar CSV. Abrir el folio para revisar el historial.
3. Subir un PDF/imagen en Archivos y descargarlo. Otra cuenta no debe poder abrir ese ID.
4. En Notificaciones, enviar un aviso a un operador. Entrar con ese operador y marcarlo como leído.
5. En Usuarios, asignar analista o supervisor a una cuenta de prueba (el supervisor exige microhub). Verificar su ámbito en Reportes.
6. En Perfiles, retirar exportación al analista y comprobar que el CSV devuelve 403.
7. Cerrar un pedido mediante el flujo operativo existente y verificar el aviso en la cuenta del cliente.

## Límites y decisiones

Highcharts 12.4.0 y su módulo de accesibilidad se cargan del CDN oficial, siguiendo su [documentación de instalación](https://www.highcharts.com/docs/getting-started/installation). Si no hay Internet, la tabla y CSV siguen disponibles y se muestra un aviso; la gráfica requiere CDN. Para una demostración sin Internet se pueden alojar los archivos de Highcharts localmente respetando su licencia.

Los reportes interpretan fechas y agrupación diaria en `America/Mexico_City`. El rango máximo es de 366 días. La carga comprueba firma inicial y tamaño, no realiza análisis antivirus ni validación completa de documentos. Los archivos son privados del usuario y todavía no se asocian a evidencias móviles; esa integración necesita el contrato de la parte A. Los avisos se actualizan al recargar; no se implementan notificaciones push.

La pantalla de perfiles administra únicamente los permisos nuevos, no un constructor arbitrario de roles. Las cuentas y altas/bajas se gestionan con el CRUD previo. La demostración integral con las apps cliente y microservicios sigue pendiente de sus contratos definitivos.
