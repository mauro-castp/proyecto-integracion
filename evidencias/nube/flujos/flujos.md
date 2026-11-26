# Procesos integrales de principio a fin


Generado el 2026-11-26 21:40 contra los servicios en ejecución. 40 de 40 casos pasan.

## Servicio planeacion · puerto 5106

### F1-01 · Escritorio (XML): el planeador registra una ubicación candidata · PASA

**Objetivo.** Planeación de ubicación.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos`

```http
Accept: application/xml
X-Traza-Id: 0be55a2a-fe4e-4cb2-98be-8130925388ca
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><candidato_nuevo xmlns="urn:microhubs:v1"><clave>********</clave><nombre>Ubicación del flujo F7B0B</nombre><latitud>25.760195</latitud><longitud>-100.370891</longitud><renta_estimada>15000.00</renta_estimada><nomina_estimada>36000.00</nomina_estimada><servicios_estimados>6000.00</servicios_estimados><otros_costos>4000.00</otros_costos><superficie_m2>100</superficie_m2><capacidad_fisica>120</capacidad_fisica><accesibilidad_vial>8</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km></candidato_nuevo>
```

**Respuesta.** HTTP 201 (esperado 201) · 63 ms · traza `0be55a2a-fe4e-4cb2-98be-8130925388ca`

```xml
<?xml version='1.0' encoding='utf-8'?>
<candidato xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>40</id><clave>FL-F7B0B</clave><nombre>Ubicación del flujo F7B0B</nombre><latitud>25.760195</latitud><longitud>-100.370891</longitud><renta_estimada>15000.00</renta_estimada><nomina_estimada>36000.00</nomina_estimada><servicios_estimados>6000.00</servicios_estimados><otros_costos>4000.00</otros_costos><costo_fijo>61000.00</costo_fijo><superficie_m2>100</superficie_m2><capacidad_fisica>120</capacidad_fisica><accesibilidad_vial>8</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato>
```

**Evidencia en PostgreSQL.** `SELECT id, clave, nombre, costo_fijo, decision FROM ubicacion_candidata WHERE clave = %s`

```json
[
  {
    "id": 40,
    "clave": "FL-F7B0B",
    "nombre": "Ubicación del flujo F7B0B",
    "costo_fijo": "61000.00",
    "decision": "pendiente"
  }
]
```

### F1-02 · El planeador simula la operación de la candidata · PASA

**Objetivo.** Capacidad, utilización y decisión sugerida (MongoDB).

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/40/simular`

```http
Accept: application/json
X-Traza-Id: 633876c7-78c0-4735-8926-00f827ac3fe1
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

**Respuesta.** HTTP 200 (esperado 200) · 199 ms · traza `633876c7-78c0-4735-8926-00f827ac3fe1`

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
X-Traza-Id: 05218df9-44c6-4c77-8426-b725fc7704c6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "candidato_id": 40,
  "pedidos_dia": 100,
  "ticket": 180,
  "margen_bruto": 0.3,
  "costos_fijos": 61000,
  "costo_variable_pedido": 22
}
```

**Respuesta.** HTTP 200 (esperado 200) · 237 ms · traza `05218df9-44c6-4c77-8426-b725fc7704c6`

```json
{
  "id": null,
  "nombre": null,
  "objeto": {
    "tipo": "candidato",
    "id": 40,
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

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/40/decision`

```http
Accept: application/json
X-Traza-Id: 0088e95d-6272-403a-b021-ae09ed934506
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aceptado",
  "motivo": "Cubre la zona del cliente y la demanda esperada supera el equilibrio."
}
```

**Respuesta.** HTTP 200 (esperado 200) · 43 ms · traza `0088e95d-6272-403a-b021-ae09ed934506`

```json
{
  "id": 40,
  "clave": "********",
  "nombre": "Ubicación del flujo F7B0B",
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
X-Traza-Id: e42e8717-6e06-4f21-bf6c-402ac59f740d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "clave": "********",
  "nombre": "Microhub F7B0B",
  "direccion": "Ubicación aprobada en planeación",
  "latitud": 25.760195,
  "longitud": -100.370891,
  "radio_km": 1.5,
  "capacidad_turno": 120
}
```

**Respuesta.** HTTP 201 (esperado 201) · 269 ms · traza `e42e8717-6e06-4f21-bf6c-402ac59f740d`

```json
{
  "id": 5,
  "clave": "********",
  "nombre": "Microhub F7B0B",
  "latitud": 25.760195,
  "longitud": -100.370891,
  "radio_km": 1.5,
  "estatus": "activo"
}
```

## Servicio capacidad · puerto 5117

### F1-06 · Asignar personal al microhub · PASA

**Objetivo.** Operadores, repartidores y capacidad física.

**Petición.** `PUT http://capacidad:5117/api/v1/capacidad/recursos/5`

```http
Accept: application/json
X-Traza-Id: e00f8a69-4ab6-460f-b48e-561ea6905c0a
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

**Respuesta.** HTTP 200 (esperado 200) · 324 ms · traza `e00f8a69-4ab6-460f-b48e-561ea6905c0a`

```json
{
  "microhub": {
    "id": 5,
    "nombre": "Microhub F7B0B"
  },
  "operadores": 2,
  "repartidores": 2,
  "capacidad_fisica": 120,
  "actualizado_en": "2026-11-26T15:39:53-06:00"
}
```

## Servicio usuarios · puerto 5102

### F1-07 · Crear la cuenta del operador · PASA

**Objetivo.** Cuenta nueva con su perfil y su microhub.

**Petición.** `POST http://usuarios:5102/api/v1/usuarios`

```http
Accept: application/json
X-Traza-Id: d743b5bb-6758-4101-b2ac-d4f82d3e3446
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Operador",
  "apellidos": "F7B0B",
  "correo": "operador.f7b0b@ejemplo.mx",
  "clave": "********",
  "rol": "operador",
  "microhub_id": 5
}
```

**Respuesta.** HTTP 201 (esperado 201) · 313 ms · traza `d743b5bb-6758-4101-b2ac-d4f82d3e3446`

