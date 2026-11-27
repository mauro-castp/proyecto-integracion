# Procesos integrales de principio a fin


Generado el 2026-11-27 08:10 contra los servicios en ejecución. 40 de 40 casos pasan.

## Servicio planeacion · puerto 5106

### F1-01 · Escritorio (XML): el planeador registra una ubicación candidata · PASA

**Objetivo.** Planeación de ubicación.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos`

```http
Accept: application/xml
X-Traza-Id: aa9f46e3-2592-4341-be48-07cee420dacb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><candidato_nuevo xmlns="urn:microhubs:v1"><clave>********</clave><nombre>Ubicación del flujo EC3AF</nombre><latitud>25.760195</latitud><longitud>-100.370891</longitud><renta_estimada>15000.00</renta_estimada><nomina_estimada>36000.00</nomina_estimada><servicios_estimados>6000.00</servicios_estimados><otros_costos>4000.00</otros_costos><superficie_m2>100</superficie_m2><capacidad_fisica>120</capacidad_fisica><accesibilidad_vial>8</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km></candidato_nuevo>
```

**Respuesta.** HTTP 201 (esperado 201) · 172 ms · traza `aa9f46e3-2592-4341-be48-07cee420dacb`

```xml
<?xml version='1.0' encoding='utf-8'?>
<candidato xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>335</id><clave>FL-EC3AF</clave><nombre>Ubicación del flujo EC3AF</nombre><latitud>25.760195</latitud><longitud>-100.370891</longitud><renta_estimada>15000.00</renta_estimada><nomina_estimada>36000.00</nomina_estimada><servicios_estimados>6000.00</servicios_estimados><otros_costos>4000.00</otros_costos><costo_fijo>61000.00</costo_fijo><superficie_m2>100</superficie_m2><capacidad_fisica>120</capacidad_fisica><accesibilidad_vial>8</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato>
```

**Evidencia en PostgreSQL.** `SELECT id, clave, nombre, costo_fijo, decision FROM ubicacion_candidata WHERE clave = %s`

```json
[
  {
    "id": 335,
    "clave": "FL-EC3AF",
    "nombre": "Ubicación del flujo EC3AF",
    "costo_fijo": "61000.00",
    "decision": "pendiente"
  }
]
```

### F1-02 · El planeador simula la operación de la candidata · PASA

**Objetivo.** Capacidad, utilización y decisión sugerida (MongoDB).

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/335/simular`

```http
Accept: application/json
X-Traza-Id: 0e301026-bc15-408c-8847-f8f78eb12814
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "supuestos": {
    "demanda_diaria": 100,
    "operadores": 3,
    "repartidores": 4,
    "ticket": 180.0,
    "costo_entrega": 22.0,
    "margen_bruto": 0.3,
    "renta": 15000.0,
    "nomina": 36000.0,
    "servicios": 6000.0,
    "otros": 4000.0,
    "distancia_km": 1.2,
    "capacidad_fisica": 120
  }
}
```

**Respuesta.** HTTP 200 (esperado 200) · 364 ms · traza `0e301026-bc15-408c-8847-f8f78eb12814`

```json
{
  "atendidos": 100.0,
  "rechazados": 0.0,
  "utilizacion": 83.3,
  "nivel": "atencion",
  "tiempo_estimado_min": 17.2,
  "operadores_requeridos": 3,
  "repartidores_requeridos": 2,
  "ingreso_dia": 18000.0,
  "margen_dia": 1166.67,
  "costo_por_pedido": 42.33,
  "equilibrio": {
    "margen_pedido": 32.0,
    "mensual": 1906.2,
    "diario": 63.5
  },
  "decision": "VIABLE",
  "explicacion": [
    "la demanda atendida supera el equilibrio en +36 pedidos/día",
    "la utilización es 83% (atencion)",
    "el espacio físico del local limita la capacidad"
  ]
}
```

## Servicio punto-equilibrio · puerto 5120

### F1-03 · Punto de equilibrio de la candidata · PASA

**Objetivo.** Viabilidad financiera antes de decidir.

**Petición.** `POST http://punto-equilibrio:5120/api/v1/punto-equilibrio/calculos`

```http
Accept: application/json
X-Traza-Id: bee52777-70ae-44d8-90e5-41c9a8da110f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "candidato_id": 335,
  "pedidos_dia": 100,
  "ticket": 180,
  "margen_bruto": 0.3,
  "costos_fijos": 61000,
  "costo_variable_pedido": 22
}
```

**Respuesta.** HTTP 200 (esperado 200) · 73 ms · traza `bee52777-70ae-44d8-90e5-41c9a8da110f`

```json
{
  "id": null,
  "nombre": null,
  "objeto": {
    "tipo": "candidato",
    "id": 335,
    "nombre": null
  },
  "entrada": {
    "costos_fijos_mes": 61000.0,
    "costo_variable_pedido": 22.0,
    "ticket": 180.0,
    "margen_bruto": 0.3,
    "pedidos_dia": 100.0,
    "dias_mes": 30.0,
    "margen_seguridad_minimo_pct": 15.0,
    "origen": {
      "costos_fijos": "manual",
      "costo_variable_pedido": "manual",
      "ticket": "manual",
      "margen_bruto": "manual",
      "pedidos_dia": "manual"
    }
  },
  "margen_pedido": 32.0,
  "equilibrio_mensual": 1906.25,
  "equilibrio_diario": 63.54,
  "ingresos_equilibrio_mes": 343125.0,
  "diferencia_pedidos_dia": 36.46,
  "margen_seguridad_pct": 57.38,
  "utilidad_dia": 1166.67,
  "utilidad_mes": 35000.0,
  "decision": "viable",
  "explicacion": [
    "supera el equilibrio por 57.4 % (mínimo 15 %)"
  ],
  "pasos": [
    "Margen por pedido = ticket × margen bruto − costo de entrega = 180.00 × 30.00% − 22.00 = 32.00",
    "Punto de equilibrio mensual = costos fijos ÷ margen por pedido = 61,000.00 ÷ 32.00 = 1,906 pedidos/mes",
    "Punto de equilibrio diario = 1,906 ÷ 30 días = 63.5 pedidos/día"
  ],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 15.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 30.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 0.28,
      "modificado": false
    }
  ]
}
```

## Servicio planeacion · puerto 5106

### F1-04 · El planeador decide · PASA

**Objetivo.** La decisión queda con motivo y en la bitácora.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/335/decision`

```http
Accept: application/json
X-Traza-Id: 3af14c6a-387b-4f72-aa8c-de687478a8ac
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aceptado",
  "motivo": "Cubre la zona del cliente y la demanda esperada supera el equilibrio."
}
```

**Respuesta.** HTTP 200 (esperado 200) · 87 ms · traza `3af14c6a-387b-4f72-aa8c-de687478a8ac`

```json
{
  "id": 335,
  "clave": "********",
  "nombre": "Ubicación del flujo EC3AF",
  "latitud": 25.760195,
  "longitud": -100.370891,
  "renta_estimada": 15000.0,
  "nomina_estimada": 36000.0,
  "servicios_estimados": 6000.0,
  "otros_costos": 4000.0,
  "costo_fijo": 61000.0,
  "superficie_m2": 100.0,
  "capacidad_fisica": 120,
  "accesibilidad_vial": 8,
  "zona_id": 3,
  "poblacion_cubierta": 5200,
  "radio_km": 1.5,
  "decision": "aceptado",
  "decision_motivo": "Cubre la zona del cliente y la demanda esperada supera el equilibrio."
}
```

**Evidencia en PostgreSQL.** `SELECT decision, decision_motivo FROM ubicacion_candidata WHERE id = %s`

```json
[
  {
    "decision": "aceptado",
    "decision_motivo": "Cubre la zona del cliente y la demanda esperada supera el equilibrio."
  }
]
```

## Servicio microhubs · puerto 5109

### F1-05 · Operación: el administrador abre el microhub · PASA

**Objetivo.** La candidata viable se vuelve microhub activo.

**Petición.** `POST http://microhubs:5109/api/v1/microhubs`

