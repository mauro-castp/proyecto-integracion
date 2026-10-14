# Bloque D — Arquitectura y prototipos

**Plataforma de Microhubs y Comercio de Proximidad**
Codex Innovations · Equipo 04 · Primer y Segundo Parcial

## Contenido

### `diagramas/`

Los 9 diagramas de arquitectura pedidos en el Primer Parcial: contexto, contenedores, componentes, despliegue, red, secuencia de procesos, comunicación entre aplicaciones, autenticación y almacenamiento de datos.

**Segundo Parcial.** Los diagramas 2 (contenedores) y 3 (componentes del web) se actualizaron a la arquitectura real (servicios Flask, psycopg, integración web–servicios; ya no mencionan PySide ni SQLAlchemy) y se agregaron:

| Diagrama | Contenido |
|---|---|
| `10_despliegue_microservicios` | Contenedores, redes `publica` y `datos`, puertos, volúmenes y dependencias del compose integrado |
| `11_componentes_microservicios` | Clientes, web, 10 servicios con su biblioteca `comun/`, almacenes y protocolos |
| `12_secuencia_cierre_entrega` | Proceso distribuido de la demostración: sesión, consulta, evidencia, GPS y cierre idempotente |
| `13_secuencia_autenticacion_comun` | JWT con Redis: inicio de sesión, petición protegida, renovación y revocación en web y servicios |
| `14` a `16_datos_*` | Modelo de datos de PostgreSQL en tres partes (seguridad y catálogo; pedidos y entregas; planeación y avisos); en color lo creado o ampliado en los scripts 06 a 08 |
| `17_datos_poliglota` | Qué guarda PostgreSQL, MongoDB y Redis y cómo se relacionan |

### `fuentes/`

Los `.puml` de cada diagrama más `tema.iuml`, el tema PlantUML compartido. Cambiar un color en `tema.iuml` afecta los diagramas que lo incluyen — así se mantiene consistente la paleta entre ellos y con el resto del proyecto (modelo de datos, prototipos, sistema web).

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

## Versión vigente

Los diagramas 2, 3 y 10 a 17 documentan el Segundo Parcial. Los diagramas 1 y 4 a 9 conservan el diseño histórico del Primer Parcial y no sustituyen al despliegue vigente.

El diagrama 10 representa 15 contenedores, de los cuales migraciones es de un solo uso. La exportación PNG actual procede del SVG editable `fuentes/10_despliegue_microservicios.svg`; la fuente PlantUML conserva la misma topología y las dependencias corregidas.
