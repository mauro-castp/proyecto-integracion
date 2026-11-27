# Procesos integrales de principio a fin


Generado el 2026-11-27 07:24 contra los servicios en ejecución. 40 de 40 casos pasan.

## Servicio planeacion · puerto 5106

### F1-01 · Escritorio (XML): el planeador registra una ubicación candidata · PASA

**Objetivo.** Planeación de ubicación.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos`

```http
Accept: application/xml
X-Traza-Id: b45e33c3-7070-477b-9a0e-5ae1981870ea
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><candidato_nuevo xmlns="urn:microhubs:v1"><clave>********</clave><nombre>Ubicación del flujo E83EF</nombre><latitud>25.760195</latitud><longitud>-100.370891</longitud><renta_estimada>15000.00</renta_estimada><nomina_estimada>36000.00</nomina_estimada><servicios_estimados>6000.00</servicios_estimados><otros_costos>4000.00</otros_costos><superficie_m2>100</superficie_m2><capacidad_fisica>120</capacidad_fisica><accesibilidad_vial>8</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km></candidato_nuevo>
```

**Respuesta.** HTTP 201 (esperado 201) · 128 ms · traza `b45e33c3-7070-477b-9a0e-5ae1981870ea`

```xml
<?xml version='1.0' encoding='utf-8'?>
<candidato xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>310</id><clave>FL-E83EF</clave><nombre>Ubicación del flujo E83EF</nombre><latitud>25.760195</latitud><longitud>-100.370891</longitud><renta_estimada>15000.00</renta_estimada><nomina_estimada>36000.00</nomina_estimada><servicios_estimados>6000.00</servicios_estimados><otros_costos>4000.00</otros_costos><costo_fijo>61000.00</costo_fijo><superficie_m2>100</superficie_m2><capacidad_fisica>120</capacidad_fisica><accesibilidad_vial>8</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato>
```

**Evidencia en PostgreSQL.** `SELECT id, clave, nombre, costo_fijo, decision FROM ubicacion_candidata WHERE clave = %s`

```json
[
  {
    "id": 310,
    "clave": "FL-E83EF",
    "nombre": "Ubicación del flujo E83EF",
    "costo_fijo": "61000.00",
    "decision": "pendiente"
  }
]
```

### F1-02 · El planeador simula la operación de la candidata · PASA

**Objetivo.** Capacidad, utilización y decisión sugerida (MongoDB).

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/310/simular`

```http
Accept: application/json
X-Traza-Id: ce2b6981-cf6f-436e-847f-6f8e36aa5d54
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

**Respuesta.** HTTP 200 (esperado 200) · 263 ms · traza `ce2b6981-cf6f-436e-847f-6f8e36aa5d54`

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
X-Traza-Id: 0bc4111d-2200-4ce2-8aab-a7b9e05502f4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "candidato_id": 310,
  "pedidos_dia": 100,
  "ticket": 180,
  "margen_bruto": 0.3,
  "costos_fijos": 61000,
  "costo_variable_pedido": 22
}
```

**Respuesta.** HTTP 200 (esperado 200) · 43 ms · traza `0bc4111d-2200-4ce2-8aab-a7b9e05502f4`

```json
{
  "id": null,
  "nombre": null,
  "objeto": {
    "tipo": "candidato",
    "id": 310,
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

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/310/decision`

```http
Accept: application/json
X-Traza-Id: e35370b9-0037-452d-bd22-e143c05b0aef
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aceptado",
  "motivo": "Cubre la zona del cliente y la demanda esperada supera el equilibrio."
}
```

**Respuesta.** HTTP 200 (esperado 200) · 65 ms · traza `e35370b9-0037-452d-bd22-e143c05b0aef`

```json
{
  "id": 310,
  "clave": "********",
  "nombre": "Ubicación del flujo E83EF",
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
X-Traza-Id: 2aaaebde-a27b-40c9-8f6f-77808907cc7f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "clave": "********",
  "nombre": "Microhub E83EF",
  "direccion": "Ubicación aprobada en planeación",
  "latitud": 25.760195,
  "longitud": -100.370891,
  "radio_km": 1.5,
  "capacidad_turno": 120
}
```

**Respuesta.** HTTP 201 (esperado 201) · 107 ms · traza `2aaaebde-a27b-40c9-8f6f-77808907cc7f`

```json
{
  "id": 17,
  "clave": "********",
  "nombre": "Microhub E83EF",
  "latitud": 25.760195,
  "longitud": -100.370891,
  "radio_km": 1.5,
  "estatus": "activo"
}
```

## Servicio capacidad · puerto 5117

### F1-06 · Asignar personal al microhub · PASA

**Objetivo.** Operadores, repartidores y capacidad física.

**Petición.** `PUT http://capacidad:5117/api/v1/capacidad/recursos/17`

```http
Accept: application/json
X-Traza-Id: 96df99cf-3f1e-4e95-9f88-958bd9f9154a
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

**Respuesta.** HTTP 200 (esperado 200) · 215 ms · traza `96df99cf-3f1e-4e95-9f88-958bd9f9154a`

```json
{
  "microhub": {
    "id": 17,
    "nombre": "Microhub E83EF"
  },
  "operadores": 2,
  "repartidores": 2,
  "capacidad_fisica": 120,
  "actualizado_en": "2026-11-27T01:24:09-06:00"
}
```

## Servicio usuarios · puerto 5102

### F1-07 · Crear la cuenta del operador · PASA

**Objetivo.** Cuenta nueva con su perfil y su microhub.

**Petición.** `POST http://usuarios:5102/api/v1/usuarios`