```http
Accept: application/json
X-Traza-Id: 7e05580d-731c-492f-a89d-776aacb05d46
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "clave": "********",
  "nombre": "Microhub EC3AF",
  "direccion": "Ubicación aprobada en planeación",
  "latitud": 25.760195,
  "longitud": -100.370891,
  "radio_km": 1.5,
  "capacidad_turno": 120
}
```

**Respuesta.** HTTP 201 (esperado 201) · 88 ms · traza `7e05580d-731c-492f-a89d-776aacb05d46`

```json
{
  "id": 20,
  "clave": "********",
  "nombre": "Microhub EC3AF",
  "latitud": 25.760195,
  "longitud": -100.370891,
  "radio_km": 1.5,
  "estatus": "activo"
}
```

## Servicio capacidad · puerto 5117

### F1-06 · Asignar personal al microhub · PASA

**Objetivo.** Operadores, repartidores y capacidad física.

**Petición.** `PUT http://capacidad:5117/api/v1/capacidad/recursos/20`

```http
Accept: application/json
X-Traza-Id: 6c9e0a0d-070c-48e9-be65-5b361eceb368
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "operadores": 2,
  "repartidores": 2,
  "capacidad_fisica": 120
}
```

**Respuesta.** HTTP 200 (esperado 200) · 220 ms · traza `6c9e0a0d-070c-48e9-be65-5b361eceb368`

```json
{
  "microhub": {
    "id": 20,
    "nombre": "Microhub EC3AF"
  },
  "operadores": 2,
  "repartidores": 2,
  "capacidad_fisica": 120,
  "actualizado_en": "2026-11-27T02:10:15-06:00"
}
```

## Servicio usuarios · puerto 5102

### F1-07 · Crear la cuenta del operador · PASA

**Objetivo.** Cuenta nueva con su perfil y su microhub.

**Petición.** `POST http://usuarios:5102/api/v1/usuarios`

```http
Accept: application/json
X-Traza-Id: 7911c7c8-04df-40ad-b03c-bc5b88ae6e44
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Operador",
  "apellidos": "EC3AF",
  "correo": "operador.ec3af@ejemplo.mx",
  "clave": "********",
  "rol": "operador",
  "microhub_id": 20
}
```

**Respuesta.** HTTP 201 (esperado 201) · 235 ms · traza `7911c7c8-04df-40ad-b03c-bc5b88ae6e44`

```json
{
  "id": 78,
  "nombre": "Operador",
  "apellidos": "EC3AF",
  "correo": "operador.ec3af@ejemplo.mx",
  "telefono": null,
  "rol": "operador",
  "microhub": {
    "id": 20,
    "clave": "********",
    "nombre": "Microhub EC3AF"
  },
  "ultimo_acceso": null
}
```

## Servicio inventario · puerto 5111

### F1-08a · Surtir el microhub nuevo · PASA

**Objetivo.** Transferencia atómica desde MH-01.

**Petición.** `POST http://inventario:5111/api/v1/inventario/transferencias`

```http
Accept: application/json
X-Traza-Id: 447a5d85-78af-425f-bad7-4777ad41cffd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "origen_microhub_id": 1,
  "destino_microhub_id": 20,
  "producto_id": 31,
  "cantidad": 12,
  "motivo": "Inventario inicial del microhub nuevo",
  "operacion_uuid": "dd8d3420-9797-4266-8f0e-9f2a5645f8e3"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 146 ms · traza `447a5d85-78af-425f-bad7-4777ad41cffd`

```json
{
  "producto_id": 31,
  "cantidad": 12,
  "duplicado": false,
  "origen": {
    "microhub_id": 1,
    "existencia": 291,
    "movimiento_id": 3060
  },
  "destino": {
    "microhub_id": 20,
    "existencia": 12,
    "movimiento_id": 3061
  }
}
```

### F1-08b · Surtir el microhub nuevo · PASA

**Objetivo.** Transferencia atómica desde MH-01.

**Petición.** `POST http://inventario:5111/api/v1/inventario/transferencias`

```http
Accept: application/json
X-Traza-Id: 3464a2d1-10d1-443d-b46c-afb1aef254a9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "origen_microhub_id": 1,
  "destino_microhub_id": 20,
  "producto_id": 18,
  "cantidad": 12,
  "motivo": "Inventario inicial del microhub nuevo",
  "operacion_uuid": "877076a9-276a-4079-aa7e-1b36f29c4cf9"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 163 ms · traza `3464a2d1-10d1-443d-b46c-afb1aef254a9`

```json
{
  "producto_id": 18,
  "cantidad": 12,
  "duplicado": false,
  "origen": {
    "microhub_id": 1,
    "existencia": 50,
    "movimiento_id": 3062
  },
  "destino": {
    "microhub_id": 20,
    "existencia": 12,
    "movimiento_id": 3063
  }
}
```

## Servicio pedidos · puerto 5104

### F1-09 · Android (JSON): el cliente hace su pedido · PASA

**Objetivo.** El motor lo asigna al microhub más cercano que tiene todo: el nuevo.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: 0469fca4-380d-4f58-8eb1-f096b7783e4b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
Content-Type: application/json
```

```json
{
  "lineas": [
    {
      "producto_id": 31,
      "cantidad": 3
    },
    {
      "producto_id": 18,
      "cantidad": 3
    }
  ],
  "operacion_uuid": "6b9f4dd3-a8e1-4b7c-a07e-2f9ec304b738"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 365 ms · traza `0469fca4-380d-4f58-8eb1-f096b7783e4b`

```json
{
  "id": 790,
  "folio": "PED-20261127-000790",
  "estado": "asignado",
  "zona_id": 3,
  "microhub_id": 20,
  "subtotal": 306.0,
  "costo_envio": 0.0,
  "total": 306.0,
  "asignado": true,
  "motivo": null,
  "duplicado": false
}
```

**Evidencia en PostgreSQL.** `SELECT criterio, candidatos_evaluados, microhub_ganador_id, motivo FROM decision_asignacion WHERE pedido_id = %s`

```json
[
  {
    "criterio": "menor_distancia",
    "candidatos_evaluados": 4,
    "microhub_ganador_id": 20,
    "motivo": null
  }
]
```

**Evidencia en PostgreSQL.** `SELECT tipo, producto_id, cantidad, existencia_resultante FROM movimiento_inventario WHERE referencia_tipo = 'pedido' AND referencia_id = %s`

```json
[
  {
    "tipo": "salida_pedido",
    "producto_id": 18,
    "cantidad": -3,
    "existencia_resultante": 9
  },
  {
    "tipo": "salida_pedido",
    "producto_id": 31,
    "cantidad": -3,
    "existencia_resultante": 9
  }
]
```

### F1-10 · El operador prepara el pedido · PASA

**Objetivo.** La transición la valida el motor.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/790/estado`

```http
Accept: application/json
X-Traza-Id: 0729838c-9d28-4a68-9043-d300fa624343
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3OCIs…(296 caracteres)
Content-Type: application/json
```

```json
{
  "estado": "en_preparacion"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 117 ms · traza `0729838c-9d28-4a68-9043-d300fa624343`

```json
{
  "id": 790,
  "folio": "PED-20261127-000790",
  "estado": "en_preparacion",
  "zona": {
    "id": 3,
    "nombre": "Paseo de San Bernabé"
  },
  "microhub_id": 20,
  "total": 306.0,
  "creado_en": "2026-11-27T02:10:16-06:00"
}
```

### F1-11 · El operador lo marca listo · PASA

**Objetivo.** Queda disponible para despacho.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/790/listo`

```http
Accept: application/json
X-Traza-Id: 471a0faa-e5f5-4019-8bd8-c5cb3f59d897
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3OCIs…(296 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 200 (esperado 200) · 73 ms · traza `471a0faa-e5f5-4019-8bd8-c5cb3f59d897`

```json
{
  "id": 790,
  "estado": "en_preparacion",
  "listo_en": "2026-11-27T02:10:17-06:00"
}
```

## Servicio rutas · puerto 5118

### F1-12 · Proponer la ruta de despacho · PASA

**Objetivo.** Agrupa, asigna repartidor y ordena las paradas (algoritmo de rutas).

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/json
X-Traza-Id: 10460ba6-5b0f-4fa1-a187-78a511eed11a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3OCIs…(296 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 20,
  "pedido_ids": [
    790
  ],
  "repartidor_ids": [
    7
  ],
  "metodo": "automatico",
  "guardar": true
}
```

