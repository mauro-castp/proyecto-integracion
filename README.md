# Plataforma de Microhubs y Comercio de Proximidad

**Codex Innovations · Equipo 04**
Primer Parcial — Ingeniería de Software

Sistema para una red de microalmacenes de barrio ("microhubs") que surten pedidos de abarrotes en cuatro colonias del sector San Bernabé, Monterrey, Nuevo León.

## Estructura del repositorio

| Carpeta | Contenido |
|---|---|
| [`bloque_c/`](bloque_c/) | Modelo de datos: esquema y lógica de PostgreSQL, colecciones de MongoDB, claves de Redis, scripts de semilla y pruebas, diagramas conceptual/lógicos, documento del entregable |
| [`bloque_d/`](bloque_d/) | Arquitectura: los 9 diagramas (contexto, contenedores, componentes, despliegue, red, secuencia, comunicación, autenticación, almacenamiento), fuentes PlantUML, prototipos de interfaz |
| [`sistema_web/`](sistema_web/) | Aplicación Flask del Primer Parcial: sitio público, portal privado, autenticación JWT, catálogos, proceso de pedido, indicadores, bitácora. Ver [`sistema_web/README.md`](sistema_web/README.md) para instrucciones de arranque |

## Arrancar el sistema web

```bash
cd sistema_web
docker compose up --build
```

Abre `http://localhost:5000`. Cuentas de demostración y detalle completo en [`sistema_web/README.md`](sistema_web/README.md).

## Equipo

Ruth Elizabeth Soriano · Vanessa Morante López · Mauro Castillo Peña · María José Cedillo Mata · Jorge Antonio Arreola Cantú