```json
{
  "id": 49,
  "nombre": "Operador",
  "apellidos": "F7B0B",
  "correo": "operador.f7b0b@ejemplo.mx",
  "telefono": null,
  "rol": "operador",
  "microhub": {
    "id": 5,
    "clave": "********",
    "nombre": "Microhub F7B0B"
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
X-Traza-Id: 6fe54389-ad5f-45b4-b161-8f66ab38b11b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "origen_microhub_id": 1,
  "destino_microhub_id": 5,
  "producto_id": 31,
  "cantidad": 12,
  "motivo": "Inventario inicial del microhub nuevo",
  "operacion_uuid": "4389d82d-9b7e-4728-a6e6-85b8c7458794"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 288 ms · traza `6fe54389-ad5f-45b4-b161-8f66ab38b11b`

```json
{
  "producto_id": 31,
  "cantidad": 12,
  "duplicado": false,
  "origen": {
    "microhub_id": 1,
    "existencia": 45,
    "movimiento_id": 1012
  },
  "destino": {
    "microhub_id": 5,
    "existencia": 12,
    "movimiento_id": 1013
  }
}
```

### F1-08b · Surtir el microhub nuevo · PASA

**Objetivo.** Transferencia atómica desde MH-01.

**Petición.** `POST http://inventario:5111/api/v1/inventario/transferencias`

```http
Accept: application/json
X-Traza-Id: 2af98705-65ea-4588-a401-fbbaa2d81bcc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "origen_microhub_id": 1,
  "destino_microhub_id": 5,
  "producto_id": 47,
  "cantidad": 12,
  "motivo": "Inventario inicial del microhub nuevo",
  "operacion_uuid": "513163a3-d395-4590-8c7b-5f68767b0fb4"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 65 ms · traza `2af98705-65ea-4588-a401-fbbaa2d81bcc`

```json
{
  "producto_id": 47,
  "cantidad": 12,
  "duplicado": false,
  "origen": {
    "microhub_id": 1,
    "existencia": 50,
    "movimiento_id": 1014
  },
  "destino": {
    "microhub_id": 5,
    "existencia": 12,
    "movimiento_id": 1015
  }
}
```

## Servicio pedidos · puerto 5104

### F1-09 · Android (JSON): el cliente hace su pedido · PASA

**Objetivo.** El motor lo asigna al microhub más cercano que tiene todo: el nuevo.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: acd8334d-d4a0-4c14-a1a7-d9ec578d379b
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
      "producto_id": 47,
      "cantidad": 3
    }
  ],
  "operacion_uuid": "f1461f52-5661-4b70-920a-12a74202af0f"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 379 ms · traza `acd8334d-d4a0-4c14-a1a7-d9ec578d379b`

```json
{
  "id": 180,
  "folio": "PED-20261126-000180",
  "estado": "asignado",
  "zona_id": 3,
  "microhub_id": 5,
  "subtotal": 336.0,
  "costo_envio": 0.0,
  "total": 336.0,
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
    "microhub_ganador_id": 5,
    "motivo": null
  }
]
```

**Evidencia en PostgreSQL.** `SELECT tipo, producto_id, cantidad, existencia_resultante FROM movimiento_inventario WHERE referencia_tipo = 'pedido' AND referencia_id = %s`

```json
[
  {
    "tipo": "salida_pedido",
    "producto_id": 31,
    "cantidad": -3,
    "existencia_resultante": 9
  },
  {
    "tipo": "salida_pedido",
    "producto_id": 47,
    "cantidad": -3,
    "existencia_resultante": 9
  }
]
```

### F1-10 · El operador prepara el pedido · PASA

**Objetivo.** La transición la valida el motor.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/180/estado`

```http
Accept: application/json
X-Traza-Id: 2b19a590-1f20-4510-ac4e-939118a063c1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0OSIs…(295 caracteres)
Content-Type: application/json
```

```json
{
  "estado": "en_preparacion"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 69 ms · traza `2b19a590-1f20-4510-ac4e-939118a063c1`

```json
{
  "id": 180,
  "folio": "PED-20261126-000180",
  "estado": "en_preparacion",
  "zona": {
    "id": 3,
    "nombre": "Paseo de San Bernabé"
  },
  "microhub_id": 5,
  "total": 336.0,
  "creado_en": "2026-11-26T15:39:55-06:00"
}
```

### F1-11 · El operador lo marca listo · PASA

**Objetivo.** Queda disponible para despacho.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/180/listo`

```http
Accept: application/json
X-Traza-Id: 35a8c4b0-4d47-4617-8284-a50d5718ba4c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0OSIs…(295 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 200 (esperado 200) · 47 ms · traza `35a8c4b0-4d47-4617-8284-a50d5718ba4c`

```json
{
  "id": 180,
  "estado": "en_preparacion",
  "listo_en": "2026-11-26T15:39:55-06:00"
}
```

## Servicio rutas · puerto 5118

### F1-12 · Proponer la ruta de despacho · PASA

**Objetivo.** Agrupa, asigna repartidor y ordena las paradas (algoritmo de rutas).

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/json
X-Traza-Id: 96b4fe4b-de2a-4d7f-91a1-7356a5847774
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0OSIs…(295 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 5,
  "pedido_ids": [
    180
  ],
  "repartidor_ids": [
    7
  ],
  "metodo": "automatico",
  "guardar": true
}
```

**Respuesta.** HTTP 201 (esperado 201) · 349 ms · traza `96b4fe4b-de2a-4d7f-91a1-7356a5847774`

```json
{
  "id": 9,
  "estado": "propuesto",
  "version": 1,
  "microhub": {
    "id": 5,
    "nombre": "Microhub F7B0B"
  },
  "fecha": "2026-11-26",
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
            "id": 180,
            "folio": "PED-20261126-000180"
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
X-Traza-Id: d52f3662-d0a4-4590-a11b-76f3ecb57de9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0OSIs…(295 caracteres)
Content-Type: application/json
```

```json
{
  "pedido_id": 180,
  "repartidor_id": 7,
  "orden_parada": 1
}
```

