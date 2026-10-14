# Evidencias de petición y respuesta · microservicios v1

Generado el 2026-10-14 03:34 contra los servicios en ejecución. 3 de 3 casos pasan.

## Servicio documentos · puerto 5107

### DOC-11 · Resumen de documentos · PASA

**Objetivo.** Agregación $group por tipo de referencia en MongoDB.

**Petición.** `GET http://documentos:5107/api/v1/documentos/resumen`

```http
Accept: application/json
X-Traza-Id: d0acd26b-8a6a-42e5-b868-6e1a826f1d5c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 19 ms · traza `d0acd26b-8a6a-42e5-b868-6e1a826f1d5c`

```json
{
  "total": 6,
  "tamano_total_bytes": 1656,
  "por_tipo": [
    {
      "referencia_tipo": "entrega",
      "cantidad": 5,
      "tamano_bytes": 1380
    },
    {
      "referencia_tipo": "usuario",
      "cantidad": 1,
      "tamano_bytes": 276
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
    "cantidad": 5,
    "tamano_bytes": 1380
  },
  {
    "_id": "usuario",
    "cantidad": 1,
    "tamano_bytes": 276
  }
]
```

## Servicio planeacion · puerto 5106

### PLA-17 · Lista de escenarios guardados · PASA

**Objetivo.** Paginación y búsqueda de escenarios compartidos con el web.

**Petición.** `GET http://planeacion:5106/api/v1/escenarios?pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 42126c55-8536-439a-90af-7ed5d5de5d0b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 43 ms · traza `42126c55-8536-439a-90af-7ed5d5de5d0b`

```json
{
  "datos": [
    {
      "id": 4,
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
      "creado_en": "2026-10-13T21:34:33-06:00"
    },
    {
      "id": 3,
      "nombre": "Escenario de prueba D-1791927087",
      "candidato_id": 20,
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
      "creado_en": "2026-10-13T15:31:28-06:00"
    },
    {
      "id": 2,
      "nombre": "Escenario de prueba D-dfc361b4",
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
      "creado_en": "2026-10-13T15:29:04-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 3,
    "paginas": 1
  }
}
```

**Evidencia en PostgreSQL.** `SELECT id, nombre, ubicacion_candidata_id, creado_por FROM escenario_planeacion ORDER BY id DESC LIMIT 3`

```json
[
  {
    "id": 4,
    "nombre": "Escenario complementario",
    "ubicacion_candidata_id": 1,
    "creado_por": 5
  },
  {
    "id": 3,
    "nombre": "Escenario de prueba D-1791927087",
    "ubicacion_candidata_id": 20,
    "creado_por": 5
  },
  {
    "id": 2,
    "nombre": "Escenario de prueba D-dfc361b4",
    "ubicacion_candidata_id": 18,
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
X-Traza-Id: c4a86d2d-a4a7-4831-a440-7fb4caf4e450
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "telefono": "8112345678"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 685 ms · traza `c4a86d2d-a4a7-4831-a440-7fb4caf4e450`

```json
{
  "id": 7,
  "nombre": "Ramiro",
  "apellidos": "Alanís Lozano",
  "correo": "repartidor1@codex.mx",
  "telefono": "8112345678",
  "rol": "repartidor",
  "microhub": null,
  "ultimo_acceso": "2026-10-13T21:34:33-06:00"
}
```

**Explicación.** Misma validación y misma auditoría que PATCH; el trigger registra quién cambió el dato.

**Evidencia en PostgreSQL.** `SELECT id, telefono, actualizado_en FROM usuario WHERE id = 7`

```json
[
  {
    "id": 7,
    "telefono": "8112345678",
    "actualizado_en": "2026-10-14 03:34:34.205137+00:00"
  }
]
```
