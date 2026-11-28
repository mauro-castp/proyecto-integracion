# Procesos integrales de principio a fin


Generado el 2026-11-28 02:28 contra los servicios en ejecución. 41 de 41 casos pasan.

## Servicio planeacion · puerto 5106

### F1-01 · Escritorio (XML): el planeador registra una ubicación candidata · PASA

**Objetivo.** Planeación de ubicación.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos`

```http
Accept: application/xml
X-Traza-Id: 376d1235-7125-420d-a519-869be969f00a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><candidato_nuevo xmlns="urn:microhubs:v1"><clave>********</clave><nombre>Ubicación del flujo 392E4</nombre><latitud>25.760195</latitud><longitud>-100.370891</longitud><renta_estimada>15000.00</renta_estimada><nomina_estimada>36000.00</nomina_estimada><servicios_estimados>6000.00</servicios_estimados><otros_costos>4000.00</otros_costos><superficie_m2>100</superficie_m2><capacidad_fisica>120</capacidad_fisica><accesibilidad_vial>8</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km></candidato_nuevo>
```

**Respuesta.** HTTP 201 (esperado 201) · 56 ms · traza `376d1235-7125-420d-a519-869be969f00a`

```xml
<?xml version='1.0' encoding='utf-8'?>
<candidato xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>422</id><clave>FL-392E4</clave><nombre>Ubicación del flujo 392E4</nombre><latitud>25.760195</latitud><longitud>-100.370891</longitud><renta_estimada>15000.00</renta_estimada><nomina_estimada>36000.00</nomina_estimada><servicios_estimados>6000.00</servicios_estimados><otros_costos>4000.00</otros_costos><costo_fijo>61000.00</costo_fijo><superficie_m2>100</superficie_m2><capacidad_fisica>120</capacidad_fisica><accesibilidad_vial>8</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato>
```

**Evidencia en PostgreSQL.** `SELECT id, clave, nombre, costo_fijo, decision FROM ubicacion_candidata WHERE clave = %s`

```json
[
  {
    "id": 422,
    "clave": "FL-392E4",
    "nombre": "Ubicación del flujo 392E4",
    "costo_fijo": "61000.00",
    "decision": "pendiente"
  }
]
```

### F1-02 · El planeador simula la operación de la candidata · PASA

**Objetivo.** Capacidad, utilización y decisión sugerida (MongoDB).

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/422/simular`

```http
Accept: application/json
X-Traza-Id: 640b86e2-3c1c-4bf6-8824-f06d27bcdee5
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

**Respuesta.** HTTP 200 (esperado 200) · 257 ms · traza `640b86e2-3c1c-4bf6-8824-f06d27bcdee5`

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
X-Traza-Id: 1ab2bcdc-e138-4cb1-af0c-5a63caeec6ce
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "candidato_id": 422,
  "pedidos_dia": 100,
  "ticket": 180,
  "margen_bruto": 0.3,
  "costos_fijos": 61000,
  "costo_variable_pedido": 22
}
```

**Respuesta.** HTTP 200 (esperado 200) · 27 ms · traza `1ab2bcdc-e138-4cb1-af0c-5a63caeec6ce`

```json
{
  "id": null,
  "nombre": null,
  "objeto": {
    "tipo": "candidato",
    "id": 422,
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

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/422/decision`

```http
Accept: application/json
X-Traza-Id: 23b967c1-0649-4bb7-a66b-e1be54c893da
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aceptado",
  "motivo": "Cubre la zona del cliente y la demanda esperada supera el equilibrio."
}
```

**Respuesta.** HTTP 200 (esperado 200) · 69 ms · traza `23b967c1-0649-4bb7-a66b-e1be54c893da`

```json
{
  "id": 422,
  "clave": "********",
  "nombre": "Ubicación del flujo 392E4",
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
X-Traza-Id: 46f27148-b9ce-4dcd-b91e-fa84ce5783e6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "clave": "********",
  "nombre": "Microhub 392E4",
  "direccion": "Ubicación aprobada en planeación",
  "latitud": 25.760195,
  "longitud": -100.370891,
  "radio_km": 1.5,
  "capacidad_turno": 120
}
```

**Respuesta.** HTTP 201 (esperado 201) · 115 ms · traza `46f27148-b9ce-4dcd-b91e-fa84ce5783e6`

```json
{
  "id": 31,
  "clave": "********",
  "nombre": "Microhub 392E4",
  "latitud": 25.760195,
  "longitud": -100.370891,
  "radio_km": 1.5,
  "estatus": "activo"
}
```

## Servicio capacidad · puerto 5117

### F1-06 · Asignar personal al microhub · PASA

**Objetivo.** Operadores, repartidores y capacidad física.

**Petición.** `PUT http://capacidad:5117/api/v1/capacidad/recursos/31`

```http
Accept: application/json
X-Traza-Id: edfc9c57-ee9e-42db-b79c-4e332a866633
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

**Respuesta.** HTTP 200 (esperado 200) · 152 ms · traza `edfc9c57-ee9e-42db-b79c-4e332a866633`

```json
{
  "microhub": {
    "id": 31,
    "nombre": "Microhub 392E4"
  },
  "operadores": 2,
  "repartidores": 2,
  "capacidad_fisica": 120,
  "actualizado_en": "2026-11-27T20:28:31-06:00"
}
```

## Servicio usuarios · puerto 5102

### F1-07 · Crear la cuenta del operador · PASA

**Objetivo.** Cuenta nueva con su perfil y su microhub.

**Petición.** `POST http://usuarios:5102/api/v1/usuarios`

```http
Accept: application/json
X-Traza-Id: f70b0fde-5a2b-4162-81d8-a66dd469e4c6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Operador",
  "apellidos": "392E4",
  "correo": "operador.392e4@ejemplo.mx",
  "clave": "********",
  "rol": "operador",
  "microhub_id": 31
}
```

**Respuesta.** HTTP 201 (esperado 201) · 166 ms · traza `f70b0fde-5a2b-4162-81d8-a66dd469e4c6`