```http
Accept: application/json
X-Traza-Id: 23cbc952-8e8e-4d8e-936d-7ea74de23a55
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Operador",
  "apellidos": "E83EF",
  "correo": "operador.e83ef@ejemplo.mx",
  "clave": "********",
  "rol": "operador",
  "microhub_id": 17
}
```

**Respuesta.** HTTP 201 (esperado 201) · 192 ms · traza `23cbc952-8e8e-4d8e-936d-7ea74de23a55`

```json
{
  "id": 71,
  "nombre": "Operador",
  "apellidos": "E83EF",
  "correo": "operador.e83ef@ejemplo.mx",
  "telefono": null,
  "rol": "operador",
  "microhub": {
    "id": 17,
    "clave": "********",
    "nombre": "Microhub E83EF"
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
X-Traza-Id: 95f0cb41-4c9b-4b95-8f15-b85f7df6de06
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "origen_microhub_id": 1,
  "destino_microhub_id": 17,
  "producto_id": 31,
  "cantidad": 12,
  "motivo": "Inventario inicial del microhub nuevo",
  "operacion_uuid": "44d2b0db-eaf6-49f2-a786-ed6a886da2b0"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 107 ms · traza `95f0cb41-4c9b-4b95-8f15-b85f7df6de06`

```json
{
  "producto_id": 31,
  "cantidad": 12,
  "duplicado": false,
  "origen": {
    "microhub_id": 1,
    "existencia": 201,
    "movimiento_id": 2926
  },
  "destino": {
    "microhub_id": 17,
    "existencia": 12,
    "movimiento_id": 2927
  }
}
```

### F1-08b · Surtir el microhub nuevo · PASA

**Objetivo.** Transferencia atómica desde MH-01.

**Petición.** `POST http://inventario:5111/api/v1/inventario/transferencias`