**Respuesta.** HTTP 201 (esperado 201) · 60 ms · traza `d52f3662-d0a4-4590-a11b-76f3ecb57de9`

```json
{
  "entrega_id": 140,
  "pedido_id": 180,
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
    "referencia_id": "140"
  }
]
```

### F1-14 · Android: el repartidor ve su parada · PASA

**Objetivo.** Sesión validada en Redis.

**Petición.** `GET http://entregas:5105/api/v1/entregas/mias?por_pagina=50`

```http
Accept: application/json
X-Traza-Id: 41c25124-7200-486e-b04e-116683d89e5d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 42 ms · traza `41c25124-7200-486e-b04e-116683d89e5d`

```json
{
  "datos": [
    {
      "id": 136,
      "pedido_id": 167,
      "folio": "PED-20261126-000167",
      "estado_pedido": "en_ruta",
      "orden_parada": 1,
      "direccion": "Fresno 2232, Paseo de San Bernabé",
      "zona": "Paseo de San Bernabé",
      "distancia_km": 0.88,
      "minutos_estimados": 10.0,
      "total": 137.0
    },
    {
      "id": 140,
      "pedido_id": 180,
      "folio": "PED-20261126-000180",
      "estado_pedido": "en_ruta",
      "orden_parada": 1,
      "direccion": "Nogal 1440, Paseo de San Bernabé",
      "zona": "Paseo de San Bernabé",
      "distancia_km": null,
      "minutos_estimados": null,
      "total": 336.0
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 50,
    "total": 2,
    "paginas": 1
  }
}
```

**Evidencia en Redis.** `SCARD auth:sesion:7`

```json
[
  {
    "comando": "SCARD auth:sesion:7",
    "valor": 1
  }
]
```

## Servicio seguimiento · puerto 5110

### F1-15 · El repartidor envía su recorrido · PASA

**Objetivo.** Puntos GPS en MongoDB (2dsphere).

**Petición.** `POST http://seguimiento:5110/api/v1/seguimiento/140/ubicaciones`

```http
Accept: application/json
X-Traza-Id: 6f25c270-0c4a-447b-9ffd-11b5177de9b8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "puntos": [
    {
      "latitud": 25.760195,
      "longitud": -100.370891,
      "capturado_en": "2026-11-26T21:35:56.113238+00:00"
    },
    {
      "latitud": 25.759995,
      "longitud": -100.371091,
      "capturado_en": "2026-11-26T21:38:56.113261+00:00"
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 39 ms · traza `6f25c270-0c4a-447b-9ffd-11b5177de9b8`

```json
{
  "recibidos": 2
}
```

## Servicio documentos · puerto 5107

### F1-16 · La foto de evidencia queda en el almacén · PASA

**Objetivo.** En la base solo sus datos; se descarga con un enlace firmado.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b08a72c4d50e5ef3e505e98/enlace`

```http
Accept: application/json
X-Traza-Id: 3c0d1ef5-8715-490c-8c9b-3da85abbab2a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 139 ms · traza `3c0d1ef5-8715-490c-8c9b-3da85abbab2a`

```json
{
  "id": "6b08a72c4d50e5ef3e505e98",
  "nombre": "evidencia-flujo1-F7B0B.jpg",
  "url_firmada": "https://storage.googleapis.com/microhubs-evidencias-637044/d…(1005 caracteres)",
  "metodo": "GET",
  "segundos": 300,
  "expira_en": "2026-11-26T15:44:56-06:00"
}
```

**Evidencia en MongoDB.** `db.documentos.findOne({_id}) sin contenido`

```json
{
  "_id": "6b08a72c4d50e5ef3e505e98",
  "nombre": "evidencia-flujo1-F7B0B.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "140"
  },
  "subido_por": 7,
  "creado_en": "2026-11-26 21:39:56.174000+00:00",
  "ruta": "documentos/2026/11/6b08a72c4d50e5ef3e505e98.jpg",
  "privacidad": "privado",
  "estado": "activo",
  "metadatos": {
    "almacen": "gcs",
    "origen": "api"
  }
}
```

## Servicio entregas · puerto 5105

### F1-17 · El repartidor cierra la entrega · PASA

**Objetivo.** Cobro, ubicación y evidencia; idempotente.

**Petición.** `POST http://entregas:5105/api/v1/entregas/140/resultado`