**Respuesta.** HTTP 201 (esperado 201) · 260 ms · traza `10460ba6-5b0f-4fa1-a187-78a511eed11a`

```json
{
  "id": 147,
  "estado": "propuesto",
  "version": 1,
  "microhub": {
    "id": 20,
    "nombre": "Microhub EC3AF"
  },
  "fecha": "2026-11-27",
  "metodo_pedido": "automatico",
  "rutas": [
    {
      "repartidor": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "metodo": "TSP exacto",
      "zonas": [
        "Paseo de San Bernabé"
      ],
      "paradas": [
        {
          "orden": 1,
          "pedido": {
            "id": 790,
            "folio": "PED-20261127-000790"
          },
          "zona": {
            "id": 3,
            "nombre": "Paseo de San Bernabé"
          },
          "latitud": 25.759995,
          "longitud": -100.371091,
          "tramo_km": 0.04,
          "minutos_acum": 4.1
        }
      ],
      "distancia_km": 0.04,
      "minutos": 4.1,
      "costo": 18.18
    }
  ],
  "sin_asignar": [],
  "total": {
    "rutas": 1,
    "paradas": 1,
    "distancia_km": 0.04,
    "minutos_maximo": 4.1,
    "costo": 18.18
  },
  "cambios": [],
  "supuestos_usados": [
    {
      "clave": "********",
      "valor": 22.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 4.5,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 18.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 8.0,
      "modificado": false
    },
    {
      "clave": "********",
      "valor": 1.3,
      "modificado": false
    }
  ]
}
```

## Servicio entregas · puerto 5105

### F1-13 · El operador asigna la entrega · PASA

**Objetivo.** El pedido pasa a ruta y el repartidor recibe el aviso.

**Petición.** `POST http://entregas:5105/api/v1/entregas`

```http
Accept: application/json
X-Traza-Id: dfd943a4-f806-41a3-ab19-e515b839d480
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3OCIs…(296 caracteres)
Content-Type: application/json
```

```json
{
  "pedido_id": 790,
  "repartidor_id": 7,
  "orden_parada": 1
}
```

**Respuesta.** HTTP 201 (esperado 201) · 96 ms · traza `dfd943a4-f806-41a3-ab19-e515b839d480`

```json
{
  "entrega_id": 457,
  "pedido_id": 790,
  "repartidor_id": 7,
  "estado_pedido": "en_ruta"
}
```

**Evidencia en PostgreSQL.** `SELECT titulo, tipo, referencia_id FROM web_notificacion WHERE destinatario_id = %s ORDER BY id DESC LIMIT 1`

```json
[
  {
    "titulo": "Nueva entrega asignada",
    "tipo": "entrega",
    "referencia_id": "457"
  }
]
```

### F1-14 · Android: el repartidor ve su parada · PASA

**Objetivo.** Sesión validada en Redis.

**Petición.** `GET http://entregas:5105/api/v1/entregas/mias?por_pagina=50`

```http
Accept: application/json
X-Traza-Id: 5dbcfd2a-f111-41db-906d-7f069ac44a07
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 56 ms · traza `5dbcfd2a-f111-41db-906d-7f069ac44a07`

```json
{
  "datos": [
    {
      "id": 439,
      "pedido_id": 731,
      "folio": "PED-20261127-000731",
      "estado_pedido": "en_ruta",
      "orden_parada": 1,
      "direccion": "Cerro Prieto 4059, Valles de San Bernabé",
      "zona": "Valles de San Bernabé",
      "distancia_km": 0.63,
      "minutos_estimados": 5.7,
      "total": 180.0
    },
    {
      "id": 457,
      "pedido_id": 790,
      "folio": "PED-20261127-000790",
      "estado_pedido": "en_ruta",
      "orden_parada": 1,
      "direccion": "Nogal 1440, Paseo de San Bernabé",
      "zona": "Paseo de San Bernabé",
      "distancia_km": null,
      "minutos_estimados": null,
      "total": 306.0
    },
    {
      "id": 440,
      "pedido_id": 748,
      "folio": "PED-20261127-000748",
      "estado_pedido": "en_ruta",
      "orden_parada": 2,
      "direccion": "Cerro Prieto 4059, Valles de San Bernabé",
      "zona": "Valles de San Bernabé",
      "distancia_km": 0.0,
      "minutos_estimados": 9.7,
      "total": 261.0
    },
    {
      "id": 441,
      "pedido_id": 732,
      "folio": "PED-20261127-000732",
      "estado_pedido": "en_ruta",
      "orden_parada": 3,
      "direccion": "Emiliano Zapata 4397, Valles de San Bernabé",
      "zona": "Valles de San Bernabé",
      "distancia_km": 0.29,
      "minutos_estimados": 14.5,
      "total": 167.0
    },
    {
      "id": 414,
      "pedido_id": 740,
      "folio": "PED-20261127-000740",
      "estado_pedido": "en_ruta",
      "orden_parada": 4,
      "direccion": "Emiliano Zapata 4706, Paseo de San Bernabé",
      "zona": "Paseo de San Bernabé",
      "distancia_km": 1.04,
      "minutos_estimados": 28.0,
      "total": 148.0
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 50,
    "total": 5,
    "paginas": 1
  }
}
```

**Evidencia en Redis.** `SCARD auth:sesion:7`

```json
[
  {
    "comando": "SCARD auth:sesion:7",
    "valor": 20
  }
]
```

## Servicio seguimiento · puerto 5110

### F1-15 · El repartidor envía su recorrido · PASA

**Objetivo.** Puntos GPS en MongoDB (2dsphere).

**Petición.** `POST http://seguimiento:5110/api/v1/seguimiento/457/ubicaciones`

```http
Accept: application/json
X-Traza-Id: 78b99b92-4d51-49f1-a8b8-0b2a68b07156
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "puntos": [
    {
      "latitud": 25.760195,
      "longitud": -100.370891,
      "capturado_en": "2026-11-27T08:06:17.788249+00:00"
    },
    {
      "latitud": 25.759995,
      "longitud": -100.371091,
      "capturado_en": "2026-11-27T08:09:17.788276+00:00"
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 42 ms · traza `78b99b92-4d51-49f1-a8b8-0b2a68b07156`

```json
{
  "recibidos": 2
}
```

## Servicio documentos · puerto 5107

### F1-16 · La foto de evidencia queda en el almacén · PASA

**Objetivo.** En la base solo sus datos; se descarga con un enlace firmado.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b093ae9f68f301419471806/enlace`

```http
Accept: application/json
X-Traza-Id: edd4f218-1515-4322-b880-9bd849f5cf9b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 34 ms · traza `edd4f218-1515-4322-b880-9bd849f5cf9b`

```json
{
  "id": "6b093ae9f68f301419471806",
  "nombre": "evidencia-flujo1-EC3AF.jpg",
  "url_firmada": "http://documentos:5107/api/v1/documentos/descarga?k=document…(208 caracteres)",
  "metodo": "GET",
  "segundos": 300,
  "expira_en": "2026-11-27T02:15:17-06:00"
}
```

**Evidencia en MongoDB.** `db.documentos.findOne({_id}) sin contenido`

```json
{
  "_id": "6b093ae9f68f301419471806",
  "nombre": "evidencia-flujo1-EC3AF.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "457"
  },
  "subido_por": 7,
  "creado_en": "2026-11-27 08:10:17.860000+00:00",
  "ruta": "documentos/2026/11/6b093ae9f68f301419471806.jpg",
  "privacidad": "privado",
  "estado": "activo",
  "metadatos": {
    "almacen": "local",
    "origen": "api"
  }
}
```

## Servicio entregas · puerto 5105

### F1-17 · El repartidor cierra la entrega · PASA

**Objetivo.** Cobro, ubicación y evidencia; idempotente.

**Petición.** `POST http://entregas:5105/api/v1/entregas/457/resultado`

