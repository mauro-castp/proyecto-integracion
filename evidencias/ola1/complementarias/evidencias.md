# Evidencias de petición y respuesta · microservicios v1

Generado el 2026-10-20 01:31 contra los servicios en ejecución. 3 de 3 casos pasan.

## Servicio documentos · puerto 5107

### DOC-11 · Resumen de documentos · PASA

**Objetivo.** Agregación $group por tipo de referencia en MongoDB.

**Petición.** `GET http://documentos:5107/api/v1/documentos/resumen`

```http
Accept: application/json
X-Traza-Id: 5eed78bd-3676-49b7-8f6e-c0f2a06b9f43
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 7 ms · traza `5eed78bd-3676-49b7-8f6e-c0f2a06b9f43`

```json
{
  "total": 3,
  "tamano_total_bytes": 828,
  "por_tipo": [
    {
      "referencia_tipo": "entrega",
      "cantidad": 2,
      "tamano_bytes": 552
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
    "cantidad": 2,
    "tamano_bytes": 552
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
X-Traza-Id: f3f79791-73cb-4f4b-82c0-04511db389ef
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 43 ms · traza `f3f79791-73cb-4f4b-82c0-04511db389ef`

```json
{
  "datos": [
    {
      "id": 2,
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
      "creado_en": "2026-10-19T19:31:46-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 1,
    "paginas": 1
  }
}
```

**Evidencia en PostgreSQL.** `SELECT id, nombre, ubicacion_candidata_id, creado_por FROM escenario_planeacion ORDER BY id DESC LIMIT 3`

```json
[
  {
    "id": 2,
    "nombre": "Escenario complementario",
    "ubicacion_candidata_id": 1,
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
X-Traza-Id: 835b1a4f-b6fc-4f47-b063-d0cdb7b9d903
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "telefono": "8112345678"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 131 ms · traza `835b1a4f-b6fc-4f47-b063-d0cdb7b9d903`

```json
{
  "id": 7,
  "nombre": "Ramiro",
  "apellidos": "Alanís Lozano",
  "correo": "repartidor1@codex.mx",
  "telefono": "8112345678",
  "rol": "repartidor",
  "microhub": null,
  "ultimo_acceso": "2026-10-19T19:31:45-06:00"
}
```

**Explicación.** Misma validación y misma auditoría que PATCH; el trigger registra quién cambió el dato.

**Evidencia en PostgreSQL.** `SELECT id, telefono, actualizado_en FROM usuario WHERE id = 7`

```json
[
  {
    "id": 7,
    "telefono": "8112345678",
    "actualizado_en": "2026-10-20 01:31:46.365137+00:00"
  }
]
```
