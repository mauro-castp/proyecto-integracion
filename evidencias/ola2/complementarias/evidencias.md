# Evidencias de petición y respuesta · microservicios v1

Generado el 2026-10-20 06:33 contra los servicios en ejecución. 3 de 3 casos pasan.

## Servicio documentos · puerto 5107

### DOC-11 · Resumen de documentos · PASA

**Objetivo.** Agregación $group por tipo de referencia en MongoDB.

**Petición.** `GET http://documentos:5107/api/v1/documentos/resumen`

```http
Accept: application/json
X-Traza-Id: 7490e737-2c0f-4d59-bc5c-1dd466285042
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 10 ms · traza `7490e737-2c0f-4d59-bc5c-1dd466285042`

```json
{
  "total": 22,
  "tamano_total_bytes": 6072,
  "por_tipo": [
    {
      "referencia_tipo": "entrega",
      "cantidad": 17,
      "tamano_bytes": 4692
    },
    {
      "referencia_tipo": "pedido",
      "cantidad": 3,
      "tamano_bytes": 828
    },
    {
      "referencia_tipo": "usuario",
      "cantidad": 2,
      "tamano_bytes": 552
    }
  ]
}
```

**Explicación.** Pipeline $group sobre referencia.tipo con conteo y suma de bytes; lo consume el tablero Microservicios del web.

**Evidencia en MongoDB.** `db.documentos.aggregate([{$group:{_id:'$referencia.tipo', cantidad:{$sum:1}, tamano_bytes:{$sum:'$tamano_bytes'}}}, {$sort:{_id:1}}])`

```json
[
  {
    "_id": "entrega",
    "cantidad": 17,
    "tamano_bytes": 4692
  },
  {
    "_id": "pedido",
    "cantidad": 3,
    "tamano_bytes": 828
  },
  {
    "_id": "usuario",
    "cantidad": 2,
    "tamano_bytes": 552
  }
]
```

## Servicio planeacion · puerto 5106

### PLA-17 · Lista de escenarios guardados · PASA

**Objetivo.** Paginación y búsqueda de escenarios compartidos con el web.

**Petición.** `GET http://planeacion:5106/api/v1/escenarios?pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 20aae88d-6de2-4d43-bb12-6447e38083c8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 44 ms · traza `20aae88d-6de2-4d43-bb12-6447e38083c8`