```http
Accept: application/json
X-Traza-Id: 8c230a18-12b8-440c-98ee-0cb6383ef3b7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 336.0,
  "cambio_entregado": 0,
  "ubicacion": {
    "latitud": 25.759995,
    "longitud": -100.371091
  },
  "evidencia_ids": [
    "6b08a72c4d50e5ef3e505e98"
  ],
  "capturado_en": "2026-11-26T21:39:56.491526+00:00",
  "id_cliente_local": "d64ec264-067c-4f37-a23f-7870c444d72e"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 90 ms · traza `8c230a18-12b8-440c-98ee-0cb6383ef3b7`

```json
{
  "entrega_id": 140,
  "pedido_id": 180,
  "estado_pedido": "entregado",
  "cerrado_en": "2026-11-26T15:39:56-06:00",
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
    "usuario_id": 49,
    "proceso": null
  },
  {
    "estado_anterior": "en_preparacion",
    "estado_nuevo": "en_ruta",
    "usuario_id": 49,
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
X-Traza-Id: 2a7f6efb-8bad-49cd-ba66-6d0724375e52
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 230 ms · traza `2a7f6efb-8bad-49cd-ba66-6d0724375e52`

```json
{
  "datos": [
    {
      "id": 75,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000180",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "180"
      },
      "creada_en": "2026-11-26T15:39:56-06:00"
    },
    {
      "id": 10,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261125-000158",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "158"
      },
      "creada_en": "2026-11-25T12:21:13-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 2,
    "paginas": 1
  }
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F1-19 · El auditor reconstruye la historia del pedido · PASA

**Objetivo.** Bitácora, estados, inventario y archivos en una línea de tiempo.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/pedido/180`

```http
Accept: application/json
X-Traza-Id: f839edd3-66d6-4b67-8969-a4fdef0a473f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 120 ms · traza `f839edd3-66d6-4b67-8969-a4fdef0a473f`

```json
{
  "objeto": {
    "tipo": "pedido",
    "id": "180"
  },
  "total": 15,
  "eventos": [
    {
      "fecha": "2026-11-26T15:39:55-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "actualizado_en = 2026-11-26T15:39:55.187116-06:00; asignado_en = None; cerrado_en = None; cliente_id = 1",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "180"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": null,
          "nuevo": "2026-11-26T15:39:55.187116-06:00"
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
          "nuevo": "2026-11-26T15:39:55.187116-06:00"
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
          "nuevo": "PED-20261126-000180"
        },
        {
          "campo": "id",
          "anterior": null,
          "nuevo": "180"
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
      "fecha": "2026-11-26T15:39:55-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "asignado_en = 2026-11-26T15:39:55.187116-06:00; estado: creado → asignado; microhub_id = 5",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "180"
      },
      "cambios": [
        {
          "campo": "asignado_en",
          "anterior": null,
          "nuevo": "2026-11-26T15:39:55.187116-06:00"
        },
        {
          "campo": "estado",
          "anterior": "creado",
          "nuevo": "asignado"
        },
        {
          "campo": "microhub_id",
          "anterior": null,
          "nuevo": "5"
        }
      ]
    },
    {
      "fecha": "2026-11-26T15:39:55-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "nuevo → creado",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "180"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T15:39:55-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "creado → asignado",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "180"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T15:39:55-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -3 de producto 31 en microhub 5 (existencia 9)",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "5-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T15:39:55-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -3 de producto 47 en microhub 5 (existencia 9)",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "5-47"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T15:39:55-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-26T15:39:55.187116-06:00 → 2026-11-26T15:39:55.545794-06:00; estado: asignado → en_preparacion",
      "usuario": {
        "id": 49,
        "nombre": "Operador F7B0B"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "180"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-26T15:39:55.187116-06:00",
          "nuevo": "2026-11-26T15:39:55.545794-06:00"
        },
        {
          "campo": "estado",
          "anterior": "asignado",
          "nuevo": "en_preparacion"
        }
      ]
    },
    {
      "fecha": "2026-11-26T15:39:55-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "asignado → en_preparacion",
      "usuario": {
        "id": 49,
        "nombre": "Operador F7B0B"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "180"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T15:39:55-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "listo_en = 2026-11-26T15:39:55.614923-06:00",
      "usuario": {
        "id": 49,
        "nombre": "Operador F7B0B"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "180"
      },
      "cambios": [
        {
          "campo": "listo_en",
          "anterior": null,
          "nuevo": "2026-11-26T15:39:55.614923-06:00"
        }
      ]
    },
    {
      "fecha": "2026-11-26T15:39:56-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "asignada_en = 2026-11-26T15:39:56.008677-06:00; cambio_entregado = None; capturado_en = None; cerrada_por_usuario_id = None",
      "usuario": {
        "id": 49,
        "nombre": "Operador F7B0B"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "140"
      },
      "cambios": [
        {
          "campo": "asignada_en",
          "anterior": null,
          "nuevo": "2026-11-26T15:39:56.008677-06:00"
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
      "fecha": "2026-11-26T15:39:56-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-26T15:39:55.545794-06:00 → 2026-11-26T15:39:56.008677-06:00; estado: en_preparacion → en_ruta",
      "usuario": {
        "id": 49,
        "nombre": "Operador F7B0B"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "180"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-26T15:39:55.545794-06:00",
          "nuevo": "2026-11-26T15:39:56.008677-06:00"
        },
        {
          "campo": "estado",
          "anterior": "en_preparacion",
          "nuevo": "en_ruta"
        }
      ]
    },
    {
      "fecha": "2026-11-26T15:39:56-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "en_preparacion → en_ruta",
      "usuario": {
        "id": 49,
        "nombre": "Operador F7B0B"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "180"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T15:39:56-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "cambio_entregado = 0.0; capturado_en = 2026-11-26T15:39:56.4…(145 caracteres)",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "140"
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
          "nuevo": "2026-11-26T15:39:56.491526-06:00"
        },
        {
          "campo": "cerrada_por_usuario_id",
          "anterior": null,
          "nuevo": "7"
        },
        {
          "campo": "cierre_en",
          "anterior": null,
          "nuevo": "2026-11-26T15:39:56.524132-06:00"
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
          "nuevo": "[\"6b08a72c4d50e5ef3e505e98\"]"
        },
        {
          "campo": "evidencia_url",
          "anterior": null,
          "nuevo": "/api/v1/documentos/6b08a72c4d50e5ef3e505e98"
        },
        {
          "campo": "id_cliente_local",
          "anterior": null,
          "nuevo": "d64ec264-067c-4f37-a23f-7870c444d72e"
        },
        {
          "campo": "monto_cobrado",
          "anterior": null,
          "nuevo": "336.0"
        },
        {
          "campo": "resultado",
          "anterior": null,
          "nuevo": "entregado"
        }
      ]
    },
    {
      "fecha": "2026-11-26T15:39:56-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-26T15:39:56.008677-06:00 → 2026-11-2…(159 caracteres)",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "180"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-26T15:39:56.008677-06:00",
          "nuevo": "2026-11-26T15:39:56.524132-06:00"
        },
        {
          "campo": "cerrado_en",
          "anterior": null,
          "nuevo": "2026-11-26T15:39:56.524132-06:00"
        },
        {
          "campo": "estado",
          "anterior": "en_ruta",
          "nuevo": "entregado"
        }
      ]
    },
    {
      "fecha": "2026-11-26T15:39:56-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "en_ruta → entregado",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "180"
      },
      "cambios": []
    }
  ]
}
```

## Servicio reportes · puerto 5123

### F1-20 · Visualización: el microhub nuevo ya aparece en la comparación · PASA

**Objetivo.** Datos listos para Highcharts.

**Petición.** `GET http://reportes:5123/api/v1/reportes/comparacion_microhubs/grafica?microhub_id=5`

