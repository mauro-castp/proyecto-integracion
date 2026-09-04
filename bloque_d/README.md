# Bloque D — Arquitectura y prototipos

**Plataforma de Microhubs y Comercio de Proximidad**
Codex Innovations · Equipo 04 · Primer Parcial

## Contenido

### `diagramas/`

Los 9 diagramas de arquitectura pedidos en el Primer Parcial: contexto, contenedores, componentes, despliegue, red, secuencia de procesos, comunicación entre aplicaciones, autenticación y almacenamiento de datos.

### `fuentes/`

Los `.puml` de cada diagrama más `tema.iuml`, el tema PlantUML compartido por los nueve. Cambiar un color en `tema.iuml` cambia los nueve diagramas — así se mantiene consistente la paleta entre ellos y con el resto del proyecto (modelo de datos, prototipos, sistema web).

Para regenerar un diagrama a partir de su fuente hace falta PlantUML:

```bash
plantuml fuentes/01_contexto.puml -o ../diagramas
```

### `prototipos.html`

Un solo archivo con 9 pantallas de las 3 plataformas (web, móvil, escritorio) y 4 interacciones funcionales. `revisar.py` hace una verificación automatizada del prototipo.

### `capturas/`

Capturas de pantalla del prototipo usadas como evidencia documental.

---

## Nota

Los prototipos son maquetas de interfaz — a diferencia de `sistema_web/`, que sí guarda y consulta información real en PostgreSQL. `prototipos.html` cubre las pantallas de móvil y escritorio, cuya implementación real corresponde al Segundo Parcial.