```http
Accept: application/json
X-Traza-Id: faa864de-044a-43ea-b6f7-3bf36e67f160
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "origen_microhub_id": 1,
  "destino_microhub_id": 17,
  "producto_id": 18,
  "cantidad": 12,
  "motivo": "Inventario inicial del microhub nuevo",
  "operacion_uuid": "6ca73f12-2305-4d9b-b1ae-e0a4651f0051"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 110 ms · traza `faa864de-044a-43ea-b6f7-3bf36e67f160`

```json
{
  "producto_id": 18,
  "cantidad": 12,
  "duplicado": false,
  "origen": {
    "microhub_id": 1,
    "existencia": 62,
    "movimiento_id": 2928
  },
  "destino": {
    "microhub_id": 17,
    "existencia": 12,
    "movimiento_id": 2929
  }
}
```

## Servicio pedidos · puerto 5104

### F1-09 · Android (JSON): el cliente hace su pedido · PASA

**Objetivo.** El motor lo asigna al microhub más cercano que tiene todo: el nuevo.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: 446d5694-3d57-49c2-a066-8d2fd26fce50
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
  "operacion_uuid": "44496cdc-3d19-4b65-9965-efd832f4a626"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 265 ms · traza `446d5694-3d57-49c2-a066-8d2fd26fce50`

```json
{
  "id": 760,
  "folio": "PED-20261127-000760",
  "estado": "asignado",
  "zona_id": 3,
  "microhub_id": 17,
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
    "microhub_ganador_id": 17,
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

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/760/estado`

```http
Accept: application/json
X-Traza-Id: 65ad93af-aba0-4299-92b3-b3d5fd46843e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MSIs…(296 caracteres)
Content-Type: application/json
```

```json
{
  "estado": "en_preparacion"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 96 ms · traza `65ad93af-aba0-4299-92b3-b3d5fd46843e`

```json
{
  "id": 760,
  "folio": "PED-20261127-000760",
  "estado": "en_preparacion",
  "zona": {
    "id": 3,
    "nombre": "Paseo de San Bernabé"
  },
  "microhub_id": 17,
  "total": 306.0,
  "creado_en": "2026-11-27T01:24:10-06:00"
}
```

### F1-11 · El operador lo marca listo · PASA

**Objetivo.** Queda disponible para despacho.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/760/listo`

```http
Accept: application/json
X-Traza-Id: 5b66cfae-1d96-41b1-b2c6-1e968320087b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MSIs…(296 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 200 (esperado 200) · 67 ms · traza `5b66cfae-1d96-41b1-b2c6-1e968320087b`

```json
{
  "id": 760,
  "estado": "en_preparacion",
  "listo_en": "2026-11-27T01:24:10-06:00"
}
```

## Servicio rutas · puerto 5118

### F1-12 · Proponer la ruta de despacho · PASA

**Objetivo.** Agrupa, asigna repartidor y ordena las paradas (algoritmo de rutas).

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/json
X-Traza-Id: f4be6e82-13af-4282-b969-92bbde21988f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MSIs…(296 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 17,
  "pedido_ids": [
    760
  ],
  "repartidor_ids": [
    7
  ],
  "metodo": "automatico",
  "guardar": true
}
```

**Respuesta.** HTTP 201 (esperado 201) · 225 ms · traza `f4be6e82-13af-4282-b969-92bbde21988f`

```json
{
  "id": 137,
  "estado": "propuesto",
  "version": 1,
  "microhub": {
    "id": 17,
    "nombre": "Microhub E83EF"
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
            "id": 760,
            "folio": "PED-20261127-000760"
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
X-Traza-Id: b342293b-73ae-41b8-985d-6738b8448f28
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MSIs…(296 caracteres)
Content-Type: application/json
```

```json
{
  "pedido_id": 760,
  "repartidor_id": 7,
  "orden_parada": 1
}
```

**Respuesta.** HTTP 201 (esperado 201) · 67 ms · traza `b342293b-73ae-41b8-985d-6738b8448f28`

```json
{
  "entrega_id": 429,
  "pedido_id": 760,
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
    "referencia_id": "429"
  }
]
```

### F1-14 · Android: el repartidor ve su parada · PASA

**Objetivo.** Sesión validada en Redis.

**Petición.** `GET http://entregas:5105/api/v1/entregas/mias?por_pagina=50`

```http
Accept: application/json
X-Traza-Id: 5d8e26fa-7a2f-43cb-b742-afbd64fb4c15
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 97 ms · traza `5d8e26fa-7a2f-43cb-b742-afbd64fb4c15`

```json
{
  "datos": [
    {
      "id": 429,
      "pedido_id": 760,
      "folio": "PED-20261127-000760",
      "estado_pedido": "en_ruta",
      "orden_parada": 1,
      "direccion": "Nogal 1440, Paseo de San Bernabé",
      "zona": "Paseo de San Bernabé",
      "distancia_km": null,
      "minutos_estimados": null,
      "total": 306.0
    },
    {
      "id": 410,
      "pedido_id": 736,
      "folio": "PED-20261127-000736",
      "estado_pedido": "en_ruta",
      "orden_parada": 4,
      "direccion": "Nogal 1469, Paseo de San Bernabé",
      "zona": "Paseo de San Bernabé",
      "distancia_km": 1.37,
      "minutos_estimados": 28.0,
      "total": 208.0
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
    "total": 3,
    "paginas": 1
  }
}
```

**Evidencia en Redis.** `SCARD auth:sesion:7`

```json
[
  {
    "comando": "SCARD auth:sesion:7",
    "valor": 30
  }
]
```

## Servicio seguimiento · puerto 5110

### F1-15 · El repartidor envía su recorrido · PASA

**Objetivo.** Puntos GPS en MongoDB (2dsphere).

**Petición.** `POST http://seguimiento:5110/api/v1/seguimiento/429/ubicaciones`

```http
Accept: application/json
X-Traza-Id: 395859b5-8c23-4e7b-8dbb-dc5dfacf1837
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "puntos": [
    {
      "latitud": 25.760195,
      "longitud": -100.370891,
      "capturado_en": "2026-11-27T07:20:11.089542+00:00"
    },
    {
      "latitud": 25.759995,
      "longitud": -100.371091,
      "capturado_en": "2026-11-27T07:23:11.089577+00:00"
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 98 ms · traza `395859b5-8c23-4e7b-8dbb-dc5dfacf1837`

```json
{
  "recibidos": 2
}
```

## Servicio documentos · puerto 5107

### F1-16 · La foto de evidencia queda en el almacén · PASA

**Objetivo.** En la base solo sus datos; se descarga con un enlace firmado.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b09301b7d5722bf715047fe/enlace`

```http
Accept: application/json
X-Traza-Id: 75b305b5-753f-49a1-a2e7-a46215d6f332
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 41 ms · traza `75b305b5-753f-49a1-a2e7-a46215d6f332`

```json
{
  "id": "6b09301b7d5722bf715047fe",
  "nombre": "evidencia-flujo1-E83EF.jpg",
  "url_firmada": "http://documentos:5107/api/v1/documentos/descarga?k=document…(208 caracteres)",
  "metodo": "GET",
  "segundos": 300,
  "expira_en": "2026-11-27T01:29:11-06:00"
}
```

**Evidencia en MongoDB.** `db.documentos.findOne({_id}) sin contenido`

```json
{
  "_id": "6b09301b7d5722bf715047fe",
  "nombre": "evidencia-flujo1-E83EF.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "429"
  },
  "subido_por": 7,
  "creado_en": "2026-11-27 07:24:11.232000+00:00",
  "ruta": "documentos/2026/11/6b09301b7d5722bf715047fe.jpg",
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

**Petición.** `POST http://entregas:5105/api/v1/entregas/429/resultado`

```http
Accept: application/json
X-Traza-Id: 8b9d4f6e-8f87-4dab-8f3e-41e0a495b0f1
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
    "6b09301b7d5722bf715047fe"
  ],
  "capturado_en": "2026-11-27T07:24:11.623322+00:00",
  "id_cliente_local": "064f512c-6bb7-4dd9-93ea-06dbb188bc47"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 120 ms · traza `8b9d4f6e-8f87-4dab-8f3e-41e0a495b0f1`

```json
{
  "entrega_id": 429,
  "pedido_id": 760,
  "estado_pedido": "entregado",
  "cerrado_en": "2026-11-27T01:24:11-06:00",
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
    "usuario_id": 71,
    "proceso": null
  },
  {
    "estado_anterior": "en_preparacion",
    "estado_nuevo": "en_ruta",
    "usuario_id": 71,
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
X-Traza-Id: 9bf5c5d8-e1ec-4c40-bb6e-239ba9bfca37
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 66 ms · traza `9bf5c5d8-e1ec-4c40-bb6e-239ba9bfca37`

```json
{
  "datos": [
    {
      "id": 1237,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000760",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "760"
      },
      "creada_en": "2026-11-27T01:24:11-06:00"
    },
    {
      "id": 1211,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000750",
      "mensaje": "El pedido cambió a entrega_fallida.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "750"
      },
      "creada_en": "2026-11-27T01:19:33-06:00"
    },
    {
      "id": 1205,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000746",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "746"
      },
      "creada_en": "2026-11-27T01:17:25-06:00"
    },
    {
      "id": 1204,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000744",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "744"
      },
      "creada_en": "2026-11-27T01:17:24-06:00"
    },
    {
      "id": 1173,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000741",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "741"
      },
      "creada_en": "2026-11-27T01:16:03-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 37,
    "paginas": 8
  }
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F1-19 · El auditor reconstruye la historia del pedido · PASA

**Objetivo.** Bitácora, estados, inventario y archivos en una línea de tiempo.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/pedido/760`

```http
Accept: application/json
X-Traza-Id: e447e917-a3ee-4f58-b13c-b3716ff0de53
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 113 ms · traza `e447e917-a3ee-4f58-b13c-b3716ff0de53`

```json
{
  "objeto": {
    "tipo": "pedido",
    "id": "760"
  },
  "total": 15,
  "eventos": [
    {
      "fecha": "2026-11-27T01:24:10-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "actualizado_en = 2026-11-27T01:24:10.31687-06:00; asignado_en = None; cerrado_en = None; cliente_id = 1",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "760"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": null,
          "nuevo": "2026-11-27T01:24:10.31687-06:00"
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
          "nuevo": "2026-11-27T01:24:10.31687-06:00"
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
          "nuevo": "PED-20261127-000760"
        },
        {
          "campo": "id",
          "anterior": null,
          "nuevo": "760"
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
      "fecha": "2026-11-27T01:24:10-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "asignado_en = 2026-11-27T01:24:10.31687-06:00; estado: creado → asignado; microhub_id = 17",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "760"
      },
      "cambios": [
        {
          "campo": "asignado_en",
          "anterior": null,
          "nuevo": "2026-11-27T01:24:10.31687-06:00"
        },
        {
          "campo": "estado",
          "anterior": "creado",
          "nuevo": "asignado"
        },
        {
          "campo": "microhub_id",
          "anterior": null,
          "nuevo": "17"
        }
      ]
    },
    {
      "fecha": "2026-11-27T01:24:10-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "nuevo → creado",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "760"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T01:24:10-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "creado → asignado",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "760"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T01:24:10-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -3 de producto 18 en microhub 17 (existencia 9)",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "17-18"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T01:24:10-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -3 de producto 31 en microhub 17 (existencia 9)",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "17-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T01:24:10-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-27T01:24:10.31687-06:00 → 2026-11-27T01:24:10.531697-06:00; estado: asignado → en_preparacion",
      "usuario": {
        "id": 71,
        "nombre": "Operador E83EF"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "760"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-27T01:24:10.31687-06:00",
          "nuevo": "2026-11-27T01:24:10.531697-06:00"
        },
        {
          "campo": "estado",
          "anterior": "asignado",
          "nuevo": "en_preparacion"
        }
      ]
    },
    {
      "fecha": "2026-11-27T01:24:10-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "asignado → en_preparacion",
      "usuario": {
        "id": 71,
        "nombre": "Operador E83EF"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "760"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T01:24:10-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "listo_en = 2026-11-27T01:24:10.629217-06:00",
      "usuario": {
        "id": 71,
        "nombre": "Operador E83EF"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "760"
      },
      "cambios": [
        {
          "campo": "listo_en",
          "anterior": null,
          "nuevo": "2026-11-27T01:24:10.629217-06:00"
        }
      ]
    },
    {
      "fecha": "2026-11-27T01:24:10-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "asignada_en = 2026-11-27T01:24:10.916668-06:00; cambio_entregado = None; capturado_en = None; cerrada_por_usuario_id = None",
      "usuario": {
        "id": 71,
        "nombre": "Operador E83EF"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "429"
      },
      "cambios": [
        {
          "campo": "asignada_en",
          "anterior": null,
          "nuevo": "2026-11-27T01:24:10.916668-06:00"
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
      "fecha": "2026-11-27T01:24:10-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-27T01:24:10.531697-06:00 → 2026-11-27T01:24:10.916668-06:00; estado: en_preparacion → en_ruta",
      "usuario": {
        "id": 71,
        "nombre": "Operador E83EF"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "760"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-27T01:24:10.531697-06:00",
          "nuevo": "2026-11-27T01:24:10.916668-06:00"
        },
        {
          "campo": "estado",
          "anterior": "en_preparacion",
          "nuevo": "en_ruta"
        }
      ]
    },
    {
      "fecha": "2026-11-27T01:24:10-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "en_preparacion → en_ruta",
      "usuario": {
        "id": 71,
        "nombre": "Operador E83EF"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "760"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T01:24:11-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "cambio_entregado = 0.0; capturado_en = 2026-11-27T01:24:11.6…(145 caracteres)",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "429"
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
          "nuevo": "2026-11-27T01:24:11.623322-06:00"
        },
        {
          "campo": "cerrada_por_usuario_id",
          "anterior": null,
          "nuevo": "7"
        },
        {
          "campo": "cierre_en",
          "anterior": null,
          "nuevo": "2026-11-27T01:24:11.674131-06:00"
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
          "nuevo": "[\"6b09301b7d5722bf715047fe\"]"
        },
        {
          "campo": "evidencia_url",
          "anterior": null,
          "nuevo": "/api/v1/documentos/6b09301b7d5722bf715047fe"
        },
        {
          "campo": "id_cliente_local",
          "anterior": null,
          "nuevo": "064f512c-6bb7-4dd9-93ea-06dbb188bc47"
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
      "fecha": "2026-11-27T01:24:11-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-27T01:24:10.916668-06:00 → 2026-11-2…(159 caracteres)",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "760"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-27T01:24:10.916668-06:00",
          "nuevo": "2026-11-27T01:24:11.674131-06:00"
        },
        {
          "campo": "cerrado_en",
          "anterior": null,
          "nuevo": "2026-11-27T01:24:11.674131-06:00"
        },
        {
          "campo": "estado",
          "anterior": "en_ruta",
          "nuevo": "entregado"
        }
      ]
    },
    {
      "fecha": "2026-11-27T01:24:11-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "en_ruta → entregado",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "760"
      },
      "cambios": []
    }
  ]
}
```

## Servicio reportes · puerto 5123

### F1-20 · Visualización: el microhub nuevo ya aparece en la comparación · PASA

**Objetivo.** Datos listos para Highcharts.

**Petición.** `GET http://reportes:5123/api/v1/reportes/comparacion_microhubs/grafica?microhub_id=17`

```http
Accept: application/json
X-Traza-Id: ad406587-4367-4c34-b742-c88da8ef19fc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 150 ms · traza `ad406587-4367-4c34-b742-c88da8ef19fc`

```json
{
  "reporte": "comparacion_microhubs",
  "titulo": "Comparación entre microhubs",
  "tipo": "column",
  "unidad": "pedidos / MXN",
  "categorias": [
    "Microhub E83EF"
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

**Petición.** `DELETE http://microhubs:5109/api/v1/microhubs/17`

```http
Accept: application/json
X-Traza-Id: 34118111-8094-42bb-85c1-b8f56426ec8e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 54 ms · traza `34118111-8094-42bb-85c1-b8f56426ec8e`

```json
(sin cuerpo)
```

## Servicio pedidos · puerto 5104

### F2-01 · Android: un cliente compra y el inventario baja · PASA

**Objetivo.** El motor descuenta inventario en la misma transacción.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: 3fbd9ad6-1a41-4e2a-b838-ca45100a449d
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
  "operacion_uuid": "eeecbefc-e7e5-4752-948e-fcfd0cb84ecb"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 312 ms · traza `3fbd9ad6-1a41-4e2a-b838-ca45100a449d`

```json
{
  "id": 761,
  "folio": "PED-20261127-000761",
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
    "existencia_resultante": 36
  }
]
```

## Servicio inventario · puerto 5111

### F2-02 · El operador fija el mínimo y nace la alerta · PASA

**Objetivo.** El trigger avisa del faltante.

**Petición.** `PATCH http://inventario:5111/api/v1/inventario/1/31/minimo`

```http
Accept: application/json
X-Traza-Id: 07e67a5f-facc-4065-86c8-9a7d70c2c64f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "minimo": 211
}
```

**Respuesta.** HTTP 200 (esperado 200) · 284 ms · traza `07e67a5f-facc-4065-86c8-9a7d70c2c64f`

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
  "existencia": 201,
  "minimo": 211,
  "reservado": 0,
  "disponible": 201,
  "estado": "bajo_minimo",
  "actualizado_en": "2026-11-27T01:24:13-06:00"
}
```

### F2-03 · La alerta de faltante · PASA

**Objetivo.** Qué producto, cuánto falta y qué tan grave es.

**Petición.** `GET http://inventario:5111/api/v1/inventario/alertas?microhub_id=1&por_pagina=100`

```http
Accept: application/json
X-Traza-Id: 5b549b83-619f-4b27-8ac4-0deef734d21f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 107 ms · traza `5b549b83-619f-4b27-8ac4-0deef734d21f`

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
      "existencia": 201,
      "minimo": 211,
      "disponible": 201,
      "faltante": 10,
      "severidad": "baja"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 8,
        "clave_interna": "AB-008",
        "nombre": "Pasta para sopa surtida"
      },
      "existencia": 6,
      "minimo": 10,
      "disponible": 6,
      "faltante": 4,
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
X-Traza-Id: daac1d81-5d73-42b8-8736-331e7e577d45
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

**Respuesta.** HTTP 201 (esperado 201) · 97 ms · traza `daac1d81-5d73-42b8-8736-331e7e577d45`

```json
{
  "id": 90,
  "folio": "SC-20261127-000090",
  "microhub_id": 1,
  "estado": "pendiente",
  "motivo": "Faltante detectado por el sistema",
  "solicitada_por": 2,
  "decidida_por": null,
  "decision_motivo": null,
  "decidida_en": null,
  "creada_en": "2026-11-27T01:24:14-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/90/decision`

```http
Accept: application/json
X-Traza-Id: 6d07442a-1671-4c74-8bab-55b5f20f11f7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aprobada",
  "motivo": "Con presupuesto"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 99 ms · traza `6d07442a-1671-4c74-8bab-55b5f20f11f7`

```json
{
  "id": 90,
  "folio": "SC-20261127-000090",
  "microhub_id": 1,
  "estado": "aprobada",
  "motivo": "Faltante detectado por el sistema",
  "solicitada_por": 2,
  "decidida_por": 1,
  "decision_motivo": "Con presupuesto",
  "decidida_en": "2026-11-27T01:24:14-06:00",
  "creada_en": "2026-11-27T01:24:14-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/90/ordenar`

```http
Accept: application/json
X-Traza-Id: 8bb04802-5715-4755-917f-1a1ab3e7e7ef
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 201 (esperado 201) · 374 ms · traza `8bb04802-5715-4755-917f-1a1ab3e7e7ef`

```json
{
  "solicitud_id": 90,
  "ordenes": [
    {
      "id": 57,
      "folio": "OC-20261127-000057",
      "solicitud_id": 90,
      "proveedor": {
        "id": 1,
        "nombre": "Abarrotes del Norte"
      },
      "microhub_id": 1,
      "estado": "emitida",
      "fecha_esperada": "2026-11-29",
      "total": 4060.0,
      "creada_en": "2026-11-27T01:24:14-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/57/recepcion`

```http
Accept: application/json
X-Traza-Id: 6035af1c-9bea-4013-afc7-12dd38fa074a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "operacion_uuid": "3dc7c6d3-e9a9-4039-9469-437cb813d5f4",
  "nota": "Completo",
  "lineas": [
    {
      "producto_id": 31,
      "cantidad": 100
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 282 ms · traza `6035af1c-9bea-4013-afc7-12dd38fa074a`

```json
{
  "orden": {
    "id": 57,
    "folio": "OC-20261127-000057",
    "solicitud_id": 90,
    "proveedor": {
      "id": 1,
      "nombre": "Abarrotes del Norte"
    },
    "microhub_id": 1,
    "estado": "recibida",
    "fecha_esperada": "2026-11-29",
    "total": 4060.0,
    "creada_en": "2026-11-27T01:24:14-06:00",
    "cerrada_en": "2026-11-27T01:24:14-06:00",
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
    "existencia": 301,
    "minimo": 211
  }
]
```

## Servicio documentos · puerto 5107

### F2-08 · La remisión firmada queda en el almacén · PASA

**Objetivo.** Archivo con enlace firmado.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b09301f7d5722bf71504803/enlace`

```http
Accept: application/json
X-Traza-Id: 87143f18-965d-4d15-b409-93a073dae9f0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 27 ms · traza `87143f18-965d-4d15-b409-93a073dae9f0`

```json
{
  "id": "6b09301f7d5722bf71504803",
  "nombre": "remision-57.jpg",
  "url_firmada": "http://documentos:5107/api/v1/documentos/descarga?k=document…(197 caracteres)",
  "metodo": "GET",
  "segundos": 300,
  "expira_en": "2026-11-27T01:29:15-06:00"
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F2-09 · Trazabilidad del producto en el microhub · PASA

**Objetivo.** Salida por pedido y recepción por orden.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/inventario?microhub_id=1&producto_id=31`

```http
Accept: application/json
X-Traza-Id: db09884c-7304-4870-aa89-0b91002203f6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 46 ms · traza `db09884c-7304-4870-aa89-0b91002203f6`

```json
{
  "objeto": {
    "tipo": "inventario",
    "id": "1-31"
  },
  "total": 16,
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
X-Traza-Id: db9602c9-aed3-4e93-9770-683c95faaaff
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 191 ms · traza `db9602c9-aed3-4e93-9770-683c95faaaff`

```json
﻿Microhub,Producto,Existencia,Mínimo,Disponible,Faltante,Severidad
Microhub San Bernabé Centro,Pasta para sopa surtida,6,10,6,4,baja
Microhub San Bernabé Centro,Limpiador multiusos,8,8,8,0,baja
Total,,,,,4,

```

## Servicio pedidos · puerto 5104

### F3-01 · El cliente hace un pedido · PASA

**Objetivo.** Punto de partida del recorrido.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: 38a1d4da-2afa-4ad7-be57-01f44e89392e
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

**Respuesta.** HTTP 201 (esperado 201) · 255 ms · traza `38a1d4da-2afa-4ad7-be57-01f44e89392e`

```json
{
  "id": 762,
  "folio": "PED-20261127-000762",
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
X-Traza-Id: 6d6b5a0a-4ec5-4727-b6d7-744e8fb95a6e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
Content-Type: application/json
```

```json
{
  "pedido_id": 762,
  "repartidor_id": 7
}
```

**Respuesta.** HTTP 201 (esperado 201) · 68 ms · traza `6d6b5a0a-4ec5-4727-b6d7-744e8fb95a6e`

```json
{
  "entrega_id": 430,
  "pedido_id": 762,
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
X-Traza-Id: 159f7ec6-e9ba-4502-8834-9db8f597e0e2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "28ba36fe-0da0-46be-b149-8ce298955e9e",
  "dispositivo": "android-flujo-d2328a",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "a07b5692-027f-451d-8f6f-0754aa581288",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-27T07:04:17.791621+00:00",
      "datos": {
        "entrega_id": 430,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-27T07:04:17.791649+00:00"
          },
          {
            "latitud": 25.7491,
            "longitud": -100.3611,
            "capturado_en": "2026-11-27T07:09:17.791663+00:00"
          }
        ]
      }
    },
    {
      "operacion_uuid": "f514f5d5-9a70-4cf1-b8e5-e4f28361870d",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-27T07:12:17.791687+00:00",
      "datos": {
        "entrega_id": 430,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "El cliente no estaba en su domicilio",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b093021f700eb3849c5ad93"
        ],
        "capturado_en": "2026-11-27T07:12:17.791693+00:00"
      }
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 556 ms · traza `159f7ec6-e9ba-4502-8834-9db8f597e0e2`

```json
{
  "id": 246,
  "lote_uuid": "28ba36fe-0da0-46be-b149-8ce298955e9e",
  "dispositivo": "android-flujo-d2328a",
  "recibido_en": "2026-11-27T01:24:17-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 0,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "a07b5692-027f-451d-8f6f-0754aa581288",
      "tipo": "ubicaciones",
      "estado": "aplicada",
      "duplicada": false,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    },
    {
      "operacion_uuid": "f514f5d5-9a70-4cf1-b8e5-e4f28361870d",
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
    "creada_en": "2026-11-27 01:04:17.791621-06:00"
  },
  {
    "tipo": "entrega_resultado",
    "estado": "aplicada",
    "intentos": 1,
    "creada_en": "2026-11-27 01:12:17.791687-06:00"
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
X-Traza-Id: f6a28c00-1625-42a1-8711-3b0f67d83c73
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "28ba36fe-0da0-46be-b149-8ce298955e9e",
  "dispositivo": "android-flujo-d2328a",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "a07b5692-027f-451d-8f6f-0754aa581288",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-27T07:04:17.791621+00:00",
      "datos": {
        "entrega_id": 430,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-27T07:04:17.791649+00:00"
          },
          {
            "latitud": 25.7491,
            "longitud": -100.3611,
            "capturado_en": "2026-11-27T07:09:17.791663+00:00"
          }
        ]
      }
    },
    {
      "operacion_uuid": "f514f5d5-9a70-4cf1-b8e5-e4f28361870d",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-27T07:12:17.791687+00:00",
      "datos": {
        "entrega_id": 430,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "El cliente no estaba en su domicilio",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b093021f700eb3849c5ad93"
        ],
        "capturado_en": "2026-11-27T07:12:17.791693+00:00"
      }
    }
  ]
}
```

**Respuesta.** HTTP 200 (esperado 200) · 239 ms · traza `f6a28c00-1625-42a1-8711-3b0f67d83c73`

```json
{
  "id": 246,
  "lote_uuid": "28ba36fe-0da0-46be-b149-8ce298955e9e",
  "dispositivo": "android-flujo-d2328a",
  "recibido_en": "2026-11-27T01:24:17-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 2,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "a07b5692-027f-451d-8f6f-0754aa581288",
      "tipo": "ubicaciones",
      "estado": "aplicada",
      "duplicada": true,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    },
    {
      "operacion_uuid": "f514f5d5-9a70-4cf1-b8e5-e4f28361870d",
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
X-Traza-Id: b3ff4f7b-65fb-431c-a4d4-fcd8858528c1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 45 ms · traza `b3ff4f7b-65fb-431c-a4d4-fcd8858528c1`

```json
{
  "datos": [
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
    },
    {
      "id": 1242,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000761",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "761"
      },
      "creada_en": "2026-11-27T01:24:15-06:00"
    },
    {
      "id": 1237,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000760",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "760"
      },
      "creada_en": "2026-11-27T01:24:11-06:00"
    },
    {
      "id": 1211,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000750",
      "mensaje": "El pedido cambió a entrega_fallida.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "750"
      },
      "creada_en": "2026-11-27T01:19:33-06:00"
    },
    {
      "id": 1205,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000746",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "746"
      },
      "creada_en": "2026-11-27T01:17:25-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 39,
    "paginas": 8
  }
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F3-06 · El auditor revisa la entrega · PASA

**Objetivo.** Bitácora y archivos de la entrega.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/entrega/430`

```http
Accept: application/json
X-Traza-Id: fd859ab1-8119-4abc-977b-528ef5fd0be4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 57 ms · traza `fd859ab1-8119-4abc-977b-528ef5fd0be4`

```json
{
  "objeto": {
    "tipo": "entrega",
    "id": "430"
  },
  "total": 3,
  "eventos": [
    {
      "fecha": "2026-11-27T01:24:17-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "asignada_en = 2026-11-27T01:24:17.664749-06:00; cambio_entregado = None; capturado_en = None; cerrada_por_usuario_id = None",
      "usuario": {
        "id": 3,
        "nombre": "María José Cedillo Mata"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "430"
      },
      "cambios": [
        {
          "campo": "asignada_en",
          "anterior": null,
          "nuevo": "2026-11-27T01:24:17.664749-06:00"
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
      "fecha": "2026-11-27T01:24:17-06:00",
      "origen": "documentos",
      "accion": "documento_subido",
      "descripcion": "evidencia-flujo3-430.jpg (276 bytes, sha256 7f6025cd8a98…)",
      "usuario": {
        "id": 7,
        "nombre": null
      },
      "entidad": {
        "tipo": "documento",
        "id": "6b093021f700eb3849c5ad93"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T01:24:18-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "cambio_entregado = 0.0; capturado_en = 2026-11-27T01:12:17.7…(145 caracteres)",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "430"
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
          "nuevo": "2026-11-27T01:12:17.791693-06:00"
        },
        {
          "campo": "cerrada_por_usuario_id",
          "anterior": null,
          "nuevo": "7"
        },
        {
          "campo": "cierre_en",
          "anterior": null,
          "nuevo": "2026-11-27T01:24:18.154547-06:00"
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
          "nuevo": "[\"6b093021f700eb3849c5ad93\"]"
        },
        {
          "campo": "evidencia_url",
          "anterior": null,
          "nuevo": "/api/v1/documentos/6b093021f700eb3849c5ad93"
        },
        {
          "campo": "id_cliente_local",
          "anterior": null,
          "nuevo": "f514f5d5-9a70-4cf1-b8e5-e4f28361870d"
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
X-Traza-Id: 9caa6b58-da02-4a9e-b87f-ae9443f37824
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 55 ms · traza `9caa6b58-da02-4a9e-b87f-ae9443f37824`

```json
{
  "datos": [
    {
      "id": 2938,
      "microhub_id": 2,
      "producto_id": 51,
      "tipo": "devolucion_cancelacion",
      "cantidad": 3,
      "existencia_resultante": 58,
      "referencia": {
        "tipo": "pedido",
        "id": "762"
      },
      "motivo": "Entrega fallida: la mercancía regresa al microhub.",
      "usuario_id": 7,
      "fecha": "2026-11-27T01:24:18-06:00"
    },
    {
      "id": 2937,
      "microhub_id": 2,
      "producto_id": 32,
      "tipo": "devolucion_cancelacion",
      "cantidad": 3,
      "existencia_resultante": 11,
      "referencia": {
        "tipo": "pedido",
        "id": "762"
      },
      "motivo": "Entrega fallida: la mercancía regresa al microhub.",
      "usuario_id": 7,
      "fecha": "2026-11-27T01:24:18-06:00"
    },
    {
      "id": 2936,
      "microhub_id": 2,
      "producto_id": 51,
      "tipo": "salida_pedido",
      "cantidad": -3,
      "existencia_resultante": 55,
      "referencia": {
        "tipo": "pedido",
        "id": "762"
      },
      "motivo": null,
      "usuario_id": 9,
      "fecha": "2026-11-27T01:24:16-06:00"
    },
    {
      "id": 2935,
      "microhub_id": 2,
      "producto_id": 32,
      "tipo": "salida_pedido",
      "cantidad": -3,
      "existencia_resultante": 8,
      "referencia": {
        "tipo": "pedido",
        "id": "762"
      },
      "motivo": null,
      "usuario_id": 9,
      "fecha": "2026-11-27T01:24:16-06:00"
    },
    {
      "id": 2934,
      "microhub_id": 2,
      "producto_id": 31,
      "tipo": "devolucion_cancelacion",
      "cantidad": 10,
      "existencia_resultante": 46,
      "referencia": {
        "tipo": "pedido",
        "id": "761"
      },
      "motivo": "Cierre del flujo de demostración",
      "usuario_id": 1,
      "fecha": "2026-11-27T01:24:15-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 1002,
    "paginas": 201
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
    "existencia_resultante": 8
  },
  {
    "tipo": "salida_pedido",
    "producto_id": 51,
    "cantidad": -3,
    "existencia_resultante": 55
  },
  {
    "tipo": "devolucion_cancelacion",
    "producto_id": 32,
    "cantidad": 3,
    "existencia_resultante": 11
  },
  {
    "tipo": "devolucion_cancelacion",
    "producto_id": 51,
    "cantidad": 3,
    "existencia_resultante": 58
  }
]
```

## Servicio reportes · puerto 5123

### F3-08 · Reporte del periodo en CSV · PASA

**Objetivo.** La entrega ya cuenta en los reportes.

**Petición.** `GET http://reportes:5123/api/v1/reportes/pedidos_por_dia/exportar?formato=csv`

```http
Accept: application/json
X-Traza-Id: a9d56005-1f39-4567-9612-bda515ce081a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 220 ms · traza `a9d56005-1f39-4567-9612-bda515ce081a`

```json
﻿Día,Pedidos,Unidades,Venta,Ticket promedio,Demanda no atendida
2026-11-25,56,282,8032.40,143.44,0
2026-11-26,213,1100,35117.60,164.87,8
2026-11-27,31,164,5138.50,165.76,1
Total,300,1546,48288.50,160.96,9

```

**Evidencia en PostgreSQL.** `SELECT reporte, formato, filas, left(sha256, 16) AS sha256 FROM reporte_exportacion ORDER BY id DESC LIMIT 1`

```json
[
  {
    "reporte": "pedidos_por_dia",
    "formato": "csv",
    "filas": 3,
    "sha256": "26ee903c46f44310"
  }
]
```