```http
Accept: application/json
X-Traza-Id: aa58b3f5-ed68-46ce-9601-45b4174eeb69
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 412 ms · traza `aa58b3f5-ed68-46ce-9601-45b4174eeb69`

```json
{
  "reporte": "comparacion_microhubs",
  "titulo": "Comparación entre microhubs",
  "tipo": "column",
  "unidad": "pedidos / MXN",
  "categorias": [
    "Microhub F7B0B"
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
        336.0
      ]
    }
  ]
}
```

## Servicio microhubs · puerto 5109

### F1-21 · Cierre: dar de baja el microhub de la demostración · PASA

**Objetivo.** Baja lógica; conserva su historia.

**Petición.** `DELETE http://microhubs:5109/api/v1/microhubs/5`

```http
Accept: application/json
X-Traza-Id: 2df13a26-4585-4d9f-b3c6-f40ec27bfcee
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 31 ms · traza `2df13a26-4585-4d9f-b3c6-f40ec27bfcee`

```json
(sin cuerpo)
```

## Servicio pedidos · puerto 5104

### F2-01 · Android: un cliente compra y el inventario baja · PASA

**Objetivo.** El motor descuenta inventario en la misma transacción.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: 26b63abf-2ecb-46f2-83fa-03d2c23838ab
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
Content-Type: application/json
```

```json
{
  "lineas": [
    {
      "producto_id": 51,
      "cantidad": 10
    }
  ],
  "operacion_uuid": "76a81c4a-a2ce-431f-8103-b9235b2fcc5e"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 147 ms · traza `26b63abf-2ecb-46f2-83fa-03d2c23838ab`

```json
{
  "id": 181,
  "folio": "PED-20261126-000181",
  "estado": "asignado",
  "zona_id": 3,
  "microhub_id": 2,
  "subtotal": 680.0,
  "costo_envio": 0.0,
  "total": 680.0,
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
    "producto_id": 51,
    "cantidad": -10,
    "existencia_resultante": 65
  }
]
```

## Servicio inventario · puerto 5111

### F2-02 · El operador fija el mínimo y nace la alerta · PASA

**Objetivo.** El trigger avisa del faltante.

**Petición.** `PATCH http://inventario:5111/api/v1/inventario/1/51/minimo`

```http
Accept: application/json
X-Traza-Id: 19fc6921-bc4b-4643-873e-761358830a88
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "minimo": 39
}
```

**Respuesta.** HTTP 200 (esperado 200) · 439 ms · traza `19fc6921-bc4b-4643-873e-761358830a88`

```json
{
  "microhub": {
    "id": 1,
    "nombre": "Microhub San Bernabé Centro"
  },
  "producto": {
    "id": 51,
    "clave_interna": "HI-006",
    "nombre": "Pañal etapa 3"
  },
  "existencia": 29,
  "minimo": 39,
  "reservado": 0,
  "disponible": 29,
  "estado": "bajo_minimo",
  "actualizado_en": "2026-11-26T15:39:58-06:00"
}
```

### F2-03 · La alerta de faltante · PASA

**Objetivo.** Qué producto, cuánto falta y qué tan grave es.

**Petición.** `GET http://inventario:5111/api/v1/inventario/alertas?microhub_id=1&por_pagina=100`