```json
{
  "id": 100,
  "nombre": "Operador",
  "apellidos": "392E4",
  "correo": "operador.392e4@ejemplo.mx",
  "telefono": null,
  "rol": "operador",
  "microhub": {
    "id": 31,
    "clave": "********",
    "nombre": "Microhub 392E4"
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
X-Traza-Id: 3bc7fb80-64f5-44fa-9f82-3bb18bf86a73
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "origen_microhub_id": 1,
  "destino_microhub_id": 31,
  "producto_id": 31,
  "cantidad": 12,
  "motivo": "Inventario inicial del microhub nuevo",
  "operacion_uuid": "7cf9e900-1618-4742-8465-a4fef5db19b3"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 93 ms · traza `3bc7fb80-64f5-44fa-9f82-3bb18bf86a73`

```json
{
  "producto_id": 31,
  "cantidad": 12,
  "duplicado": false,
  "origen": {
    "microhub_id": 1,
    "existencia": 731,
    "movimiento_id": 3588
  },
  "destino": {
    "microhub_id": 31,
    "existencia": 12,
    "movimiento_id": 3589
  }
}
```

### F1-08b · Surtir el microhub nuevo · PASA

**Objetivo.** Transferencia atómica desde MH-01.

**Petición.** `POST http://inventario:5111/api/v1/inventario/transferencias`