```http
Accept: application/json
X-Traza-Id: 3014a74e-682a-4b96-b090-c0988ee76f0c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 306.0,
  "cambio_entregado": 0,
  "ubicacion": {
    "latitud": 25.759995,
    "longitud": -100.371091
  },
  "evidencia_ids": [
    "6b093ae9f68f301419471806"
  ],
  "capturado_en": "2026-11-27T08:10:18.248638+00:00",
  "id_cliente_local": "ba55095e-50c1-486a-b0f2-34f8b161e09c"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 134 ms · traza `3014a74e-682a-4b96-b090-c0988ee76f0c`

```json
{
  "entrega_id": 457,
  "pedido_id": 790,
  "estado_pedido": "entregado",
  "cerrado_en": "2026-11-27T02:10:18-06:00",
  "duplicado": false
}
```

**Evidencia en PostgreSQL.** `SELECT estado_anterior, estado_nuevo, usuario_id, proceso FROM historial_estatus WHERE pedido_id = %s ORDER BY id`

```json
[
  {
    "estado_anterior": null,
    "estado_nuevo": "creado",
    "usuario_id": 9,
    "proceso": null
  },
  {
    "estado_anterior": "creado",
    "estado_nuevo": "asignado",
    "usuario_id": 9,
    "proceso": null
  },
  {
    "estado_anterior": "asignado",
    "estado_nuevo": "en_preparacion",
    "usuario_id": 78,
    "proceso": null
  },
  {
    "estado_anterior": "en_preparacion",
    "estado_nuevo": "en_ruta",
    "usuario_id": 78,
    "proceso": null
  },
  {
    "estado_anterior": "en_ruta",
    "estado_nuevo": "entregado",
    "usuario_id": 7,
    "proceso": null
  }
]
```

## Servicio notificaciones · puerto 5124

### F1-18 · El cliente recibe el aviso del cierre · PASA

**Objetivo.** Aviso generado por el motor.

**Petición.** `GET http://notificaciones:5124/api/v1/notificaciones?por_pagina=5`

```http
Accept: application/json
X-Traza-Id: b3e3ff28-6491-4279-b72d-2446f5961f03
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 70 ms · traza `b3e3ff28-6491-4279-b72d-2446f5961f03`

```json
{
  "datos": [
    {
      "id": 1352,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000790",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "790"
      },
      "creada_en": "2026-11-27T02:10:18-06:00"
    },
    {
      "id": 1322,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000772",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "772"
      },
      "creada_en": "2026-11-27T02:06:41-06:00"
    },
    {
      "id": 1321,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000770",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "770"
      },
      "creada_en": "2026-11-27T02:06:39-06:00"
    },
    {
      "id": 1275,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000766",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "766"
      },
      "creada_en": "2026-11-27T01:25:21-06:00"
    },
    {
      "id": 1246,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000762",
      "mensaje": "El pedido cambió a entrega_fallida.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "762"
      },
      "creada_en": "2026-11-27T01:24:18-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 43,
    "paginas": 9
  }
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F1-19 · El auditor reconstruye la historia del pedido · PASA

**Objetivo.** Bitácora, estados, inventario y archivos en una línea de tiempo.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/pedido/790`

```http
Accept: application/json
X-Traza-Id: ac14872b-6ddb-4a9a-871b-1db0ccc7c79a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 150 ms · traza `ac14872b-6ddb-4a9a-871b-1db0ccc7c79a`

```json
{
  "objeto": {
    "tipo": "pedido",
    "id": "790"
  },
  "total": 15,
  "eventos": [
    {
      "fecha": "2026-11-27T02:10:16-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "actualizado_en = 2026-11-27T02:10:16.93061-06:00; asignado_en = None; cerrado_en = None; cliente_id = 1",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "790"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": null,
          "nuevo": "2026-11-27T02:10:16.93061-06:00"
        },
        {
          "campo": "asignado_en",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "cerrado_en",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "cliente_id",
          "anterior": null,
          "nuevo": "1"
        },
        {
          "campo": "costo_envio",
          "anterior": null,
          "nuevo": "0.0"
        },
        {
          "campo": "creado_en",
          "anterior": null,
          "nuevo": "2026-11-27T02:10:16.93061-06:00"
        },
        {
          "campo": "domicilio_id",
          "anterior": null,
          "nuevo": "1"
        },
        {
          "campo": "estado",
          "anterior": null,
          "nuevo": "creado"
        },
        {
          "campo": "folio",
          "anterior": null,
          "nuevo": "PED-20261127-000790"
        },
        {
          "campo": "id",
          "anterior": null,
          "nuevo": "790"
        },
        {
          "campo": "listo_en",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "microhub_id",
          "anterior": null,
          "nuevo": null
        }
      ]
    },
    {
      "fecha": "2026-11-27T02:10:16-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "asignado_en = 2026-11-27T02:10:16.93061-06:00; estado: creado → asignado; microhub_id = 20",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "790"
      },
      "cambios": [
        {
          "campo": "asignado_en",
          "anterior": null,
          "nuevo": "2026-11-27T02:10:16.93061-06:00"
        },
        {
          "campo": "estado",
          "anterior": "creado",
          "nuevo": "asignado"
        },
        {
          "campo": "microhub_id",
          "anterior": null,
          "nuevo": "20"
        }
      ]
    },
    {
      "fecha": "2026-11-27T02:10:16-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "nuevo → creado",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "790"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T02:10:16-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "creado → asignado",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "790"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T02:10:16-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -3 de producto 18 en microhub 20 (existencia 9)",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "20-18"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T02:10:16-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -3 de producto 31 en microhub 20 (existencia 9)",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "20-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T02:10:17-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-27T02:10:16.93061-06:00 → 2026-11-27T02:10:17.177745-06:00; estado: asignado → en_preparacion",
      "usuario": {
        "id": 78,
        "nombre": "Operador EC3AF"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "790"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-27T02:10:16.93061-06:00",
          "nuevo": "2026-11-27T02:10:17.177745-06:00"
        },
        {
          "campo": "estado",
          "anterior": "asignado",
          "nuevo": "en_preparacion"
        }
      ]
    },
    {
      "fecha": "2026-11-27T02:10:17-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "asignado → en_preparacion",
      "usuario": {
        "id": 78,
        "nombre": "Operador EC3AF"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "790"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T02:10:17-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "listo_en = 2026-11-27T02:10:17.297127-06:00",
      "usuario": {
        "id": 78,
        "nombre": "Operador EC3AF"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "790"
      },
      "cambios": [
        {
          "campo": "listo_en",
          "anterior": null,
          "nuevo": "2026-11-27T02:10:17.297127-06:00"
        }
      ]
    },
    {
      "fecha": "2026-11-27T02:10:17-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "asignada_en = 2026-11-27T02:10:17.627116-06:00; cambio_entregado = None; capturado_en = None; cerrada_por_usuario_id = None",
      "usuario": {
        "id": 78,
        "nombre": "Operador EC3AF"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "457"
      },
      "cambios": [
        {
          "campo": "asignada_en",
          "anterior": null,
          "nuevo": "2026-11-27T02:10:17.627116-06:00"
        },
        {
          "campo": "cambio_entregado",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "capturado_en",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "cerrada_por_usuario_id",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "cierre_en",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "cierre_latitud",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "cierre_longitud",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "cierre_precision_m",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "confirmacion_recepcion",
          "anterior": null,
          "nuevo": "false"
        },
        {
          "campo": "costo_entrega_estimado",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "distancia_km",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "evidencia_ids",
          "anterior": null,
          "nuevo": null
        }
      ]
    },
    {
      "fecha": "2026-11-27T02:10:17-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-27T02:10:17.177745-06:00 → 2026-11-27T02:10:17.627116-06:00; estado: en_preparacion → en_ruta",
      "usuario": {
        "id": 78,
        "nombre": "Operador EC3AF"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "790"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-27T02:10:17.177745-06:00",
          "nuevo": "2026-11-27T02:10:17.627116-06:00"
        },
        {
          "campo": "estado",
          "anterior": "en_preparacion",
          "nuevo": "en_ruta"
        }
      ]
    },
    {
      "fecha": "2026-11-27T02:10:17-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "en_preparacion → en_ruta",
      "usuario": {
        "id": 78,
        "nombre": "Operador EC3AF"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "790"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T02:10:18-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "cambio_entregado = 0.0; capturado_en = 2026-11-27T02:10:18.2…(143 caracteres)",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "457"
      },
      "cambios": [
        {
          "campo": "cambio_entregado",
          "anterior": null,
          "nuevo": "0.0"
        },
        {
          "campo": "capturado_en",
          "anterior": null,
          "nuevo": "2026-11-27T02:10:18.248638-06:00"
        },
        {
          "campo": "cerrada_por_usuario_id",
          "anterior": null,
          "nuevo": "7"
        },
        {
          "campo": "cierre_en",
          "anterior": null,
          "nuevo": "2026-11-27T02:10:18.3021-06:00"
        },
        {
          "campo": "cierre_latitud",
          "anterior": null,
          "nuevo": "25.759995"
        },
        {
          "campo": "cierre_longitud",
          "anterior": null,
          "nuevo": "-100.371091"
        },
        {
          "campo": "confirmacion_recepcion",
          "anterior": "false",
          "nuevo": "true"
        },
        {
          "campo": "evidencia_ids",
          "anterior": null,
          "nuevo": "[\"6b093ae9f68f301419471806\"]"
        },
        {
          "campo": "evidencia_url",
          "anterior": null,
          "nuevo": "/api/v1/documentos/6b093ae9f68f301419471806"
        },
        {
          "campo": "id_cliente_local",
          "anterior": null,
          "nuevo": "ba55095e-50c1-486a-b0f2-34f8b161e09c"
        },
        {
          "campo": "monto_cobrado",
          "anterior": null,
          "nuevo": "306.0"
        },
        {
          "campo": "resultado",
          "anterior": null,
          "nuevo": "entregado"
        }
      ]
    },
    {
      "fecha": "2026-11-27T02:10:18-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-27T02:10:17.627116-06:00 → 2026-11-2…(155 caracteres)",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "790"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-27T02:10:17.627116-06:00",
          "nuevo": "2026-11-27T02:10:18.3021-06:00"
        },
        {
          "campo": "cerrado_en",
          "anterior": null,
          "nuevo": "2026-11-27T02:10:18.3021-06:00"
        },
        {
          "campo": "estado",
          "anterior": "en_ruta",
          "nuevo": "entregado"
        }
      ]
    },
    {
      "fecha": "2026-11-27T02:10:18-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "en_ruta → entregado",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "790"
      },
      "cambios": []
    }
  ]
}
```

