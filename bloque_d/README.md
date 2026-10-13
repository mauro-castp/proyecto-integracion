# Bloque D — Arquitectura y prototipos

**Plataforma de Microhubs y Comercio de Proximidad**
Codex Innovations · Equipo 04 · Primer Parcial

## Contenido

### `diagramas/`

Los 9 diagramas de arquitectura pedidos en el Primer Parcial: contexto, contenedores, componentes, despliegue, red, secuencia de procesos, comunicación entre aplicaciones, autenticación y almacenamiento de datos.

**Segundo Parcial.** Los diagramas 2 (contenedores) y 3 (componentes del web) se actualizaron a la arquitectura real (servicios Flask, psycopg, integración web–servicios; ya no mencionan PySide ni SQLAlchemy) y se agregaron:

| Diagrama | Contenido |
|---|---|
| `10_despliegue_microservicios` | Contenedores, redes `publica` y `datos`, puertos, volúmenes y dependencias del compose integrado |
| `11_componentes_microservicios` | Clientes, web, 8 servicios con su biblioteca `comun/`, almacenes y protocolos |
| `12_secuencia_cierre_entrega` | Proceso distribuido de la demostración: sesión, consulta, evidencia, GPS y cierre idempotente |
| `13_secuencia_autenticacion_comun` | JWT con Redis: inicio de sesión, petición protegida, renovación y revocación en web y servicios |
| `14` a `16_datos_*` | Modelo de datos de PostgreSQL en tres partes (seguridad y catálogo; pedidos y entregas; planeación y avisos); en color lo creado o ampliado en los scripts 06 a 08 |
| `17_datos_poliglota` | Qué guarda PostgreSQL, MongoDB y Redis y cómo se relacionan |

### `fuentes/`

Los `.puml` de cada diagrama más `tema.iuml`, el tema PlantUML compartido por los nueve. Cambiar un color en `tema.iuml` cambia los nueve diagramas — así se mantiene consistente la paleta entre ellos y con el resto del proyecto (modelo de datos, prototipos, sistema web).

Para regenerar un diagrama a partir de su fuente hace falta PlantUML:

```bash
plantuml fuentes/01_contexto.puml -o ../diagramas
# o con Docker:
docker run --rm -v "$PWD/fuentes:/data" -v "$PWD/diagramas:/out" -w /data plantuml/plantuml -tpng -o /out 10_despliegue_microservicios.puml
```

### `prototipos.html`

Un solo archivo con 9 pantallas de las 3 plataformas (web, móvil, escritorio) y 4 interacciones funcionales. `revisar.py` hace una verificación automatizada del prototipo.

### `capturas/`

Capturas de pantalla del prototipo usadas como evidencia documental.

---

## Nota

Los prototipos son maquetas de interfaz — a diferencia de `sistema_web/`, que sí guarda y consulta información real en PostgreSQL. `prototipos.html` cubre las pantallas de móvil y escritorio, cuya implementación real corresponde al Segundo Parcial.
