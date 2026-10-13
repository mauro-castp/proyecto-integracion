# Plataforma de Microhubs y Comercio de Proximidad

**Codex Innovations · Equipo 04**
Segundo Parcial — Integración de Aplicaciones Computacionales

Sistema para una red de microalmacenes de barrio ("microhubs") que surten pedidos de abarrotes en cuatro colonias del sector San Bernabé, Monterrey, Nuevo León.

## Estructura del repositorio

| Carpeta | Contenido |
|---|---|
| [`bloque_a/`](bloque_a/) | Análisis del problema, matriz de perfiles y permisos, propuesta del proyecto (incluye el plan de trabajo del semestre) |
| [`bloque_b/`](bloque_b/) | Requerimientos funcionales y no funcionales, reglas de negocio, historias de usuario, casos de uso, matriz de trazabilidad |
| [`bloque_c/`](bloque_c/) | Modelo de datos: esquema y lógica de PostgreSQL, colecciones de MongoDB, claves de Redis, scripts de semilla y pruebas, diagramas conceptual/lógicos, documento del entregable. Ver [`bloque_c/README.md`](bloque_c/README.md) |
| [`bloque_d/`](bloque_d/) | Arquitectura: los 9 diagramas (contexto, contenedores, componentes, despliegue, red, secuencia, comunicación, autenticación, almacenamiento), fuentes PlantUML, prototipos de interfaz. Ver [`bloque_d/README.md`](bloque_d/README.md) |
| [`sistema_web/`](sistema_web/) | Aplicación Flask del Primer Parcial: sitio público, portal privado, autenticación JWT, catálogos, proceso de pedido, indicadores, bitácora. Ver [`sistema_web/README.md`](sistema_web/README.md) para instrucciones de arranque |
| [`servicios/`](servicios/) | Los ocho microservicios del contrato v1 (puertos 5101–5108): JSON y XML, JWT con Redis, MongoDB, Swagger y pruebas. Ver [`servicios/README.md`](servicios/README.md) |
| [`app_movil/`](app_movil/) | App Android del repartidor (Kotlin, solo JSON) |
| [`app_escritorio/`](app_escritorio/) | App de escritorio de planeación (C#, solo XML) y los XSD oficiales del contrato |
| [`presentacion/`](presentacion/) | Diapositivas de la demostración técnica, con capturas reales del sistema corriendo |

## Arrancar la plataforma completa (web + microservicios)

```bash
docker compose -f docker-compose.integrado.yml up --build -d
```

Web en `http://localhost:5000`; servicios en los puertos 5101–5108 con Swagger en `/api/v1/docs`. Para probar las apps contra
el backend: [`INSTRUCCIONES_PARTE_B.md`](INSTRUCCIONES_PARTE_B.md).

## Arrancar solo el sistema web

```bash
cd sistema_web
docker compose up --build
```

Abre `http://localhost:5000`. Cuentas de demostración y detalle completo en [`sistema_web/README.md`](sistema_web/README.md).

## Equipo

Ruth Elizabeth Soriano · Vanessa Morante López · Mauro Castillo Peña · María José Cedillo Mata · Jorge Antonio Arreola Cantú