## Servicio reportes · puerto 5123

### F1-20 · Visualización: el microhub nuevo ya aparece en la comparación · PASA

**Objetivo.** Datos listos para Highcharts.

**Petición.** `GET http://reportes:5123/api/v1/reportes/comparacion_microhubs/grafica?microhub_id=20`

```http
Accept: application/json
X-Traza-Id: ea607dda-d0a2-4f47-b94f-4788dd2e18cc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 153 ms · traza `ea607dda-d0a2-4f47-b94f-4788dd2e18cc`

```json
{
  "reporte": "comparacion_microhubs",
  "titulo": "Comparación entre microhubs",
  "tipo": "column",
  "unidad": "pedidos / MXN",
  "categorias": [
    "Microhub EC3AF"
  ],
  "series": [
    {
      "nombre": "Pedidos",
      "datos": [
        1.0
      ]
    },
    {
      "nombre": "Venta",
      "datos": [
        306.0
      ]
    }
  ]
}
```

## Servicio microhubs · puerto 5109

### F1-21 · Cierre: dar de baja el microhub de la demostración · PASA

**Objetivo.** Baja lógica; conserva su historia.

**Petición.** `DELETE http://microhubs:5109/api/v1/microhubs/20`

```http
Accept: application/json
X-Traza-Id: be2cb53e-4d19-4973-9dff-670da0f98410
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 54 ms · traza `be2cb53e-4d19-4973-9dff-670da0f98410`

```json
(sin cuerpo)
```

## Servicio pedidos · puerto 5104

### F2-01 · Android: un cliente compra y el inventario baja · PASA

**Objetivo.** El motor descuenta inventario en la misma transacción.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: d522ff9e-55a5-4cfc-96e5-8755a122300c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
Content-Type: application/json
```

```json
{
  "lineas": [
    {
      "producto_id": 31,
      "cantidad": 10
    }
  ],
  "operacion_uuid": "7c870c76-c26b-44ca-8b3b-51cabcdab890"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 272 ms · traza `d522ff9e-55a5-4cfc-96e5-8755a122300c`

```json
{
  "id": 791,
  "folio": "PED-20261127-000791",
  "estado": "asignado",
  "zona_id": 3,
  "microhub_id": 2,
  "subtotal": 580.0,
  "costo_envio": 0.0,
  "total": 580.0,
  "asignado": true,
  "motivo": null,
  "duplicado": false
}
```

**Evidencia en PostgreSQL.** `SELECT microhub_id, producto_id, cantidad, existencia_resultante FROM movimiento_inventario WHERE referencia_tipo = 'pedido' AND referencia_id = %s`

```json
[
  {
    "microhub_id": 2,
    "producto_id": 31,
    "cantidad": -10,
    "existencia_resultante": 30
  }
]
```

## Servicio inventario · puerto 5111

### F2-02 · El operador fija el mínimo y nace la alerta · PASA

**Objetivo.** El trigger avisa del faltante.

**Petición.** `PATCH http://inventario:5111/api/v1/inventario/1/31/minimo`

```http
Accept: application/json
X-Traza-Id: 96478ee2-67e4-4e6d-b13b-544b6e6eb34a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "minimo": 301
}
```

**Respuesta.** HTTP 200 (esperado 200) · 192 ms · traza `96478ee2-67e4-4e6d-b13b-544b6e6eb34a`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "producto": {
    "id": 31,
    "clave_interna": "LA-003",
    "nombre": "Queso fresco"
  },
  "existencia": 291,
  "minimo": 301,
  "reservado": 0,
  "disponible": 291,
  "estado": "bajo_minimo",
  "actualizado_en": "2026-11-27T02:10:20-06:00"
}
```

### F2-03 · La alerta de faltante · PASA

**Objetivo.** Qué producto, cuánto falta y qué tan grave es.

**Petición.** `GET http://inventario:5111/api/v1/inventario/alertas?microhub_id=1&por_pagina=100`

```http
Accept: application/json
X-Traza-Id: 5c43e215-ffce-4959-b814-1a0063dc9cf1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 113 ms · traza `5c43e215-ffce-4959-b814-1a0063dc9cf1`

```json
{
  "datos": [
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 31,
        "clave_interna": "LA-003",
        "nombre": "Queso fresco"
      },
      "existencia": 291,
      "minimo": 301,
      "disponible": 291,
      "faltante": 10,
      "severidad": "baja"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 40,
        "clave_interna": "LI-004",
        "nombre": "Limpiador multiusos"
      },
      "existencia": 8,
      "minimo": 8,
      "disponible": 8,
      "faltante": 0,
      "severidad": "baja"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 100,
    "total": 2,
    "paginas": 1
  }
}
```

## Servicio abastecimiento · puerto 5114

### F2-04 · El operador pide reposición · PASA

**Objetivo.** Solicitud con sus líneas.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes`

```http
Accept: application/json
X-Traza-Id: de64a740-0d97-4799-bd7c-c5e2e95ce14e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "motivo": "Faltante detectado por el sistema",
  "lineas": [
    {
      "producto_id": 31,
      "cantidad": 100
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 107 ms · traza `de64a740-0d97-4799-bd7c-c5e2e95ce14e`

```json
{
  "id": 101,
  "folio": "SC-20261127-000101",
  "microhub_id": 1,
  "estado": "pendiente",
  "motivo": "Faltante detectado por el sistema",
  "solicitada_por": 2,
  "decidida_por": null,
  "decision_motivo": null,
  "decidida_en": null,
  "creada_en": "2026-11-27T02:10:20-06:00",
  "lineas": [
    {
      "producto": {
        "id": 31,
        "nombre": "Queso fresco"
      },
      "cantidad": 100
    }
  ]
}
```

### F2-05 · El administrador aprueba · PASA

**Objetivo.** Quien pidió recibe el aviso.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/101/decision`