```json
{
  "datos": [
    {
      "id": 10,
      "nombre": "Escenario complementario",
      "candidato_id": 1,
      "supuestos": {
        "demanda_diaria": 120.0,
        "operadores": 3,
        "repartidores": 4,
        "ticket": 135.0,
        "costo_entrega": 22.0,
        "margen_bruto": 0.28,
        "renta": 18000.0,
        "nomina": 42000.0,
        "servicios": 7000.0,
        "otros": 5000.0,
        "distancia_km": 2.4,
        "capacidad_fisica": 150
      },
      "resultados": {
        "atendidos": 120.0,
        "rechazados": 0.0,
        "utilizacion": 80.0,
        "nivel": "atencion",
        "tiempo_estimado_min": 19.4,
        "operadores_requeridos": 3,
        "repartidores_requeridos": 2,
        "ingreso_dia": 16200.0,
        "margen_dia": -504.0,
        "costo_por_pedido": 42.0,
        "equilibrio": {
          "margen_pedido": 15.8,
          "mensual": 4557.0,
          "diario": 151.9
        },
        "decision": "NO VIABLE CON LOS SUPUESTOS ACTUALES",
        "explicacion": [
          "la demanda atendida (120/día) no alcanza el equilibrio (152/día)",
          "el espacio físico del local limita la capacidad",
          "reducir costos fijos, aumentar ticket o buscar una ubicación con más demanda"
        ]
      },
      "creado_en": "2026-10-20T00:33:39-06:00"
    },
    {
      "id": 5,
      "nombre": "Escenario de prueba D-9da61c72",
      "candidato_id": 52,
      "supuestos": {
        "demanda_diaria": 120.0,
        "operadores": 3,
        "repartidores": 4,
        "ticket": 135.0,
        "costo_entrega": 22.0,
        "margen_bruto": 0.28,
        "renta": 18000.0,
        "nomina": 42000.0,
        "servicios": 7000.0,
        "otros": 5000.0,
        "distancia_km": 2.4,
        "capacidad_fisica": 150
      },
      "resultados": {
        "atendidos": 120.0,
        "rechazados": 0.0,
        "utilizacion": 80.0,
        "nivel": "atencion",
        "tiempo_estimado_min": 19.4,
        "operadores_requeridos": 3,
        "repartidores_requeridos": 2,
        "ingreso_dia": 16200.0,
        "margen_dia": -504.0,
        "costo_por_pedido": 42.0,
        "equilibrio": {
          "margen_pedido": 15.8,
          "mensual": 4557.0,
          "diario": 151.9
        },
        "decision": "NO VIABLE CON LOS SUPUESTOS ACTUALES",
        "explicacion": [
          "la demanda atendida (120/día) no alcanza el equilibrio (152/día)",
          "el espacio físico del local limita la capacidad",
          "reducir costos fijos, aumentar ticket o buscar una ubicación con más demanda"
        ]
      },
      "creado_en": "2026-10-20T00:16:11-06:00"
    },
    {
      "id": 4,
      "nombre": "Escenario de prueba D-1792460274",
      "candidato_id": 25,
      "supuestos": {
        "demanda_diaria": 120.0,
        "operadores": 3,
        "repartidores": 4,
        "ticket": 135.0,
        "costo_entrega": 22.0,
        "margen_bruto": 0.28,
        "renta": 18000.0,
        "nomina": 42000.0,
        "servicios": 7000.0,
        "otros": 5000.0,
        "distancia_km": 2.4,
        "capacidad_fisica": 150
      },
      "resultados": {
        "atendidos": 120.0,
        "rechazados": 0.0,
        "utilizacion": 80.0,
        "nivel": "atencion",
        "tiempo_estimado_min": 19.4,
        "operadores_requeridos": 3,
        "repartidores_requeridos": 2,
        "ingreso_dia": 16200.0,
        "margen_dia": -504.0,
        "costo_por_pedido": 42.0,
        "equilibrio": {
          "margen_pedido": 15.8,
          "mensual": 4557.0,
          "diario": 151.9
        },
        "decision": "NO VIABLE CON LOS SUPUESTOS ACTUALES",
        "explicacion": [
          "la demanda atendida (120/día) no alcanza el equilibrio (152/día)",
          "el espacio físico del local limita la capacidad",
          "reducir costos fijos, aumentar ticket o buscar una ubicación con más demanda"
        ]
      },
      "creado_en": "2026-10-19T19:37:55-06:00"
    },
    {
      "id": 3,
      "nombre": "Escenario de prueba D-de823ae6",
      "candidato_id": 18,
      "supuestos": {
        "demanda_diaria": 120.0,
        "operadores": 3,
        "repartidores": 4,
        "ticket": 135.0,
        "costo_entrega": 22.0,
        "margen_bruto": 0.28,
        "renta": 18000.0,
        "nomina": 42000.0,
        "servicios": 7000.0,
        "otros": 5000.0,
        "distancia_km": 2.4,
        "capacidad_fisica": 150
      },
      "resultados": {
        "atendidos": 120.0,
        "rechazados": 0.0,
        "utilizacion": 80.0,
        "nivel": "atencion",
        "tiempo_estimado_min": 19.4,
        "operadores_requeridos": 3,
        "repartidores_requeridos": 2,
        "ingreso_dia": 16200.0,
        "margen_dia": -504.0,
        "costo_por_pedido": 42.0,
        "equilibrio": {
          "margen_pedido": 15.8,
          "mensual": 4557.0,
          "diario": 151.9
        },
        "decision": "NO VIABLE CON LOS SUPUESTOS ACTUALES",
        "explicacion": [
          "la demanda atendida (120/día) no alcanza el equilibrio (152/día)",
          "el espacio físico del local limita la capacidad",
          "reducir costos fijos, aumentar ticket o buscar una ubicación con más demanda"
        ]
      },
      "creado_en": "2026-10-19T19:32:15-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 4,
    "paginas": 1
  }
}
```

**Evidencia en PostgreSQL.** `SELECT id, nombre, ubicacion_candidata_id, creado_por FROM escenario_planeacion ORDER BY id DESC LIMIT 3`

```json
[
  {
    "id": 10,
    "nombre": "Escenario complementario",
    "ubicacion_candidata_id": 1,
    "creado_por": 5
  },
  {
    "id": 5,
    "nombre": "Escenario de prueba D-9da61c72",
    "ubicacion_candidata_id": 52,
    "creado_por": 5
  },
  {
    "id": 4,
    "nombre": "Escenario de prueba D-1792460274",
    "ubicacion_candidata_id": 25,
    "creado_por": 5
  }
]
```

## Servicio usuarios · puerto 5102

### USR-08 · Actualizar mi teléfono (PUT) · PASA

**Objetivo.** PUT es alias de PATCH: lo usa la app Android cuando la JVM no admite PATCH.

**Petición.** `PUT http://usuarios:5102/api/v1/usuarios/yo`

```http
Accept: application/json
X-Traza-Id: 66a40d8c-a6da-4949-8056-cd655c35486a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "telefono": "8112345678"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 60 ms · traza `66a40d8c-a6da-4949-8056-cd655c35486a`

```json
{
  "id": 7,
  "nombre": "Ramiro",
  "apellidos": "Alanís Lozano",
  "correo": "repartidor1@codex.mx",
  "telefono": "8112345678",
  "rol": "repartidor",
  "microhub": null,
  "ultimo_acceso": "2026-10-20T00:33:38-06:00"
}
```

**Explicación.** Misma validación y misma auditoría que PATCH; el trigger registra quién cambió el dato.

**Evidencia en PostgreSQL.** `SELECT id, telefono, actualizado_en FROM usuario WHERE id = 7`

```json
[
  {
    "id": 7,
    "telefono": "8112345678",
    "actualizado_en": "2026-10-20 06:33:39.385284+00:00"
  }
]
```
