# Evidencias de petición y respuesta · microservicios v1

Generado el 2026-11-26 21:24 contra los servicios en ejecución. 3 de 3 casos pasan.

## Servicio documentos · puerto 5107

### DOC-11 · Resumen de documentos · PASA

**Objetivo.** Agregación $group por tipo de referencia en MongoDB.

**Petición.** `GET http://documentos:5107/api/v1/documentos/resumen`

```http
Accept: application/json
X-Traza-Id: c847a65c-0072-4068-8157-50c6441cc0cd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 13 ms · traza `c847a65c-0072-4068-8157-50c6441cc0cd`

```json
{
  "total": 110,
  "tamano_total_bytes": 30108,
  "por_tipo": [
    {
      "referencia_tipo": "entrega",
      "cantidad": 92,
      "tamano_bytes": 25140
    },
    {
      "referencia_tipo": "pedido",
      "cantidad": 11,
      "tamano_bytes": 3036
    },
    {
      "referencia_tipo": "usuario",
      "cantidad": 7,
      "tamano_bytes": 1932
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
    "cantidad": 92,
    "tamano_bytes": 25140
  },
  {
    "_id": "pedido",
    "cantidad": 11,
    "tamano_bytes": 3036
  },
  {
    "_id": "usuario",
    "cantidad": 14,
    "tamano_bytes": 3162
  }
]
```

## Servicio planeacion · puerto 5106

### PLA-17 · Lista de escenarios guardados · PASA

**Objetivo.** Paginación y búsqueda de escenarios compartidos con el web.

**Petición.** `GET http://planeacion:5106/api/v1/escenarios?pagina=1&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 10511346-701d-49ed-b0af-1980bf938309
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 83 ms · traza `10511346-701d-49ed-b0af-1980bf938309`

```json
{
  "datos": [
    {
      "id": 29,
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
      "creado_en": "2026-11-26T15:24:14-06:00"
    },
    {
      "id": 27,
      "nombre": "Escenario de prueba D-846419a2",
      "candidato_id": 143,
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
      "creado_en": "2026-11-26T15:14:59-06:00"
    },
    {
      "id": 26,
      "nombre": "Escenario de prueba D-dd57bbf9",
      "candidato_id": 141,
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
      "creado_en": "2026-11-26T14:21:23-06:00"
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
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 14,
    "paginas": 3
  }
}
```

**Evidencia en PostgreSQL.** `SELECT id, nombre, ubicacion_candidata_id, creado_por FROM escenario_planeacion ORDER BY id DESC LIMIT 3`

```json
[
  {
    "id": 29,
    "nombre": "Escenario complementario",
    "ubicacion_candidata_id": 1,
    "creado_por": 5
  },
  {
    "id": 27,
    "nombre": "Escenario de prueba D-846419a2",
    "ubicacion_candidata_id": 143,
    "creado_por": 5
  },
  {
    "id": 26,
    "nombre": "Escenario de prueba D-dd57bbf9",
    "ubicacion_candidata_id": 141,
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
X-Traza-Id: 2182eeca-f4e9-42c5-be1a-f30e4f47b940
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "telefono": "8112345678"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 147 ms · traza `2182eeca-f4e9-42c5-be1a-f30e4f47b940`

```json
{
  "id": 7,
  "nombre": "Ramiro",
  "apellidos": "Alanís Lozano",
  "correo": "repartidor1@codex.mx",
  "telefono": "8112345678",
  "rol": "repartidor",
  "microhub": null,
  "ultimo_acceso": "2026-11-26T15:24:14-06:00"
}
```

**Explicación.** Misma validación y misma auditoría que PATCH; el trigger registra quién cambió el dato.

**Evidencia en PostgreSQL.** `SELECT id, telefono, actualizado_en FROM usuario WHERE id = 7`

```json
[
  {
    "id": 7,
    "telefono": "8112345678",
    "actualizado_en": "2026-11-26 15:24:14.994408-06:00"
  }
]
```