```http
Accept: application/json
X-Traza-Id: 48d04161-7a0e-4e5a-87cf-540927d5330b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aprobada",
  "motivo": "Con presupuesto"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 99 ms · traza `48d04161-7a0e-4e5a-87cf-540927d5330b`

```json
{
  "id": 101,
  "folio": "SC-20261127-000101",
  "microhub_id": 1,
  "estado": "aprobada",
  "motivo": "Faltante detectado por el sistema",
  "solicitada_por": 2,
  "decidida_por": 1,
  "decision_motivo": "Con presupuesto",
  "decidida_en": "2026-11-27T02:10:20-06:00",
  "creada_en": "2026-11-27T02:10:20-06:00",
  "lineas": [
    {
      "producto": {
        "id": 31,
        "nombre": "Queso fresco"
      },
      "cantidad": 100
    }
  ]
}
```

### F2-06 · Se emite la orden de compra · PASA

**Objetivo.** Al proveedor con la mejor oferta.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/101/ordenar`

```http
Accept: application/json
X-Traza-Id: 383c88fd-39e0-4403-9f7a-202e3255bd79
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 201 (esperado 201) · 347 ms · traza `383c88fd-39e0-4403-9f7a-202e3255bd79`

```json
{
  "solicitud_id": 101,
  "ordenes": [
    {
      "id": 64,
      "folio": "OC-20261127-000064",
      "solicitud_id": 101,
      "proveedor": {
        "id": 1,
        "nombre": "Abarrotes del Norte"
      },
      "microhub_id": 1,
      "estado": "emitida",
      "fecha_esperada": "2026-11-29",
      "total": 4060.0,
      "creada_en": "2026-11-27T02:10:21-06:00",
      "cerrada_en": null,
      "lineas": [
        {
          "producto": {
            "id": 31,
            "nombre": "Queso fresco"
          },
          "cantidad": 100,
          "precio_compra": 40.6,
          "cantidad_recibida": 0,
          "pendiente_inventario": 0
        }
      ]
    }
  ]
}
```

### F2-07 · Llega la mercancía y se recibe · PASA

**Objetivo.** Sube el inventario una sola vez (idempotente).

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/64/recepcion`

```http
Accept: application/json
X-Traza-Id: ec6587c3-73c9-4949-927b-3f7f9d41968a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "operacion_uuid": "59a88f86-f86a-4314-8186-ca512bd4edc6",
  "nota": "Completo",
  "lineas": [
    {
      "producto_id": 31,
      "cantidad": 100
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 394 ms · traza `ec6587c3-73c9-4949-927b-3f7f9d41968a`

```json
{
  "orden": {
    "id": 64,
    "folio": "OC-20261127-000064",
    "solicitud_id": 101,
    "proveedor": {
      "id": 1,
      "nombre": "Abarrotes del Norte"
    },
    "microhub_id": 1,
    "estado": "recibida",
    "fecha_esperada": "2026-11-29",
    "total": 4060.0,
    "creada_en": "2026-11-27T02:10:21-06:00",
    "cerrada_en": "2026-11-27T02:10:21-06:00",
    "lineas": [
      {
        "producto": {
          "id": 31,
          "nombre": "Queso fresco"
        },
        "cantidad": 100,
        "precio_compra": 40.6,
        "cantidad_recibida": 100,
        "pendiente_inventario": 0
      }
    ]
  },
  "aplicadas": 1,
  "pendientes": 0,
  "aviso": null
}
```

**Evidencia en PostgreSQL.** `SELECT existencia, minimo FROM inventario WHERE microhub_id = %s AND producto_id = %s`

```json
[
  {
    "existencia": 391,
    "minimo": 301
  }
]
```

## Servicio documentos · puerto 5107

### F2-08 · La remisión firmada queda en el almacén · PASA

**Objetivo.** Archivo con enlace firmado.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b093aedf68f30141947180b/enlace`

