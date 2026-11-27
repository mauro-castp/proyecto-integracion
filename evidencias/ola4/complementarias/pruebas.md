# Pruebas ejecutadas · microservicios v1

| ID | Servicio | Objetivo | Entrada | Esperado | Obtenido | Estado |
|---|---|---|---|---|---|---|
| DOC-11 | documentos | Agregación $group por tipo de referencia en MongoDB. | `GET /api/v1/documentos/resumen` | 200 | 200 | PASA |
| PLA-17 | planeacion | Paginación y búsqueda de escenarios compartidos con el web. | `GET /api/v1/escenarios?pagina=1&por_pagina=5` | 200 | 200 | PASA |
| USR-08 | usuarios | PUT es alias de PATCH: lo usa la app Android cuando la JVM no admite PATCH. | `PUT /api/v1/usuarios/yo` | 200 | 200 | PASA |

**Total:** 3 casos · 3 pasan · 0 fallan.