```http
Accept: application/json
X-Traza-Id: aa5cae52-7555-49e1-abf2-9a51bd8b79a0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 66 ms · traza `aa5cae52-7555-49e1-abf2-9a51bd8b79a0`

```json
{
  "datos": [
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 21,
        "clave_interna": "BE-001",
        "nombre": "Agua purificada"
      },
      "existencia": 0,
      "minimo": 10,
      "disponible": 0,
      "faltante": 10,
      "severidad": "agotado"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 51,
        "clave_interna": "HI-006",
        "nombre": "Pañal etapa 3"
      },
      "existencia": 29,
      "minimo": 39,
      "disponible": 29,
      "faltante": 10,
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
X-Traza-Id: efac2e28-5282-45c2-bc58-9f6f73362c6f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 1,
  "motivo": "Faltante detectado por el sistema",
  "lineas": [
    {
      "producto_id": 51,
      "cantidad": 100
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 247 ms · traza `efac2e28-5282-45c2-bc58-9f6f73362c6f`

```json
{
  "id": 10,
  "folio": "SC-20261126-000010",
  "microhub_id": 1,
  "estado": "pendiente",
  "motivo": "Faltante detectado por el sistema",
  "solicitada_por": 2,
  "decidida_por": null,
  "decision_motivo": null,
  "decidida_en": null,
  "creada_en": "2026-11-26T15:39:58-06:00",
  "lineas": [
    {
      "producto": {
        "id": 51,
        "nombre": "Pañal etapa 3"
      },
      "cantidad": 100
    }
  ]
}
```

### F2-05 · El administrador aprueba · PASA

**Objetivo.** Quien pidió recibe el aviso.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/10/decision`

```http
Accept: application/json
X-Traza-Id: ac5133dd-8048-4918-a40e-f9fa54f2ed82
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aprobada",
  "motivo": "Con presupuesto"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 155 ms · traza `ac5133dd-8048-4918-a40e-f9fa54f2ed82`

```json
{
  "id": 10,
  "folio": "SC-20261126-000010",
  "microhub_id": 1,
  "estado": "aprobada",
  "motivo": "Faltante detectado por el sistema",
  "solicitada_por": 2,
  "decidida_por": 1,
  "decision_motivo": "Con presupuesto",
  "decidida_en": "2026-11-26T15:39:59-06:00",
  "creada_en": "2026-11-26T15:39:58-06:00",
  "lineas": [
    {
      "producto": {
        "id": 51,
        "nombre": "Pañal etapa 3"
      },
      "cantidad": 100
    }
  ]
}
```

### F2-06 · Se emite la orden de compra · PASA

**Objetivo.** Al proveedor con la mejor oferta.

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/10/ordenar`

```http
Accept: application/json
X-Traza-Id: 9c2b617e-a6fc-461d-b8af-0a39eb88adf8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 201 (esperado 201) · 395 ms · traza `9c2b617e-a6fc-461d-b8af-0a39eb88adf8`

```json
{
  "solicitud_id": 10,
  "ordenes": [
    {
      "id": 6,
      "folio": "OC-20261126-000006",
      "solicitud_id": 10,
      "proveedor": {
        "id": 3,
        "nombre": "Mayorista San Nicolás"
      },
      "microhub_id": 1,
      "estado": "emitida",
      "fecha_esperada": "2026-11-30",
      "total": 4624.0,
      "creada_en": "2026-11-26T15:39:59-06:00",
      "cerrada_en": null,
      "lineas": [
        {
          "producto": {
            "id": 51,
            "nombre": "Pañal etapa 3"
          },
          "cantidad": 100,
          "precio_compra": 46.24,
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/6/recepcion`

```http
Accept: application/json
X-Traza-Id: 4c2955fc-be73-4886-b7d1-2f8de8dec986
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "operacion_uuid": "8240ecde-c737-401c-bf34-8373f212bd33",
  "nota": "Completo",
  "lineas": [
    {
      "producto_id": 51,
      "cantidad": 100
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 199 ms · traza `4c2955fc-be73-4886-b7d1-2f8de8dec986`

```json
{
  "orden": {
    "id": 6,
    "folio": "OC-20261126-000006",
    "solicitud_id": 10,
    "proveedor": {
      "id": 3,
      "nombre": "Mayorista San Nicolás"
    },
    "microhub_id": 1,
    "estado": "recibida",
    "fecha_esperada": "2026-11-30",
    "total": 4624.0,
    "creada_en": "2026-11-26T15:39:59-06:00",
    "cerrada_en": "2026-11-26T15:39:59-06:00",
    "lineas": [
      {
        "producto": {
          "id": 51,
          "nombre": "Pañal etapa 3"
        },
        "cantidad": 100,
        "precio_compra": 46.24,
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
    "existencia": 129,
    "minimo": 39
  }
]
```

## Servicio documentos · puerto 5107

### F2-08 · La remisión firmada queda en el almacén · PASA

**Objetivo.** Archivo con enlace firmado.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b08a72f4d50e5ef3e505e9d/enlace`

```http
Accept: application/json
X-Traza-Id: 1eeb71b6-b085-4087-9c0b-1861fb44b9fe
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 135 ms · traza `1eeb71b6-b085-4087-9c0b-1861fb44b9fe`

```json
{
  "id": "6b08a72f4d50e5ef3e505e9d",
  "nombre": "remision-6.jpg",
  "url_firmada": "https://storage.googleapis.com/microhubs-evidencias-637044/d…(993 caracteres)",
  "metodo": "GET",
  "segundos": 300,
  "expira_en": "2026-11-26T15:45:00-06:00"
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F2-09 · Trazabilidad del producto en el microhub · PASA

**Objetivo.** Salida por pedido y recepción por orden.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/inventario?microhub_id=1&producto_id=51`

```http
Accept: application/json
X-Traza-Id: ff4f060d-2371-4d05-88af-91335f320df0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 35 ms · traza `ff4f060d-2371-4d05-88af-91335f320df0`

```json
{
  "objeto": {
    "tipo": "inventario",
    "id": "1-51"
  },
  "total": 9,
  "eventos": [
    {
      "fecha": "2026-10-14T06:58:58-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -1 de producto 51 en microhub 1 (existencia 31)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-51"
      },
      "cambios": []
    },
    {
      "fecha": "2026-10-16T20:15:08-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -1 de producto 51 en microhub 1 (existencia 33)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-51"
      },
      "cambios": []
    },
    {
      "fecha": "2026-10-25T16:12:30-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -1 de producto 51 en microhub 1 (existencia 30)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-51"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-04T12:10:13-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -1 de producto 51 en microhub 1 (existencia 32)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-51"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-11T06:06:18-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "devolucion_cancelacion: +1 de producto 51 en microhub 1 (existencia 33). Entrega fallida: la mercancía regresa al microhub.",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-51"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-11T06:06:18-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -1 de producto 51 en microhub 1 (existencia 32)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-51"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-17T04:12:09-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -1 de producto 51 en microhub 1 (existencia 29)",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-51"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-25T12:10:23-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "recepcion: +34 de producto 51 en microhub 1 (existencia 34). Carga inicial de semilla",
      "usuario": null,
      "entidad": {
        "tipo": "inventario",
        "id": "1-51"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T15:39:59-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "recepcion: +100 de producto 51 en microhub 1 (existencia 129). Recepción de la orden OC-20261126-000006: Completo",
      "usuario": {
        "id": 2,
        "nombre": "Ruth Elizabeth Soriano"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "1-51"
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
X-Traza-Id: 7e5c524f-129f-4195-b548-d2dbf285c883
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 214 ms · traza `7e5c524f-129f-4195-b548-d2dbf285c883`

```json
﻿Microhub,Producto,Existencia,Mínimo,Disponible,Faltante,Severidad
Microhub San Bernabé Centro,Agua purificada,0,10,0,10,agotado
Total,,,,,10,

```

## Servicio pedidos · puerto 5104

### F3-01 · El cliente hace un pedido · PASA

**Objetivo.** Punto de partida del recorrido.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: 24921d91-c585-473b-a173-f4d585cc2db2
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

**Respuesta.** HTTP 201 (esperado 201) · 129 ms · traza `24921d91-c585-473b-a173-f4d585cc2db2`

```json
{
  "id": 182,
  "folio": "PED-20261126-000182",
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
X-Traza-Id: 8b5b0a32-2888-455b-b014-3e75405436f4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
Content-Type: application/json
```

```json
{
  "pedido_id": 182,
  "repartidor_id": 7
}
```

**Respuesta.** HTTP 201 (esperado 201) · 43 ms · traza `8b5b0a32-2888-455b-b014-3e75405436f4`

```json
{
  "entrega_id": 141,
  "pedido_id": 182,
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
X-Traza-Id: 20b7b5b3-23b1-4dc2-b903-9b15c2674d3c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "d6bd04ea-6b7f-49f7-8271-431264a68a73",
  "dispositivo": "android-flujo-a4fe54",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "ec959ba3-0ea7-4231-b6fd-9514b6b47d5c",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-26T21:20:01.805886+00:00",
      "datos": {
        "entrega_id": 141,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-26T21:20:01.805904+00:00"
          },
          {
            "latitud": 25.7491,
            "longitud": -100.3611,
            "capturado_en": "2026-11-26T21:25:01.805912+00:00"
          }
        ]
      }
    },
    {
      "operacion_uuid": "10a2975c-555d-4661-8724-eb8949fc2688",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-26T21:28:01.805927+00:00",
      "datos": {
        "entrega_id": 141,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "El cliente no estaba en su domicilio",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b08a731b02903f83cb4b145"
        ],
        "capturado_en": "2026-11-26T21:28:01.805933+00:00"
      }
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 586 ms · traza `20b7b5b3-23b1-4dc2-b903-9b15c2674d3c`

```json
{
  "id": 3,
  "lote_uuid": "d6bd04ea-6b7f-49f7-8271-431264a68a73",
  "dispositivo": "android-flujo-a4fe54",
  "recibido_en": "2026-11-26T15:40:01-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 0,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "ec959ba3-0ea7-4231-b6fd-9514b6b47d5c",
      "tipo": "ubicaciones",
      "estado": "aplicada",
      "duplicada": false,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    },
    {
      "operacion_uuid": "10a2975c-555d-4661-8724-eb8949fc2688",
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
    "creada_en": "2026-11-26 15:20:01.805886-06:00"
  },
  {
    "tipo": "entrega_resultado",
    "estado": "aplicada",
    "intentos": 1,
    "creada_en": "2026-11-26 15:28:01.805927-06:00"
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
X-Traza-Id: 4fa40d8f-876b-4e0b-8c7b-42d4aa690f92
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "d6bd04ea-6b7f-49f7-8271-431264a68a73",
  "dispositivo": "android-flujo-a4fe54",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "ec959ba3-0ea7-4231-b6fd-9514b6b47d5c",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-26T21:20:01.805886+00:00",
      "datos": {
        "entrega_id": 141,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-26T21:20:01.805904+00:00"
          },
          {
            "latitud": 25.7491,
            "longitud": -100.3611,
            "capturado_en": "2026-11-26T21:25:01.805912+00:00"
          }
        ]
      }
    },
    {
      "operacion_uuid": "10a2975c-555d-4661-8724-eb8949fc2688",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-26T21:28:01.805927+00:00",
      "datos": {
        "entrega_id": 141,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "El cliente no estaba en su domicilio",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b08a731b02903f83cb4b145"
        ],
        "capturado_en": "2026-11-26T21:28:01.805933+00:00"
      }
    }
  ]
}
```

**Respuesta.** HTTP 200 (esperado 200) · 112 ms · traza `4fa40d8f-876b-4e0b-8c7b-42d4aa690f92`

```json
{
  "id": 3,
  "lote_uuid": "d6bd04ea-6b7f-49f7-8271-431264a68a73",
  "dispositivo": "android-flujo-a4fe54",
  "recibido_en": "2026-11-26T15:40:01-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 2,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "ec959ba3-0ea7-4231-b6fd-9514b6b47d5c",
      "tipo": "ubicaciones",
      "estado": "aplicada",
      "duplicada": true,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    },
    {
      "operacion_uuid": "10a2975c-555d-4661-8724-eb8949fc2688",
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
X-Traza-Id: c8f9e66c-7b73-4b0a-9f7c-17c83a69eb32
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 131 ms · traza `c8f9e66c-7b73-4b0a-9f7c-17c83a69eb32`

```json
{
  "datos": [
    {
      "id": 82,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000182",
      "mensaje": "El pedido cambió a entrega_fallida.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "182"
      },
      "creada_en": "2026-11-26T15:40:01-06:00"
    },
    {
      "id": 80,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000181",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "181"
      },
      "creada_en": "2026-11-26T15:40:00-06:00"
    },
    {
      "id": 75,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000180",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "180"
      },
      "creada_en": "2026-11-26T15:39:56-06:00"
    },
    {
      "id": 10,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261125-000158",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "158"
      },
      "creada_en": "2026-11-25T12:21:13-06:00"
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

## Servicio auditoria-monitoreo · puerto 5126

### F3-06 · El auditor revisa la entrega · PASA

**Objetivo.** Bitácora y archivos de la entrega.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/entrega/141`

```http
Accept: application/json
X-Traza-Id: bc928b6a-fc66-4a84-a3c0-13a6d1116674
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 42 ms · traza `bc928b6a-fc66-4a84-a3c0-13a6d1116674`

```json
{
  "objeto": {
    "tipo": "entrega",
    "id": "141"
  },
  "total": 3,
  "eventos": [
    {
      "fecha": "2026-11-26T15:40:01-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "asignada_en = 2026-11-26T15:40:01.684338-06:00; cambio_entregado = None; capturado_en = None; cerrada_por_usuario_id = None",
      "usuario": {
        "id": 3,
        "nombre": "María José Cedillo Mata"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "141"
      },
      "cambios": [
        {
          "campo": "asignada_en",
          "anterior": null,
          "nuevo": "2026-11-26T15:40:01.684338-06:00"
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
      "fecha": "2026-11-26T15:40:01-06:00",
      "origen": "documentos",
      "accion": "documento_subido",
      "descripcion": "evidencia-flujo3-141.jpg (276 bytes, sha256 7f6025cd8a98…)",
      "usuario": {
        "id": 7,
        "nombre": null
      },
      "entidad": {
        "tipo": "documento",
        "id": "6b08a731b02903f83cb4b145"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T15:40:01-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "cambio_entregado = 0.0; capturado_en = 2026-11-26T15:28:01.8…(145 caracteres)",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "141"
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
          "nuevo": "2026-11-26T15:28:01.805933-06:00"
        },
        {
          "campo": "cerrada_por_usuario_id",
          "anterior": null,
          "nuevo": "7"
        },
        {
          "campo": "cierre_en",
          "anterior": null,
          "nuevo": "2026-11-26T15:40:01.989769-06:00"
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
          "nuevo": "[\"6b08a731b02903f83cb4b145\"]"
        },
        {
          "campo": "evidencia_url",
          "anterior": null,
          "nuevo": "/api/v1/documentos/6b08a731b02903f83cb4b145"
        },
        {
          "campo": "id_cliente_local",
          "anterior": null,
          "nuevo": "10a2975c-555d-4661-8724-eb8949fc2688"
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
X-Traza-Id: 702e0a4c-98bf-4687-ab3f-4961018f1051
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 34 ms · traza `702e0a4c-98bf-4687-ab3f-4961018f1051`

```json
{
  "datos": [
    {
      "id": 1024,
      "microhub_id": 2,
      "producto_id": 51,
      "tipo": "devolucion_cancelacion",
      "cantidad": 3,
      "existencia_resultante": 75,
      "referencia": {
        "tipo": "pedido",
        "id": "182"
      },
      "motivo": "Entrega fallida: la mercancía regresa al microhub.",
      "usuario_id": 7,
      "fecha": "2026-11-26T15:40:01-06:00"
    },
    {
      "id": 1023,
      "microhub_id": 2,
      "producto_id": 32,
      "tipo": "devolucion_cancelacion",
      "cantidad": 3,
      "existencia_resultante": 25,
      "referencia": {
        "tipo": "pedido",
        "id": "182"
      },
      "motivo": "Entrega fallida: la mercancía regresa al microhub.",
      "usuario_id": 7,
      "fecha": "2026-11-26T15:40:01-06:00"
    },
    {
      "id": 1022,
      "microhub_id": 2,
      "producto_id": 51,
      "tipo": "salida_pedido",
      "cantidad": -3,
      "existencia_resultante": 72,
      "referencia": {
        "tipo": "pedido",
        "id": "182"
      },
      "motivo": null,
      "usuario_id": 9,
      "fecha": "2026-11-26T15:40:01-06:00"
    },
    {
      "id": 1021,
      "microhub_id": 2,
      "producto_id": 32,
      "tipo": "salida_pedido",
      "cantidad": -3,
      "existencia_resultante": 22,
      "referencia": {
        "tipo": "pedido",
        "id": "182"
      },
      "motivo": null,
      "usuario_id": 9,
      "fecha": "2026-11-26T15:40:01-06:00"
    },
    {
      "id": 1020,
      "microhub_id": 2,
      "producto_id": 51,
      "tipo": "devolucion_cancelacion",
      "cantidad": 10,
      "existencia_resultante": 75,
      "referencia": {
        "tipo": "pedido",
        "id": "181"
      },
      "motivo": "Cierre del flujo de demostración",
      "usuario_id": 1,
      "fecha": "2026-11-26T15:40:00-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 411,
    "paginas": 83
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
    "existencia_resultante": 22
  },
  {
    "tipo": "salida_pedido",
    "producto_id": 51,
    "cantidad": -3,
    "existencia_resultante": 72
  },
  {
    "tipo": "devolucion_cancelacion",
    "producto_id": 32,
    "cantidad": 3,
    "existencia_resultante": 25
  },
  {
    "tipo": "devolucion_cancelacion",
    "producto_id": 51,
    "cantidad": 3,
    "existencia_resultante": 75
  }
]
```

## Servicio reportes · puerto 5123

### F3-08 · Reporte del periodo en CSV · PASA

**Objetivo.** La entrega ya cuenta en los reportes.

**Petición.** `GET http://reportes:5123/api/v1/reportes/pedidos_por_dia/exportar?formato=csv`

```http
Accept: application/json
X-Traza-Id: 27f06c42-399c-4b00-a3ca-fc165084b333
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 151 ms · traza `27f06c42-399c-4b00-a3ca-fc165084b333`

```json
﻿Día,Pedidos,Unidades,Venta,Ticket promedio,Demanda no atendida
2026-10-28,9,38,1257.30,139.70,4
2026-10-29,1,3,109.50,109.50,0
2026-10-30,1,4,101.50,101.50,0
2026-10-31,2,12,398.50,199.25,2
2026-11-01,4,20,742.00,185.50,2
2026-11-02,1,3,102.50,102.50,1
2026-11-03,3,15,530.00,176.67,2
2026-11-04,3,11,424.00,141.33,1
2026-11-05,4,22,579.50,144.88,2
2026-11-06,3,16,520.50,173.50,1
2026-11-07,4,20,600.40,150.10,0
2026-11-08,2,8,213.00,106.50,1
2026-11-09,3,16,567.50,189.17,2
2026-11-10,4,16,535.00,133.75,0
2026-11-11,4,18,594.90,148.72,2
2026-11-12,3,13,435.00,145.00,0
2026-11-13,3,13,401.00,133.67,0
2026-11-14,5,18,593.00,118.60,1
2026-11-15,2,9,304.90,152.45,1
2026-11-16,1,5,170.00,170.00,1
2026-11-17,3,17,473.50,157.83,1
2026-11-18,1,2,100.50,100.50,2
2026-11-19,7,40,1211.20,173.03,5
2026-11-20,4,20,617.90,154.47,2
2026-11-21,3,15,519.90,173.30,1
2026-11-22,5,19,619.80,123.96,2
2026-11-24,4,20,542.50,135.62,1
2026-11-25,9,54,1429.50,158.83,0
2026-11-26,6,30,1311.50,218.58,0
Total,104,497,16006.30,153.91,37

```

**Evidencia en PostgreSQL.** `SELECT reporte, formato, filas, left(sha256, 16) AS sha256 FROM reporte_exportacion ORDER BY id DESC LIMIT 1`

```json
[
  {
    "reporte": "pedidos_por_dia",
    "formato": "csv",
    "filas": 29,
    "sha256": "e895a06ad5159638"
  }
]
```