```http
Accept: application/json
X-Traza-Id: 3fc2eee6-5791-47ec-bcad-d002f335404a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 35 ms · traza `3fc2eee6-5791-47ec-bcad-d002f335404a`

```json
{
  "id": "6b093aedf68f30141947180b",
  "nombre": "remision-64.jpg",
  "url_firmada": "http://documentos:5107/api/v1/documentos/descarga?k=document…(197 caracteres)",
  "metodo": "GET",
  "segundos": 300,
  "expira_en": "2026-11-27T02:15:21-06:00"
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F2-09 · Trazabilidad del producto en el microhub · PASA

**Objetivo.** Salida por pedido y recepción por orden.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/inventario?microhub_id=1&producto_id=31`

```http
Accept: application/json
X-Traza-Id: ef5c8940-c146-49b4-b6dc-e219262e39af
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 75 ms · traza `ef5c8940-c146-49b4-b6dc-e219262e39af`

```json
{
  "objeto": {
    "tipo": "inventario",
    "id": "1-31"
  },
  "total": 21,
  "eventos": [
    {
      "fecha": "2026-10-19T19:30:40-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "recepcion: +57 de producto 31 en microhub 1 (existencia 57). Carga inicial de semilla",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-10-19T19:30:41-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "devolucion_cancelacion: +1 de producto 31 en microhub 1 (existencia 57). Cancelación del cliente (RN18).",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-10-19T19:30:41-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -1 de producto 31 en microhub 1 (existencia 56)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-10-20T00:28:51-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -2 de producto 31 en microhub 1 (existencia 55)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-10-20T00:31:43-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "devolucion_cancelacion: +2 de producto 31 en microhub 1 (existencia 57). Reposición del inventario de una prueba",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T00:33:03-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -2 de producto 31 en microhub 1 (existencia 55)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T15:21:16-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "transferencia_salida: -12 de producto 31 en microhub 1 (existencia 43). Inventario inicial del microhub nuevo",
      "usuario": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "1-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T15:21:58-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "transferencia_salida: -12 de producto 31 en microhub 1 (existencia 31). Inventario inicial del microhub nuevo",
      "usuario": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "1-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T15:22:04-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "recepcion: +100 de producto 31 en microhub 1 (existencia 131). Recepción de la orden OC-20261126-000038: Completo",
      "usuario": {
        "id": 2,
        "nombre": "Ruth Elizabeth Soriano"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "1-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T21:45:24-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -2 de producto 31 en microhub 1 (existencia 129)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T23:11:41-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "transferencia_salida: -12 de producto 31 en microhub 1 (existencia 117). Inventario inicial del microhub nuevo",
      "usuario": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "1-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T23:11:46-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "recepcion: +100 de producto 31 en microhub 1 (existencia 217). Recepción de la orden OC-20261126-000044: Completo",
      "usuario": {
        "id": 2,
        "nombre": "Ruth Elizabeth Soriano"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "1-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T00:14:44-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -2 de producto 31 en microhub 1 (existencia 215)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T00:17:15-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -2 de producto 31 en microhub 1 (existencia 213)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T01:24:09-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "transferencia_salida: -12 de producto 31 en microhub 1 (existencia 201). Inventario inicial del microhub nuevo",
      "usuario": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "1-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T01:24:14-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "recepcion: +100 de producto 31 en microhub 1 (existencia 301). Recepción de la orden OC-20261127-000057: Completo",
      "usuario": {
        "id": 2,
        "nombre": "Ruth Elizabeth Soriano"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "1-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T01:25:19-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "devolucion_cancelacion: +2 de producto 31 en microhub 1 (existencia 303). Entrega fallida: la mercancía regresa al microhub.",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "1-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T02:07:42-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -1 de producto 31 en microhub 1 (existencia 302)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T02:07:48-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "devolucion_cancelacion: +1 de producto 31 en microhub 1 (existencia 303). Pedido de prueba cancelado",
      "usuario": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "1-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T02:10:15-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "transferencia_salida: -12 de producto 31 en microhub 1 (existencia 291). Inventario inicial del microhub nuevo",
      "usuario": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "1-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T02:10:21-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "recepcion: +100 de producto 31 en microhub 1 (existencia 391). Recepción de la orden OC-20261127-000064: Completo",
      "usuario": {
        "id": 2,
        "nombre": "Ruth Elizabeth Soriano"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "1-31"
      },
      "cambios": []
    }
  ]
}
```

## Servicio reportes · puerto 5123

### F2-10 · Reporte de alertas en CSV · PASA

**Objetivo.** Visualización y archivo descargable con huella.

**Petición.** `GET http://reportes:5123/api/v1/reportes/inventario_alertas/exportar?formato=csv&microhub_id=1`

```http
Accept: application/json
X-Traza-Id: 10aaec60-a5a6-4cc6-b548-c90cd061b91b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 232 ms · traza `10aaec60-a5a6-4cc6-b548-c90cd061b91b`

```json
﻿Microhub,Producto,Existencia,Mínimo,Disponible,Faltante,Severidad
Microhub San Bernabé Centro,Limpiador multiusos,8,8,8,0,baja
Total,,,,,0,

```

## Servicio pedidos · puerto 5104

### F3-01 · El cliente hace un pedido · PASA

**Objetivo.** Punto de partida del recorrido.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: 73f87e5a-6c8a-4784-83e6-ed873cc6e093
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
Content-Type: application/json
```

```json
{
  "lineas": [
    {
      "producto_id": 32,
      "cantidad": 3
    },
    {
      "producto_id": 51,
      "cantidad": 3
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 249 ms · traza `73f87e5a-6c8a-4784-83e6-ed873cc6e093`

```json
{
  "id": 792,
  "folio": "PED-20261127-000792",
  "estado": "asignado",
  "zona_id": 3,
  "microhub_id": 2,
  "subtotal": 420.0,
  "costo_envio": 0.0,
  "total": 420.0,
  "asignado": true,
  "motivo": null,
  "duplicado": false
}
```

## Servicio entregas · puerto 5105

### F3-02 · El operador asigna la entrega · PASA

**Objetivo.** El repartidor la descarga antes de salir.

**Petición.** `POST http://entregas:5105/api/v1/entregas`

```http
Accept: application/json
X-Traza-Id: 30f4ae4a-6f82-4dcf-95bf-ad7baed4915b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
Content-Type: application/json
```

```json
{
  "pedido_id": 792,
  "repartidor_id": 7
}
```

**Respuesta.** HTTP 201 (esperado 201) · 65 ms · traza `30f4ae4a-6f82-4dcf-95bf-ad7baed4915b`

```json
{
  "entrega_id": 458,
  "pedido_id": 792,
  "repartidor_id": 7,
  "estado_pedido": "en_ruta"
}
```

## Servicio sincronizacion · puerto 5125

### F3-03 · Android recupera la red y manda lo hecho sin conexión · PASA

**Objetivo.** Se aplica en el orden en que ocurrió.

**Petición.** `POST http://sincronizacion:5125/api/v1/sincronizacion/lotes`

```http
Accept: application/json
X-Traza-Id: 3104f310-03e9-495b-9abd-cab09c7b007b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "63045dcf-e44b-4305-a244-8447d6e56f3f",
  "dispositivo": "android-flujo-b2b325",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "de7d64ff-6d99-4c6a-ba93-1af819c7b0b2",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-27T07:50:24.653491+00:00",
      "datos": {
        "entrega_id": 458,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-27T07:50:24.653565+00:00"
          },
          {
            "latitud": 25.7491,
            "longitud": -100.3611,
            "capturado_en": "2026-11-27T07:55:24.653575+00:00"
          }
        ]
      }
    },
    {
      "operacion_uuid": "fccb30b4-74a5-4746-9b77-1c1f42d653fb",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-27T07:58:24.653596+00:00",
      "datos": {
        "entrega_id": 458,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "El cliente no estaba en su domicilio",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b093af0f68f301419471810"
        ],
        "capturado_en": "2026-11-27T07:58:24.653602+00:00"
      }
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 496 ms · traza `3104f310-03e9-495b-9abd-cab09c7b007b`

```json
{
  "id": 264,
  "lote_uuid": "63045dcf-e44b-4305-a244-8447d6e56f3f",
  "dispositivo": "android-flujo-b2b325",
  "recibido_en": "2026-11-27T02:10:24-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 0,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "de7d64ff-6d99-4c6a-ba93-1af819c7b0b2",
      "tipo": "ubicaciones",
      "estado": "aplicada",
      "duplicada": false,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    },
    {
      "operacion_uuid": "fccb30b4-74a5-4746-9b77-1c1f42d653fb",
      "tipo": "entrega_resultado",
      "estado": "aplicada",
      "duplicada": false,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    }
  ]
}
```

**Evidencia en PostgreSQL.** `SELECT tipo, estado, intentos, creada_en FROM sync_operacion WHERE dispositivo = %s ORDER BY creada_en`

```json
[
  {
    "tipo": "ubicaciones",
    "estado": "aplicada",
    "intentos": 1,
    "creada_en": "2026-11-27 01:50:24.653491-06:00"
  },
  {
    "tipo": "entrega_resultado",
    "estado": "aplicada",
    "intentos": 1,
    "creada_en": "2026-11-27 01:58:24.653596-06:00"
  }
]
```

**Evidencia en MongoDB.** `db.ubicaciones_entrega.countDocuments({entrega_id})`

```json
2
```

### F3-04 · La respuesta se perdió y reenvía el mismo lote · PASA

**Objetivo.** No se repite nada.

**Petición.** `POST http://sincronizacion:5125/api/v1/sincronizacion/lotes`

```http
Accept: application/json
X-Traza-Id: 2a996c34-312a-4b44-a30e-233082351192
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "63045dcf-e44b-4305-a244-8447d6e56f3f",
  "dispositivo": "android-flujo-b2b325",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "de7d64ff-6d99-4c6a-ba93-1af819c7b0b2",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-27T07:50:24.653491+00:00",
      "datos": {
        "entrega_id": 458,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-27T07:50:24.653565+00:00"
          },
          {
            "latitud": 25.7491,
            "longitud": -100.3611,
            "capturado_en": "2026-11-27T07:55:24.653575+00:00"
          }
        ]
      }
    },
    {
      "operacion_uuid": "fccb30b4-74a5-4746-9b77-1c1f42d653fb",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-27T07:58:24.653596+00:00",
      "datos": {
        "entrega_id": 458,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "El cliente no estaba en su domicilio",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b093af0f68f301419471810"
        ],
        "capturado_en": "2026-11-27T07:58:24.653602+00:00"
      }
    }
  ]
}
```

**Respuesta.** HTTP 200 (esperado 200) · 280 ms · traza `2a996c34-312a-4b44-a30e-233082351192`

```json
{
  "id": 264,
  "lote_uuid": "63045dcf-e44b-4305-a244-8447d6e56f3f",
  "dispositivo": "android-flujo-b2b325",
  "recibido_en": "2026-11-27T02:10:24-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 2,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "de7d64ff-6d99-4c6a-ba93-1af819c7b0b2",
      "tipo": "ubicaciones",
      "estado": "aplicada",
      "duplicada": true,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    },
    {
      "operacion_uuid": "fccb30b4-74a5-4746-9b77-1c1f42d653fb",
      "tipo": "entrega_resultado",
      "estado": "aplicada",
      "duplicada": true,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    }
  ]
}
```

## Servicio notificaciones · puerto 5124

### F3-05 · El cliente se entera de que la entrega falló · PASA

**Objetivo.** Aviso del motor.

**Petición.** `GET http://notificaciones:5124/api/v1/notificaciones?por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 05a4ace1-368b-45f8-9567-3d01f24c8b8d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 57 ms · traza `05a4ace1-368b-45f8-9567-3d01f24c8b8d`

```json
{
  "datos": [
    {
      "id": 1359,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000792",
      "mensaje": "El pedido cambió a entrega_fallida.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "792"
      },
      "creada_en": "2026-11-27T02:10:24-06:00"
    },
    {
      "id": 1357,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000791",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "791"
      },
      "creada_en": "2026-11-27T02:10:22-06:00"
    },
    {
      "id": 1352,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000790",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "790"
      },
      "creada_en": "2026-11-27T02:10:18-06:00"
    },
    {
      "id": 1322,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000772",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "772"
      },
      "creada_en": "2026-11-27T02:06:41-06:00"
    },
    {
      "id": 1321,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000770",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "770"
      },
      "creada_en": "2026-11-27T02:06:39-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 45,
    "paginas": 9
  }
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F3-06 · El auditor revisa la entrega · PASA

