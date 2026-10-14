# Cambios de la documentación del Segundo Parcial

## Cambios de arquitectura

| Antes | Ahora | Efecto |
|---|---|---|
| Catálogos (5103) | Productos (5103), Zonas (5108) y Microhubs (5109) | Cada recurso de consulta tiene su propio servicio |
| GPS dentro de Entregas | Seguimiento (5110) | Las rutas son `/api/v1/seguimiento/{id}/ubicaciones` y `/recorrido` |
| Notificaciones (5108) | Triggers de PostgreSQL y bandeja del portal | Se quitó la API; los avisos se siguen generando |
| 8 microservicios | 10 microservicios | 15 contenedores definidos: 14 en ejecución y el de migraciones |
| 48 endpoints en el reporte | 45 operaciones en el código | El detalle está en `servicios/INVENTARIO_ENDPOINTS.md` (sin salud ni documentación) |

## Documentos

- `reporte_tecnico/Reporte_Tecnico_Segundo_Parcial_Equipo04.docx`, versión 4.3: diez fichas completas, requisitos, historias, contratos, despliegue, pruebas y trazabilidad.
- `Arquitectura_Plataforma_Microhubs (1).docx`: arquitectura de la plataforma con los diez servicios.
- `bloque_d/`: diagramas y sus fuentes PlantUML.
- `presentacion/`: presentación de 31 diapositivas, guion en PDF y el mismo contenido en texto.
- `servicios/INVENTARIO_ENDPOINTS.md`: las 45 operaciones y los casos de evidencia de cada una.
- `evidencias/`: 93 casos y, en `evidencias/complementarias/`, 3 más.
- `capturas/`: figuras del reporte; las 13 a 26 se tomaron de nuevo con el sistema de diez servicios.

## Pruebas del 13 de octubre de 2026

- Servicios: 14 unitarias, 7 de contrato y 5 de integración web.
- Web y planeación: 35 pruebas. Reglas SQL: 26 verificaciones.
- Evidencias: 93 de 93 casos y 3 de 3 complementarios.
- App de escritorio: 64 comprobaciones. App Android: 46 pruebas unitarias y 3 contra los servicios.
- Docker: el sistema se levantó desde cero con `docker compose -f docker-compose.integrado.yml up --build -d`.

No se repitieron los dos scripts de extremo a extremo del web ni las pruebas de emulador de Android.

Ejemplo de cierre de entrega: ENT-05 (entrega 129, pedido 153, monto 146.80, HTTP 201). ENT-06 repite el UUID y devuelve 200. El GPS usa SEG-01 y SEG-02.

Los documentos del Primer Parcial se quedan como antecedente.