```http
Accept: application/json
X-Traza-Id: 543cd0f9-cf4b-44cb-bb03-9b8b22b617f5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "origen_microhub_id": 1,
  "destino_microhub_id": 31,
  "producto_id": 23,
  "cantidad": 12,
  "motivo": "Inventario inicial del microhub nuevo",
  "operacion_uuid": "c8730813-2a94-4e62-ae6c-a38aadb1eb2c"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 90 ms · traza `543cd0f9-cf4b-44cb-bb03-9b8b22b617f5`

```json
{
  "producto_id": 23,
  "cantidad": 12,
  "duplicado": false,
  "origen": {
    "microhub_id": 1,
    "existencia": 40,
    "movimiento_id": 3590
  },
  "destino": {
    "microhub_id": 31,
    "existencia": 12,
    "movimiento_id": 3591
  }
}
```

## Servicio pedidos · puerto 5104

### F1-09 · Android (JSON): el cliente hace su pedido · PASA

**Objetivo.** El motor lo asigna al microhub más cercano que tiene todo: el nuevo.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: d4e086d3-2b11-4dd8-af50-f282e8d4f93d
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
      "producto_id": 23,
      "cantidad": 3
    }
  ],
  "operacion_uuid": "109fcaff-dd2f-484e-a05c-d60405558c65"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 253 ms · traza `d4e086d3-2b11-4dd8-af50-f282e8d4f93d`

```json
{
  "id": 1081,
  "folio": "PED-20261127-001081",
  "estado": "asignado",
  "zona_id": 3,
  "microhub_id": 31,
  "subtotal": 289.5,
  "costo_envio": 0.0,
  "total": 289.5,
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
    "microhub_ganador_id": 31,
    "motivo": null
  }
]
```

**Evidencia en PostgreSQL.** `SELECT tipo, producto_id, cantidad, existencia_resultante FROM movimiento_inventario WHERE referencia_tipo = 'pedido' AND referencia_id = %s`

```json
[
  {
    "tipo": "salida_pedido",
    "producto_id": 23,
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

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/1081/estado`

```http
Accept: application/json
X-Traza-Id: 981237bb-af44-45f1-9dde-c2ad4419f3f4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMDAi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "estado": "en_preparacion"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 105 ms · traza `981237bb-af44-45f1-9dde-c2ad4419f3f4`

```json
{
  "id": 1081,
  "folio": "PED-20261127-001081",
  "estado": "en_preparacion",
  "zona": {
    "id": 3,
    "nombre": "Paseo de San Bernabé"
  },
  "microhub_id": 31,
  "total": 289.5,
  "creado_en": "2026-11-27T20:28:32-06:00"
}
```

### F1-11 · El operador lo marca listo · PASA

**Objetivo.** Queda disponible para despacho.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/1081/listo`

```http
Accept: application/json
X-Traza-Id: 7a4b2611-395c-43d5-9a38-610782ec159c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMDAi…(298 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 200 (esperado 200) · 74 ms · traza `7a4b2611-395c-43d5-9a38-610782ec159c`

```json
{
  "id": 1081,
  "estado": "en_preparacion",
  "listo_en": "2026-11-27T20:28:32-06:00"
}
```

## Servicio usuarios · puerto 5102

### F1-07b · Crear la cuenta del repartidor del microhub · PASA

**Objetivo.** RN41: cada repartidor pertenece a un microhub.

**Petición.** `POST http://usuarios:5102/api/v1/usuarios`

```http
Accept: application/json
X-Traza-Id: a8ab28f7-3937-4896-bf91-148bfcf02a5c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Repartidor",
  "apellidos": "392E4",
  "correo": "repartidor.392e4@ejemplo.mx",
  "clave": "********",
  "rol": "repartidor",
  "microhub_id": 31
}
```

**Respuesta.** HTTP 201 (esperado 201) · 170 ms · traza `a8ab28f7-3937-4896-bf91-148bfcf02a5c`

```json
{
  "id": 101,
  "nombre": "Repartidor",
  "apellidos": "392E4",
  "correo": "repartidor.392e4@ejemplo.mx",
  "telefono": null,
  "rol": "repartidor",
  "microhub": {
    "id": 31,
    "clave": "********",
    "nombre": "Microhub 392E4"
  },
  "ultimo_acceso": null
}
```

## Servicio rutas · puerto 5118

### F1-12 · Proponer la ruta de despacho · PASA

**Objetivo.** Agrupa, asigna repartidor y ordena las paradas (algoritmo de rutas).

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/json
X-Traza-Id: 42bbb5e2-0aef-4364-87d3-8b43c801855e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMDAi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 31,
  "pedido_ids": [
    1081
  ],
  "repartidor_ids": [
    101
  ],
  "metodo": "automatico",
  "guardar": true
}
```

**Respuesta.** HTTP 201 (esperado 201) · 304 ms · traza `42bbb5e2-0aef-4364-87d3-8b43c801855e`

```json
{
  "id": 167,
  "estado": "propuesto",
  "version": 1,
  "microhub": {
    "id": 31,
    "nombre": "Microhub 392E4"
  },
  "fecha": "2026-11-27",
  "metodo_pedido": "automatico",
  "rutas": [
    {
      "repartidor": {
        "id": 101,
        "nombre": "Repartidor 392E4"
      },
      "metodo": "TSP exacto",
      "zonas": [
        "Paseo de San Bernabé"
      ],
      "paradas": [
        {
          "orden": 1,
          "pedido": {
            "id": 1081,
            "folio": "PED-20261127-001081"
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
X-Traza-Id: 3ff3d9ca-8411-4822-93d7-029fe5c675b4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMDAi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "pedido_id": 1081,
  "repartidor_id": 101,
  "orden_parada": 1
}
```

**Respuesta.** HTTP 201 (esperado 201) · 105 ms · traza `3ff3d9ca-8411-4822-93d7-029fe5c675b4`

```json
{
  "entrega_id": 517,
  "pedido_id": 1081,
  "repartidor_id": 101,
  "estado_pedido": "en_ruta"
}
```

**Evidencia en PostgreSQL.** `SELECT titulo, tipo, referencia_id FROM web_notificacion WHERE destinatario_id = %s ORDER BY id DESC LIMIT 1`

```json
[
  {
    "titulo": "Nueva entrega asignada",
    "tipo": "entrega",
    "referencia_id": "517"
  }
]
```

### F1-14 · Android: el repartidor ve su parada · PASA

**Objetivo.** Sesión validada en Redis.

**Petición.** `GET http://entregas:5105/api/v1/entregas/mias?por_pagina=50`

```http
Accept: application/json
X-Traza-Id: 059a28ee-da3e-4a9e-9891-90e888ca94c9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMDEi…(303 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 104 ms · traza `059a28ee-da3e-4a9e-9891-90e888ca94c9`

```json
{
  "datos": [
    {
      "id": 517,
      "pedido_id": 1081,
      "folio": "PED-20261127-001081",
      "estado_pedido": "en_ruta",
      "orden_parada": 1,
      "direccion": "Nogal 1440, Paseo de San Bernabé",
      "zona": "Paseo de San Bernabé",
      "distancia_km": null,
      "minutos_estimados": null,
      "total": 289.5
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 50,
    "total": 1,
    "paginas": 1
  }
}
```

**Evidencia en Redis.** `SCARD auth:sesion:101`

```json
[
  {
    "comando": "SCARD auth:sesion:101",
    "valor": 1
  }
]
```

## Servicio seguimiento · puerto 5110

### F1-15 · El repartidor envía su recorrido · PASA

**Objetivo.** Puntos GPS en MongoDB (2dsphere).

**Petición.** `POST http://seguimiento:5110/api/v1/seguimiento/517/ubicaciones`

```http
Accept: application/json
X-Traza-Id: 138f27d7-98e1-4b6e-bc42-ba0964c75d8d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMDEi…(303 caracteres)
Content-Type: application/json
```

```json
{
  "puntos": [
    {
      "latitud": 25.760195,
      "longitud": -100.370891,
      "capturado_en": "2026-11-28T02:24:33.605746+00:00"
    },
    {
      "latitud": 25.759995,
      "longitud": -100.371091,
      "capturado_en": "2026-11-28T02:27:33.605821+00:00"
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 66 ms · traza `138f27d7-98e1-4b6e-bc42-ba0964c75d8d`

```json
{
  "recibidos": 2
}
```

## Servicio documentos · puerto 5107

### F1-16 · La foto de evidencia queda en el almacén · PASA

**Objetivo.** En la base solo sus datos; se descarga con un enlace firmado.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b0a3c51e768f05cdb023a98/enlace`

```http
Accept: application/json
X-Traza-Id: 0f48a008-6237-47bd-8d6e-3c0cc865a4f5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 57 ms · traza `0f48a008-6237-47bd-8d6e-3c0cc865a4f5`

```json
{
  "id": "6b0a3c51e768f05cdb023a98",
  "nombre": "evidencia-flujo1-392E4.jpg",
  "url_firmada": "http://documentos:5107/api/v1/documentos/descarga?k=document…(208 caracteres)",
  "metodo": "GET",
  "segundos": 300,
  "expira_en": "2026-11-27T20:33:33-06:00"
}
```

**Evidencia en MongoDB.** `db.documentos.findOne({_id}) sin contenido`

```json
{
  "_id": "6b0a3c51e768f05cdb023a98",
  "nombre": "evidencia-flujo1-392E4.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "517"
  },
  "subido_por": 101,
  "creado_en": "2026-11-28 02:28:33.712000+00:00",
  "ruta": "documentos/2026/11/6b0a3c51e768f05cdb023a98.jpg",
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

**Petición.** `POST http://entregas:5105/api/v1/entregas/517/resultado`

```http
Accept: application/json
X-Traza-Id: fb097acc-c401-4610-84a9-28b4bea0d82b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMDEi…(303 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 289.5,
  "cambio_entregado": 0,
  "ubicacion": {
    "latitud": 25.759995,
    "longitud": -100.371091
  },
  "evidencia_ids": [
    "6b0a3c51e768f05cdb023a98"
  ],
  "capturado_en": "2026-11-28T02:28:34.050770+00:00",
  "id_cliente_local": "84d0e99a-6caf-4831-a429-304a181c081d"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 110 ms · traza `fb097acc-c401-4610-84a9-28b4bea0d82b`

```json
{
  "entrega_id": 517,
  "pedido_id": 1081,
  "estado_pedido": "entregado",
  "cerrado_en": "2026-11-27T20:28:34-06:00",
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
    "usuario_id": 100,
    "proceso": null
  },
  {
    "estado_anterior": "en_preparacion",
    "estado_nuevo": "en_ruta",
    "usuario_id": 100,
    "proceso": null
  },
  {
    "estado_anterior": "en_ruta",
    "estado_nuevo": "entregado",
    "usuario_id": 101,
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
X-Traza-Id: 1e438518-ece2-4ec0-8019-d1f1df9457c9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 46 ms · traza `1e438518-ece2-4ec0-8019-d1f1df9457c9`

```json
{
  "datos": [
    {
      "id": 1663,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-001081",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "1081"
      },
      "creada_en": "2026-11-27T20:28:34-06:00"
    },
    {
      "id": 1629,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-001059",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "1059"
      },
      "creada_en": "2026-11-27T20:00:17-06:00"
    },
    {
      "id": 1621,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-001033",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "1033"
      },
      "creada_en": "2026-11-27T19:59:03-06:00"
    },
    {
      "id": 1580,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000883",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "883"
      },
      "creada_en": "2026-11-27T19:56:29-06:00"
    },
    {
      "id": 1575,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000886",
      "mensaje": "El pedido cambió a entrega_fallida.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "886"
      },
      "creada_en": "2026-11-27T11:38:17-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 61,
    "paginas": 13
  }
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F1-19 · El auditor reconstruye la historia del pedido · PASA

**Objetivo.** Bitácora, estados, inventario y archivos en una línea de tiempo.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/pedido/1081`

```http
Accept: application/json
X-Traza-Id: 7e67b4f6-70f8-48bc-98d5-45db1cf56ac1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 111 ms · traza `7e67b4f6-70f8-48bc-98d5-45db1cf56ac1`

```json
{
  "objeto": {
    "tipo": "pedido",
    "id": "1081"
  },
  "total": 15,
  "eventos": [
    {
      "fecha": "2026-11-27T20:28:32-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "actualizado_en = 2026-11-27T20:28:32.239687-06:00; asignado_en = None; cerrado_en = None; cliente_id = 1",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "1081"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": null,
          "nuevo": "2026-11-27T20:28:32.239687-06:00"
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
          "nuevo": "2026-11-27T20:28:32.239687-06:00"
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
          "nuevo": "PED-20261127-001081"
        },
        {
          "campo": "id",
          "anterior": null,
          "nuevo": "1081"
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
      "fecha": "2026-11-27T20:28:32-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "asignado_en = 2026-11-27T20:28:32.239687-06:00; estado: creado → asignado; microhub_id = 31",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "1081"
      },
      "cambios": [
        {
          "campo": "asignado_en",
          "anterior": null,
          "nuevo": "2026-11-27T20:28:32.239687-06:00"
        },
        {
          "campo": "estado",
          "anterior": "creado",
          "nuevo": "asignado"
        },
        {
          "campo": "microhub_id",
          "anterior": null,
          "nuevo": "31"
        }
      ]
    },
    {
      "fecha": "2026-11-27T20:28:32-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "nuevo → creado",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "1081"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T20:28:32-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "creado → asignado",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "1081"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T20:28:32-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -3 de producto 23 en microhub 31 (existencia 9)",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "31-23"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T20:28:32-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -3 de producto 31 en microhub 31 (existencia 9)",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "31-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T20:28:32-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-27T20:28:32.239687-06:00 → 2026-11-27T20:28:32.463742-06:00; estado: asignado → en_preparacion",
      "usuario": {
        "id": 100,
        "nombre": "Operador 392E4"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "1081"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-27T20:28:32.239687-06:00",
          "nuevo": "2026-11-27T20:28:32.463742-06:00"
        },
        {
          "campo": "estado",
          "anterior": "asignado",
          "nuevo": "en_preparacion"
        }
      ]
    },
    {
      "fecha": "2026-11-27T20:28:32-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "asignado → en_preparacion",
      "usuario": {
        "id": 100,
        "nombre": "Operador 392E4"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "1081"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T20:28:32-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "listo_en = 2026-11-27T20:28:32.56629-06:00",
      "usuario": {
        "id": 100,
        "nombre": "Operador 392E4"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "1081"
      },
      "cambios": [
        {
          "campo": "listo_en",
          "anterior": null,
          "nuevo": "2026-11-27T20:28:32.56629-06:00"
        }
      ]
    },
    {
      "fecha": "2026-11-27T20:28:33-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "asignada_en = 2026-11-27T20:28:33.388571-06:00; cambio_entregado = None; capturado_en = None; cerrada_por_usuario_id = None",
      "usuario": {
        "id": 100,
        "nombre": "Operador 392E4"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "517"
      },
      "cambios": [
        {
          "campo": "asignada_en",
          "anterior": null,
          "nuevo": "2026-11-27T20:28:33.388571-06:00"
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
      "fecha": "2026-11-27T20:28:33-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-27T20:28:32.463742-06:00 → 2026-11-27T20:28:33.388571-06:00; estado: en_preparacion → en_ruta",
      "usuario": {
        "id": 100,
        "nombre": "Operador 392E4"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "1081"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-27T20:28:32.463742-06:00",
          "nuevo": "2026-11-27T20:28:33.388571-06:00"
        },
        {
          "campo": "estado",
          "anterior": "en_preparacion",
          "nuevo": "en_ruta"
        }
      ]
    },
    {
      "fecha": "2026-11-27T20:28:33-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "en_preparacion → en_ruta",
      "usuario": {
        "id": 100,
        "nombre": "Operador 392E4"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "1081"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T20:28:34-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "cambio_entregado = 0.0; capturado_en = 2026-11-27T20:28:34.0…(146 caracteres)",
      "usuario": {
        "id": 101,
        "nombre": "Repartidor 392E4"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "517"
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
          "nuevo": "2026-11-27T20:28:34.05077-06:00"
        },
        {
          "campo": "cerrada_por_usuario_id",
          "anterior": null,
          "nuevo": "101"
        },
        {
          "campo": "cierre_en",
          "anterior": null,
          "nuevo": "2026-11-27T20:28:34.102843-06:00"
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
          "nuevo": "[\"6b0a3c51e768f05cdb023a98\"]"
        },
        {
          "campo": "evidencia_url",
          "anterior": null,
          "nuevo": "/api/v1/documentos/6b0a3c51e768f05cdb023a98"
        },
        {
          "campo": "id_cliente_local",
          "anterior": null,
          "nuevo": "84d0e99a-6caf-4831-a429-304a181c081d"
        },
        {
          "campo": "monto_cobrado",
          "anterior": null,
          "nuevo": "289.5"
        },
        {
          "campo": "resultado",
          "anterior": null,
          "nuevo": "entregado"
        }
      ]
    },
    {
      "fecha": "2026-11-27T20:28:34-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-27T20:28:33.388571-06:00 → 2026-11-2…(159 caracteres)",
      "usuario": {
        "id": 101,
        "nombre": "Repartidor 392E4"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "1081"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-27T20:28:33.388571-06:00",
          "nuevo": "2026-11-27T20:28:34.102843-06:00"
        },
        {
          "campo": "cerrado_en",
          "anterior": null,
          "nuevo": "2026-11-27T20:28:34.102843-06:00"
        },
        {
          "campo": "estado",
          "anterior": "en_ruta",
          "nuevo": "entregado"
        }
      ]
    },
    {
      "fecha": "2026-11-27T20:28:34-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "en_ruta → entregado",
      "usuario": {
        "id": 101,
        "nombre": "Repartidor 392E4"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "1081"
      },
      "cambios": []
    }
  ]
}
```

## Servicio reportes · puerto 5123

### F1-20 · Visualización: el microhub nuevo ya aparece en la comparación · PASA

**Objetivo.** Datos listos para Highcharts.

**Petición.** `GET http://reportes:5123/api/v1/reportes/comparacion_microhubs/grafica?microhub_id=31`

```http
Accept: application/json
X-Traza-Id: b3426ffe-ac54-410f-9553-d7c165f78873
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 114 ms · traza `b3426ffe-ac54-410f-9553-d7c165f78873`

```json
{
  "reporte": "comparacion_microhubs",
  "titulo": "Comparación entre microhubs",
  "tipo": "column",
  "unidad": "pedidos / MXN",
  "categorias": [
    "Microhub 392E4"
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
        289.5
      ]
    }
  ]
}
```

## Servicio microhubs · puerto 5109

### F1-21 · Cierre: dar de baja el microhub de la demostración · PASA

**Objetivo.** Baja lógica; conserva su historia.

**Petición.** `DELETE http://microhubs:5109/api/v1/microhubs/31`

```http
Accept: application/json
X-Traza-Id: 143c5635-3aff-47df-bf1d-1ddf0f6e998d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 49 ms · traza `143c5635-3aff-47df-bf1d-1ddf0f6e998d`

```json
(sin cuerpo)
```

## Servicio pedidos · puerto 5104

### F2-01 · Android: un cliente compra y el inventario baja · PASA

**Objetivo.** El motor descuenta inventario en la misma transacción.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: 2d6a5240-2791-42d1-b592-c0fa7d701a90
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
  "operacion_uuid": "ca62d01e-11ee-4fa2-8d1a-9fb7796713fe"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 280 ms · traza `2d6a5240-2791-42d1-b592-c0fa7d701a90`

```json
{
  "id": 1082,
  "folio": "PED-20261127-001082",
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
    "existencia_resultante": 17
  }
]
```

## Servicio inventario · puerto 5111

### F2-02 · El operador fija el mínimo y nace la alerta · PASA

**Objetivo.** El trigger avisa del faltante.

**Petición.** `PATCH http://inventario:5111/api/v1/inventario/1/31/minimo`

```http
Accept: application/json
X-Traza-Id: 15e27363-2584-43ce-b8e2-09fc93ec576c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "minimo": 741
}
```

**Respuesta.** HTTP 200 (esperado 200) · 261 ms · traza `15e27363-2584-43ce-b8e2-09fc93ec576c`

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
  "existencia": 731,
  "minimo": 741,
  "reservado": 0,
  "disponible": 731,
  "estado": "bajo_minimo",
  "actualizado_en": "2026-11-27T20:28:36-06:00"
}
```

### F2-03 · La alerta de faltante · PASA

**Objetivo.** Qué producto, cuánto falta y qué tan grave es.

**Petición.** `GET http://inventario:5111/api/v1/inventario/alertas?microhub_id=1&por_pagina=100`

```http
Accept: application/json
X-Traza-Id: 16dc02a7-53be-4860-bd54-122754a3ad39
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 94 ms · traza `16dc02a7-53be-4860-bd54-122754a3ad39`

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
      "existencia": 731,
      "minimo": 741,
      "disponible": 731,
      "faltante": 10,
      "severidad": "baja"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 30,
        "clave_interna": "LA-002",
        "nombre": "Leche deslactosada"
      },
      "existencia": 3,
      "minimo": 5,
      "disponible": 3,
      "faltante": 2,
      "severidad": "baja"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 26,
        "clave_interna": "BE-006",
        "nombre": "Bebida de soya"
      },
      "existencia": 9,
      "minimo": 10,
      "disponible": 9,
      "faltante": 1,
      "severidad": "baja"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 100,
    "total": 3,
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
X-Traza-Id: a89d41ac-6288-43f3-95a7-fa0b90ffb3db
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

**Respuesta.** HTTP 201 (esperado 201) · 83 ms · traza `a89d41ac-6288-43f3-95a7-fa0b90ffb3db`

```json
{
  "id": 130,
  "folio": "SC-20261127-000130",
  "microhub_id": 1,
  "estado": "pendiente",
  "motivo": "Faltante detectado por el sistema",
  "solicitada_por": 2,
  "decidida_por": null,
  "decision_motivo": null,
  "decidida_en": null,
  "creada_en": "2026-11-27T20:28:36-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/130/decision`

```http
Accept: application/json
X-Traza-Id: 8ed4a0eb-a160-48cb-b03b-dc1c43047cc2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aprobada",
  "motivo": "Con presupuesto"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 93 ms · traza `8ed4a0eb-a160-48cb-b03b-dc1c43047cc2`

```json
{
  "id": 130,
  "folio": "SC-20261127-000130",
  "microhub_id": 1,
  "estado": "aprobada",
  "motivo": "Faltante detectado por el sistema",
  "solicitada_por": 2,
  "decidida_por": 1,
  "decision_motivo": "Con presupuesto",
  "decidida_en": "2026-11-27T20:28:36-06:00",
  "creada_en": "2026-11-27T20:28:36-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/130/ordenar`

```http
Accept: application/json
X-Traza-Id: ec1653a1-1b50-48a3-8afa-ea2c8905f7c5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 201 (esperado 201) · 201 ms · traza `ec1653a1-1b50-48a3-8afa-ea2c8905f7c5`

```json
{
  "solicitud_id": 130,
  "ordenes": [
    {
      "id": 85,
      "folio": "OC-20261127-000085",
      "solicitud_id": 130,
      "proveedor": {
        "id": 1,
        "nombre": "Abarrotes del Norte"
      },
      "microhub_id": 1,
      "estado": "emitida",
      "fecha_esperada": "2026-11-29",
      "total": 4060.0,
      "creada_en": "2026-11-27T20:28:36-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/85/recepcion`

```http
Accept: application/json
X-Traza-Id: 5a46c20b-5611-4394-9ce7-1ee73ef9c1e4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "operacion_uuid": "97154ef7-f4c6-4f1d-a172-87d84cdb17a9",
  "nota": "Completo",
  "lineas": [
    {
      "producto_id": 31,
      "cantidad": 100
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 276 ms · traza `5a46c20b-5611-4394-9ce7-1ee73ef9c1e4`

```json
{
  "orden": {
    "id": 85,
    "folio": "OC-20261127-000085",
    "solicitud_id": 130,
    "proveedor": {
      "id": 1,
      "nombre": "Abarrotes del Norte"
    },
    "microhub_id": 1,
    "estado": "recibida",
    "fecha_esperada": "2026-11-29",
    "total": 4060.0,
    "creada_en": "2026-11-27T20:28:36-06:00",
    "cerrada_en": "2026-11-27T20:28:37-06:00",
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
    "existencia": 831,
    "minimo": 741
  }
]
```

## Servicio documentos · puerto 5107

### F2-08 · La remisión firmada queda en el almacén · PASA

**Objetivo.** Archivo con enlace firmado.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b0a3c55e768f05cdb023a9d/enlace`

```http
Accept: application/json
X-Traza-Id: a4111302-94ba-4b45-8d48-531a5bcd4f9e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 39 ms · traza `a4111302-94ba-4b45-8d48-531a5bcd4f9e`

```json
{
  "id": "6b0a3c55e768f05cdb023a9d",
  "nombre": "remision-85.jpg",
  "url_firmada": "http://documentos:5107/api/v1/documentos/descarga?k=document…(197 caracteres)",
  "metodo": "GET",
  "segundos": 300,
  "expira_en": "2026-11-27T20:33:37-06:00"
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F2-09 · Trazabilidad del producto en el microhub · PASA

**Objetivo.** Salida por pedido y recepción por orden.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/inventario?microhub_id=1&producto_id=31`

```http
Accept: application/json
X-Traza-Id: 31c96e7a-e729-4bc4-a4aa-7428735d6a8e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 53 ms · traza `31c96e7a-e729-4bc4-a4aa-7428735d6a8e`

```json
{
  "objeto": {
    "tipo": "inventario",
    "id": "1-31"
  },
  "total": 31,
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
    },
    {
      "fecha": "2026-11-27T11:32:48-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "transferencia_salida: -12 de producto 31 en microhub 1 (existencia 379). Inventario inicial del microhub nuevo",
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
      "fecha": "2026-11-27T11:32:52-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "recepcion: +100 de producto 31 en microhub 1 (existencia 479). Recepción de la orden OC-20261127-000073: Completo",
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
      "fecha": "2026-11-27T11:37:23-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "transferencia_salida: -12 de producto 31 en microhub 1 (existencia 467). Inventario inicial del microhub nuevo",
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
      "fecha": "2026-11-27T11:37:28-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "recepcion: +100 de producto 31 en microhub 1 (existencia 567). Recepción de la orden OC-20261127-000077: Completo",
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
      "fecha": "2026-11-27T11:38:10-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "transferencia_salida: -12 de producto 31 en microhub 1 (existencia 555). Inventario inicial del microhub nuevo",
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
      "fecha": "2026-11-27T11:38:14-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "recepcion: +100 de producto 31 en microhub 1 (existencia 655). Recepción de la orden OC-20261127-000078: Completo",
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
      "fecha": "2026-11-27T20:00:12-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "transferencia_salida: -12 de producto 31 en microhub 1 (existencia 643). Inventario inicial del microhub nuevo",
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
      "fecha": "2026-11-27T20:00:16-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "recepcion: +100 de producto 31 en microhub 1 (existencia 743). Recepción de la orden OC-20261127-000082: Completo",
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
      "fecha": "2026-11-27T20:28:31-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "transferencia_salida: -12 de producto 31 en microhub 1 (existencia 731). Inventario inicial del microhub nuevo",
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
      "fecha": "2026-11-27T20:28:37-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "recepcion: +100 de producto 31 en microhub 1 (existencia 831). Recepción de la orden OC-20261127-000085: Completo",
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
X-Traza-Id: 99328d89-89dc-4e8a-8835-dad0b027ab41
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 170 ms · traza `99328d89-89dc-4e8a-8835-dad0b027ab41`

```json
﻿Microhub,Producto,Existencia,Mínimo,Disponible,Faltante,Severidad
Microhub San Bernabé Centro,Leche deslactosada,3,5,3,2,baja
Microhub San Bernabé Centro,Bebida de soya,9,10,9,1,baja
Total,,,,,3,

```

## Servicio pedidos · puerto 5104

### F3-01 · El cliente hace un pedido · PASA

**Objetivo.** Punto de partida del recorrido.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: 6f487f9e-2c8e-4366-b334-d8300daba49d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
Content-Type: application/json
```

```json
{
  "lineas": [
    {
      "producto_id": 51,
      "cantidad": 3
    },
    {
      "producto_id": 31,
      "cantidad": 3
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 194 ms · traza `6f487f9e-2c8e-4366-b334-d8300daba49d`

```json
{
  "id": 1083,
  "folio": "PED-20261127-001083",
  "estado": "asignado",
  "zona_id": 3,
  "microhub_id": 2,
  "subtotal": 378.0,
  "costo_envio": 0.0,
  "total": 378.0,
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
X-Traza-Id: 9aed7478-2a27-4184-b4a3-621ddd6f6d40
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
Content-Type: application/json
```

```json
{
  "pedido_id": 1083,
  "repartidor_id": 8
}
```

**Respuesta.** HTTP 201 (esperado 201) · 55 ms · traza `9aed7478-2a27-4184-b4a3-621ddd6f6d40`

```json
{
  "entrega_id": 518,
  "pedido_id": 1083,
  "repartidor_id": 8,
  "estado_pedido": "en_ruta"
}
```

## Servicio sincronizacion · puerto 5125

### F3-03 · Android recupera la red y manda lo hecho sin conexión · PASA

**Objetivo.** Se aplica en el orden en que ocurrió.

**Petición.** `POST http://sincronizacion:5125/api/v1/sincronizacion/lotes`

```http
Accept: application/json
X-Traza-Id: c5da07aa-a1a6-41f5-8261-edfad7835ed3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4Iiwi…(292 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "81b58773-ba0a-4ae8-b2f2-28bc76fb4d0c",
  "dispositivo": "android-flujo-b45bb8",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "2badd633-f313-404f-9a76-5db6432d1e39",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-28T02:08:39.851871+00:00",
      "datos": {
        "entrega_id": 518,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-28T02:08:39.851894+00:00"
          },
          {
            "latitud": 25.7491,
            "longitud": -100.3611,
            "capturado_en": "2026-11-28T02:13:39.851903+00:00"
          }
        ]
      }
    },
    {
      "operacion_uuid": "b95d23fa-59a0-4063-bdb9-346128c7dd05",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-28T02:16:39.851926+00:00",
      "datos": {
        "entrega_id": 518,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "El cliente no estaba en su domicilio",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b0a3c57a55f138667f109a2"
        ],
        "capturado_en": "2026-11-28T02:16:39.851942+00:00"
      }
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 453 ms · traza `c5da07aa-a1a6-41f5-8261-edfad7835ed3`

```json
{
  "id": 299,
  "lote_uuid": "81b58773-ba0a-4ae8-b2f2-28bc76fb4d0c",
  "dispositivo": "android-flujo-b45bb8",
  "recibido_en": "2026-11-27T20:28:39-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 0,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "2badd633-f313-404f-9a76-5db6432d1e39",
      "tipo": "ubicaciones",
      "estado": "aplicada",
      "duplicada": false,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    },
    {
      "operacion_uuid": "b95d23fa-59a0-4063-bdb9-346128c7dd05",
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
    "creada_en": "2026-11-27 20:08:39.851871-06:00"
  },
  {
    "tipo": "entrega_resultado",
    "estado": "aplicada",
    "intentos": 1,
    "creada_en": "2026-11-27 20:16:39.851926-06:00"
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
X-Traza-Id: 3a752344-3f9d-4c14-9b73-d2a3cb7170fc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4Iiwi…(292 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "81b58773-ba0a-4ae8-b2f2-28bc76fb4d0c",
  "dispositivo": "android-flujo-b45bb8",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "2badd633-f313-404f-9a76-5db6432d1e39",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-28T02:08:39.851871+00:00",
      "datos": {
        "entrega_id": 518,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-28T02:08:39.851894+00:00"
          },
          {
            "latitud": 25.7491,
            "longitud": -100.3611,
            "capturado_en": "2026-11-28T02:13:39.851903+00:00"
          }
        ]
      }
    },
    {
      "operacion_uuid": "b95d23fa-59a0-4063-bdb9-346128c7dd05",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-28T02:16:39.851926+00:00",
      "datos": {
        "entrega_id": 518,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "El cliente no estaba en su domicilio",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b0a3c57a55f138667f109a2"
        ],
        "capturado_en": "2026-11-28T02:16:39.851942+00:00"
      }
    }
  ]
}
```

**Respuesta.** HTTP 200 (esperado 200) · 184 ms · traza `3a752344-3f9d-4c14-9b73-d2a3cb7170fc`

```json
{
  "id": 299,
  "lote_uuid": "81b58773-ba0a-4ae8-b2f2-28bc76fb4d0c",
  "dispositivo": "android-flujo-b45bb8",
  "recibido_en": "2026-11-27T20:28:39-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 2,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "2badd633-f313-404f-9a76-5db6432d1e39",
      "tipo": "ubicaciones",
      "estado": "aplicada",
      "duplicada": true,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    },
    {
      "operacion_uuid": "b95d23fa-59a0-4063-bdb9-346128c7dd05",
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
X-Traza-Id: 1e541bc3-021e-4dc6-9931-b2b0e7f0e918
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 53 ms · traza `1e541bc3-021e-4dc6-9931-b2b0e7f0e918`

```json
{
  "datos": [
    {
      "id": 1670,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-001083",
      "mensaje": "El pedido cambió a entrega_fallida.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "1083"
      },
      "creada_en": "2026-11-27T20:28:40-06:00"
    },
    {
      "id": 1668,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-001082",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "1082"
      },
      "creada_en": "2026-11-27T20:28:37-06:00"
    },
    {
      "id": 1663,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-001081",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "1081"
      },
      "creada_en": "2026-11-27T20:28:34-06:00"
    },
    {
      "id": 1629,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-001059",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "1059"
      },
      "creada_en": "2026-11-27T20:00:17-06:00"
    },
    {
      "id": 1621,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-001033",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "1033"
      },
      "creada_en": "2026-11-27T19:59:03-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 63,
    "paginas": 13
  }
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F3-06 · El auditor revisa la entrega · PASA

**Objetivo.** Bitácora y archivos de la entrega.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/entrega/518`

```http
Accept: application/json
X-Traza-Id: 9d3dfacb-2051-425e-9d2d-8a2a04688bc8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 79 ms · traza `9d3dfacb-2051-425e-9d2d-8a2a04688bc8`

```json
{
  "objeto": {
    "tipo": "entrega",
    "id": "518"
  },
  "total": 3,
  "eventos": [
    {
      "fecha": "2026-11-27T20:28:39-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "asignada_en = 2026-11-27T20:28:39.754729-06:00; cambio_entregado = None; capturado_en = None; cerrada_por_usuario_id = None",
      "usuario": {
        "id": 3,
        "nombre": "María José Cedillo Mata"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "518"
      },
      "cambios": [
        {
          "campo": "asignada_en",
          "anterior": null,
          "nuevo": "2026-11-27T20:28:39.754729-06:00"
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
      "fecha": "2026-11-27T20:28:39-06:00",
      "origen": "documentos",
      "accion": "documento_subido",
      "descripcion": "evidencia-flujo3-518.jpg (276 bytes, sha256 7f6025cd8a98…)",
      "usuario": {
        "id": 8,
        "nombre": null
      },
      "entidad": {
        "tipo": "documento",
        "id": "6b0a3c57a55f138667f109a2"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T20:28:40-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "cambio_entregado = 0.0; capturado_en = 2026-11-27T20:16:39.8…(145 caracteres)",
      "usuario": {
        "id": 8,
        "nombre": "Diana Sepúlveda Ibarra"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "518"
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
          "nuevo": "2026-11-27T20:16:39.851942-06:00"
        },
        {
          "campo": "cerrada_por_usuario_id",
          "anterior": null,
          "nuevo": "8"
        },
        {
          "campo": "cierre_en",
          "anterior": null,
          "nuevo": "2026-11-27T20:28:40.105257-06:00"
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
          "nuevo": "[\"6b0a3c57a55f138667f109a2\"]"
        },
        {
          "campo": "evidencia_url",
          "anterior": null,
          "nuevo": "/api/v1/documentos/6b0a3c57a55f138667f109a2"
        },
        {
          "campo": "id_cliente_local",
          "anterior": null,
          "nuevo": "b95d23fa-59a0-4063-bdb9-346128c7dd05"
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
X-Traza-Id: 528c961f-b611-4e27-8ddc-39fdf09e2ff8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 54 ms · traza `528c961f-b611-4e27-8ddc-39fdf09e2ff8`

```json
{
  "datos": [
    {
      "id": 3600,
      "microhub_id": 2,
      "producto_id": 51,
      "tipo": "devolucion_cancelacion",
      "cantidad": 3,
      "existencia_resultante": 52,
      "referencia": {
        "tipo": "pedido",
        "id": "1083"
      },
      "motivo": "Entrega fallida: la mercancía regresa al microhub.",
      "usuario_id": 8,
      "fecha": "2026-11-27T20:28:40-06:00"
    },
    {
      "id": 3599,
      "microhub_id": 2,
      "producto_id": 31,
      "tipo": "devolucion_cancelacion",
      "cantidad": 3,
      "existencia_resultante": 27,
      "referencia": {
        "tipo": "pedido",
        "id": "1083"
      },
      "motivo": "Entrega fallida: la mercancía regresa al microhub.",
      "usuario_id": 8,
      "fecha": "2026-11-27T20:28:40-06:00"
    },
    {
      "id": 3598,
      "microhub_id": 2,
      "producto_id": 51,
      "tipo": "salida_pedido",
      "cantidad": -3,
      "existencia_resultante": 49,
      "referencia": {
        "tipo": "pedido",
        "id": "1083"
      },
      "motivo": null,
      "usuario_id": 9,
      "fecha": "2026-11-27T20:28:38-06:00"
    },
    {
      "id": 3597,
      "microhub_id": 2,
      "producto_id": 31,
      "tipo": "salida_pedido",
      "cantidad": -3,
      "existencia_resultante": 24,
      "referencia": {
        "tipo": "pedido",
        "id": "1083"
      },
      "motivo": null,
      "usuario_id": 9,
      "fecha": "2026-11-27T20:28:38-06:00"
    },
    {
      "id": 3596,
      "microhub_id": 2,
      "producto_id": 31,
      "tipo": "devolucion_cancelacion",
      "cantidad": 10,
      "existencia_resultante": 27,
      "referencia": {
        "tipo": "pedido",
        "id": "1082"
      },
      "motivo": "Cierre del flujo de demostración",
      "usuario_id": 1,
      "fecha": "2026-11-27T20:28:37-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 1217,
    "paginas": 244
  }
}
```

**Evidencia en PostgreSQL.** `SELECT tipo, producto_id, cantidad, existencia_resultante FROM movimiento_inventario WHERE referencia_id = %s ORDER BY id`

```json
[
  {
    "tipo": "salida_pedido",
    "producto_id": 31,
    "cantidad": -3,
    "existencia_resultante": 24
  },
  {
    "tipo": "salida_pedido",
    "producto_id": 51,
    "cantidad": -3,
    "existencia_resultante": 49
  },
  {
    "tipo": "devolucion_cancelacion",
    "producto_id": 31,
    "cantidad": 3,
    "existencia_resultante": 27
  },
  {
    "tipo": "devolucion_cancelacion",
    "producto_id": 51,
    "cantidad": 3,
    "existencia_resultante": 52
  }
]
```

## Servicio reportes · puerto 5123

### F3-08 · Reporte del periodo en CSV · PASA

**Objetivo.** La entrega ya cuenta en los reportes.

**Petición.** `GET http://reportes:5123/api/v1/reportes/pedidos_por_dia/exportar?formato=csv`

```http
Accept: application/json
X-Traza-Id: 2d4fb0b3-c90a-4059-92f8-e59c8d067c1a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 187 ms · traza `2d4fb0b3-c90a-4059-92f8-e59c8d067c1a`

```json
﻿Día,Pedidos,Unidades,Venta,Ticket promedio,Demanda no atendida
2026-11-25,56,282,8032.40,143.44,0
2026-11-26,212,1096,34991.60,165.05,8
2026-11-27,279,1508,47403.50,169.91,9
Total,547,2886,90427.50,165.32,17

```

**Evidencia en PostgreSQL.** `SELECT reporte, formato, filas, left(sha256, 16) AS sha256 FROM reporte_exportacion ORDER BY id DESC LIMIT 1`

```json
[
  {
    "reporte": "pedidos_por_dia",
    "formato": "csv",
    "filas": 3,
    "sha256": "4c64a1887c091acd"
  }
]
```