**Objetivo.** Bitácora y archivos de la entrega.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/entrega/458`

```http
Accept: application/json
X-Traza-Id: 9cf2d35e-1b72-4293-839b-11206099c8b6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 53 ms · traza `9cf2d35e-1b72-4293-839b-11206099c8b6`

```json
{
  "objeto": {
    "tipo": "entrega",
    "id": "458"
  },
  "total": 3,
  "eventos": [
    {
      "fecha": "2026-11-27T02:10:24-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "asignada_en = 2026-11-27T02:10:24.543583-06:00; cambio_entregado = None; capturado_en = None; cerrada_por_usuario_id = None",
      "usuario": {
        "id": 3,
        "nombre": "María José Cedillo Mata"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "458"
      },
      "cambios": [
        {
          "campo": "asignada_en",
          "anterior": null,
          "nuevo": "2026-11-27T02:10:24.543583-06:00"
        },
        {
          "campo": "cambio_entregado",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "capturado_en",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "cerrada_por_usuario_id",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "cierre_en",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "cierre_latitud",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "cierre_longitud",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "cierre_precision_m",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "confirmacion_recepcion",
          "anterior": null,
          "nuevo": "false"
        },
        {
          "campo": "costo_entrega_estimado",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "distancia_km",
          "anterior": null,
          "nuevo": null
        },
        {
          "campo": "evidencia_ids",
          "anterior": null,
          "nuevo": null
        }
      ]
    },
    {
      "fecha": "2026-11-27T02:10:24-06:00",
      "origen": "documentos",
      "accion": "documento_subido",
      "descripcion": "evidencia-flujo3-458.jpg (276 bytes, sha256 7f6025cd8a98…)",
      "usuario": {
        "id": 7,
        "nombre": null
      },
      "entidad": {
        "tipo": "documento",
        "id": "6b093af0f68f301419471810"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T02:10:24-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "cambio_entregado = 0.0; capturado_en = 2026-11-27T01:58:24.6…(145 caracteres)",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "458"
      },
      "cambios": [
        {
          "campo": "cambio_entregado",
          "anterior": null,
          "nuevo": "0.0"
        },
        {
          "campo": "capturado_en",
          "anterior": null,
          "nuevo": "2026-11-27T01:58:24.653602-06:00"
        },
        {
          "campo": "cerrada_por_usuario_id",
          "anterior": null,
          "nuevo": "7"
        },
        {
          "campo": "cierre_en",
          "anterior": null,
          "nuevo": "2026-11-27T02:10:24.989486-06:00"
        },
        {
          "campo": "cierre_latitud",
          "anterior": null,
          "nuevo": "25.7491"
        },
        {
          "campo": "cierre_longitud",
          "anterior": null,
          "nuevo": "-100.3611"
        },
        {
          "campo": "evidencia_ids",
          "anterior": null,
          "nuevo": "[\"6b093af0f68f301419471810\"]"
        },
        {
          "campo": "evidencia_url",
          "anterior": null,
          "nuevo": "/api/v1/documentos/6b093af0f68f301419471810"
        },
        {
          "campo": "id_cliente_local",
          "anterior": null,
          "nuevo": "fccb30b4-74a5-4746-9b77-1c1f42d653fb"
        },
        {
          "campo": "incidencia",
          "anterior": null,
          "nuevo": "El cliente no estaba en su domicilio"
        },
        {
          "campo": "monto_cobrado",
          "anterior": null,
          "nuevo": "0.0"
        },
        {
          "campo": "resultado",
          "anterior": null,
          "nuevo": "fallida"
        }
      ]
    }
  ]
}
```

## Servicio inventario · puerto 5111

### F3-07 · El producto regresó al inventario · PASA

**Objetivo.** La devolución la hizo el motor.

**Petición.** `GET http://inventario:5111/api/v1/inventario/movimientos?microhub_id=2&por_pagina=5`

```http
Accept: application/json
X-Traza-Id: 09bf6b36-cfab-499d-a9e2-284a4aad5290
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 56 ms · traza `09bf6b36-cfab-499d-a9e2-284a4aad5290`

```json
{
  "datos": [
    {
      "id": 3072,
      "microhub_id": 2,
      "producto_id": 51,
      "tipo": "devolucion_cancelacion",
      "cantidad": 3,
      "existencia_resultante": 55,
      "referencia": {
        "tipo": "pedido",
        "id": "792"
      },
      "motivo": "Entrega fallida: la mercancía regresa al microhub.",
      "usuario_id": 7,
      "fecha": "2026-11-27T02:10:24-06:00"
    },
    {
      "id": 3071,
      "microhub_id": 2,
      "producto_id": 32,
      "tipo": "devolucion_cancelacion",
      "cantidad": 3,
      "existencia_resultante": 5,
      "referencia": {
        "tipo": "pedido",
        "id": "792"
      },
      "motivo": "Entrega fallida: la mercancía regresa al microhub.",
      "usuario_id": 7,
      "fecha": "2026-11-27T02:10:24-06:00"
    },
    {
      "id": 3070,
      "microhub_id": 2,
      "producto_id": 51,
      "tipo": "salida_pedido",
      "cantidad": -3,
      "existencia_resultante": 52,
      "referencia": {
        "tipo": "pedido",
        "id": "792"
      },
      "motivo": null,
      "usuario_id": 9,
      "fecha": "2026-11-27T02:10:23-06:00"
    },
    {
      "id": 3069,
      "microhub_id": 2,
      "producto_id": 32,
      "tipo": "salida_pedido",
      "cantidad": -3,
      "existencia_resultante": 2,
      "referencia": {
        "tipo": "pedido",
        "id": "792"
      },
      "motivo": null,
      "usuario_id": 9,
      "fecha": "2026-11-27T02:10:23-06:00"
    },
    {
      "id": 3068,
      "microhub_id": 2,
      "producto_id": 31,
      "tipo": "devolucion_cancelacion",
      "cantidad": 10,
      "existencia_resultante": 40,
      "referencia": {
        "tipo": "pedido",
        "id": "791"
      },
      "motivo": "Cierre del flujo de demostración",
      "usuario_id": 1,
      "fecha": "2026-11-27T02:10:22-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 1045,
    "paginas": 209
  }
}
```

**Evidencia en PostgreSQL.** `SELECT tipo, producto_id, cantidad, existencia_resultante FROM movimiento_inventario WHERE referencia_id = %s ORDER BY id`

```json
[
  {
    "tipo": "salida_pedido",
    "producto_id": 32,
    "cantidad": -3,
    "existencia_resultante": 2
  },
  {
    "tipo": "salida_pedido",
    "producto_id": 51,
    "cantidad": -3,
    "existencia_resultante": 52
  },
  {
    "tipo": "devolucion_cancelacion",
    "producto_id": 32,
    "cantidad": 3,
    "existencia_resultante": 5
  },
  {
    "tipo": "devolucion_cancelacion",
    "producto_id": 51,
    "cantidad": 3,
    "existencia_resultante": 55
  }
]
```

## Servicio reportes · puerto 5123

### F3-08 · Reporte del periodo en CSV · PASA

**Objetivo.** La entrega ya cuenta en los reportes.

**Petición.** `GET http://reportes:5123/api/v1/reportes/pedidos_por_dia/exportar?formato=csv`

```http
Accept: application/json
X-Traza-Id: 8349f6e1-29cb-449b-8897-f29a2aacab84
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 222 ms · traza `8349f6e1-29cb-449b-8897-f29a2aacab84`

```json
﻿Día,Pedidos,Unidades,Venta,Ticket promedio,Demanda no atendida
2026-11-25,56,282,8032.40,143.44,0
2026-11-26,212,1096,34991.60,165.05,8
2026-11-27,52,292,9553.10,183.71,3
Total,320,1670,52577.10,164.30,11

```

**Evidencia en PostgreSQL.** `SELECT reporte, formato, filas, left(sha256, 16) AS sha256 FROM reporte_exportacion ORDER BY id DESC LIMIT 1`

```json
[
  {
    "reporte": "pedidos_por_dia",
    "formato": "csv",
    "filas": 3,
    "sha256": "be0e1e1dcdb9faa8"
  }
]
```
