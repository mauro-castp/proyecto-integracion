# Evidencias de petición y respuesta · microservicios v1

Generado el 2026-11-26 20:20 contra los servicios en ejecución. 3 de 3 casos pasan.

## Servicio documentos · puerto 5107

### DOC-11 · Resumen de documentos · PASA

**Objetivo.** Agregación $group por tipo de referencia en MongoDB.

**Petición.** `GET http://documentos:5107/api/v1/documentos/resumen`

```http
Accept: application/json
X-Traza-Id: 69927bd4-8889-48df-9e89-04be8d2dc995
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 10 ms · traza `69927bd4-8889-48df-9e89-04be8d2dc995`

```json
{
  "total": 91,
  "tamano_total_bytes": 25116,
  "por_tipo": [
    {
      "referencia_tipo": "entrega",
      "cantidad": 76,
      "tamano_bytes": 20976
    },
    {
      "referencia_tipo": "pedido",
      "cantidad": 10,
      "tamano_bytes": 2760
    },
    {
      "referencia_tipo": "usuario",
      "cantidad": 5,
      "tamano_bytes": 1380
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
    "cantidad": 76,
    "tamano_bytes": 20976
  },
  {
    "_id": "pedido",
    "cantidad": 10,
    "tamano_bytes": 2760
  },
  {
    "_id": "usuario",
    "cantidad": 10,
    "tamano_bytes": 2292
  }
]
```

## Servicio planeacion · puerto 5106

### PLA-17 · Lista de escenarios guardados · PASA

**Objetivo.** Paginación y búsqueda de escenarios compartidos con el web.

**Petición.** `GET http://planeacion:5106/api/v1/escenarios?pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: af0c383d-5f11-4a38-91bf-ce12f79f9bf6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 44 ms · traza `af0c383d-5f11-4a38-91bf-ce12f79f9bf6`

```json
{
  "datos": [
    {
      "id": 25,
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
      "creado_en": "2026-11-26T14:20:29-06:00"
    },
    {
      "id": 19,
      "nombre": "Escenario de prueba D-a840f4dc",
      "candidato_id": 118,
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
      "creado_en": "2026-11-26T00:39:00-06:00"
    },
    {
      "id": 18,
      "nombre": "Escenario de prueba D-25631556",
      "candidato_id": 116,
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
      "creado_en": "2026-11-26T00:35:22-06:00"
    },
    {
      "id": 17,
      "nombre": "Escenario de prueba D-2e606219",
      "candidato_id": 114,
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
      "creado_en": "2026-11-26T00:31:07-06:00"
    },
    {
      "id": 16,
      "nombre": "Escenario de prueba D-46e6cc93",
      "candidato_id": 112,
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
      "creado_en": "2026-11-25T15:56:58-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 12,
    "paginas": 3
  }
}
```

**Evidencia en PostgreSQL.** `SELECT id, nombre, ubicacion_candidata_id, creado_por FROM escenario_planeacion ORDER BY id DESC LIMIT 3`

```json
[
  {
    "id": 25,
    "nombre": "Escenario complementario",
    "ubicacion_candidata_id": 1,
    "creado_por": 5
  },
  {
    "id": 19,
    "nombre": "Escenario de prueba D-a840f4dc",
    "ubicacion_candidata_id": 118,
    "creado_por": 5
  },
  {
    "id": 18,
    "nombre": "Escenario de prueba D-25631556",
    "ubicacion_candidata_id": 116,
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
X-Traza-Id: 12271de3-cd87-4034-90c7-f735b10e64ad
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "telefono": "8112345678"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 71 ms · traza `12271de3-cd87-4034-90c7-f735b10e64ad`

```json
{
  "id": 7,
  "nombre": "Ramiro",
  "apellidos": "Alanís Lozano",
  "correo": "repartidor1@codex.mx",
  "telefono": "8112345678",
  "rol": "repartidor",
  "microhub": null,
  "ultimo_acceso": "2026-11-26T14:20:28-06:00"
}
```

**Explicación.** Misma validación y misma auditoría que PATCH; el trigger registra quién cambió el dato.

**Evidencia en PostgreSQL.** `SELECT id, telefono, actualizado_en FROM usuario WHERE id = 7`

```json
[
  {
    "id": 7,
    "telefono": "8112345678",
    "actualizado_en": "2026-11-26 14:20:29.411736-06:00"
  }
]
```
