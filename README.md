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
| [`bloque_d/`](bloque_d/) | Arquitectura: diagramas 1 a 17 (contexto, contenedores, componentes, despliegue, red, secuencia, comunicación, autenticación, almacenamiento), fuentes PlantUML, prototipos de interfaz. Ver [`bloque_d/README.md`](bloque_d/README.md) |
| [`sistema_web/`](sistema_web/) | Portal Flask ampliado en el Segundo Parcial: sitio público, portal privado, autenticación JWT, catálogos, proceso de pedido, indicadores, bitácora. Ver [`sistema_web/README.md`](sistema_web/README.md) para instrucciones de arranque |
| [`servicios/`](servicios/) | Los diez microservicios del contrato v1, uno por responsabilidad de negocio (puertos 5101–5110): JSON y XML, JWT con Redis, MongoDB, Swagger y pruebas. Ver [`servicios/README.md`](servicios/README.md) |
| [`app_movil/`](app_movil/) | App Android del repartidor (Kotlin, solo JSON) |
| [`app_escritorio/`](app_escritorio/) | App de escritorio de planeación (C#, solo XML) y los XSD oficiales del contrato |
| [`presentacion/`](presentacion/) | Presentación actualizada de 31 diapositivas y guion por slide |

## Arrancar la plataforma completa (web + microservicios)

```bash
docker compose -f docker-compose.integrado.yml up --build -d
```

Web en `http://localhost:5000`; servicios en los puertos 5101–5110 con Swagger en `/api/v1/docs`. Para probar las apps contra
el backend: [`INSTRUCCIONES_PARTE_B.md`](INSTRUCCIONES_PARTE_B.md).

## Arrancar solo el sistema web

```bash
cd sistema_web
docker compose up --build
```

Abre `http://localhost:5000`. Cuentas de demostración y detalle completo en [`sistema_web/README.md`](sistema_web/README.md).

## Equipo

Ruth Elizabeth Soriano · Vanessa Morante López · Mauro Castillo Peña · María José Cedillo Mata · Jorge Antonio Arreola Cantú

## Video de la presentación

[Presentación Equipo 4 Microhubs en YouTube](https://youtu.be/wEvJhCQN4rM) (también en el archivo `Liga de video de Youtube 2ndo Parcial`).

## Documentación del Segundo Parcial actualizada

- `reporte_tecnico/Reporte_Tecnico_Segundo_Parcial_Equipo04.docx`: reporte integral versión 4.3, con diez fichas completas, trazabilidad y enlace del video.
- `Arquitectura_Plataforma_Microhubs (1).docx`: arquitectura vigente.
- `servicios/INVENTARIO_ENDPOINTS.md`: 45 operaciones método-ruta obtenidas del código.
- `CAMBIOS_DOCUMENTACION_SEGUNDO_PARCIAL.md`: resumen de lo que cambió en la documentación del Segundo Parcial.

Catálogos se separó en Productos, Zonas y Microhubs. Seguimiento recibe el GPS en :5110. Los avisos permanecen en PostgreSQL y el portal; :5108 ahora corresponde a Zonas.

Las evidencias adjuntas registran 93 casos aprobados el 13 de octubre de 2026 a las 21:27 UTC. Las figuras 13 a 26 del reporte se renovaron contra el despliegue de diez servicios; cómo se obtuvo cada una está en `capturas/LEEME.md`. Las pruebas del repositorio y las capturas se ejecutaron de nuevo el 13 de octubre de 2026 sobre el despliegue de diez servicios.
