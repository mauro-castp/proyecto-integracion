# Procesos integrales de principio a fin


Generado el 2026-11-27 05:11 contra los servicios en ejecución. 40 de 40 casos pasan.

## Servicio planeacion · puerto 5106

### F1-01 · Escritorio (XML): el planeador registra una ubicación candidata · PASA

**Objetivo.** Planeación de ubicación.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos`

```http
Accept: application/xml
X-Traza-Id: 5c2b8973-f226-44b2-8730-23e08125139a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><candidato_nuevo xmlns="urn:microhubs:v1"><clave>********</clave><nombre>Ubicación del flujo AB350</nombre><latitud>25.760195</latitud><longitud>-100.370891</longitud><renta_estimada>15000.00</renta_estimada><nomina_estimada>36000.00</nomina_estimada><servicios_estimados>6000.00</servicios_estimados><otros_costos>4000.00</otros_costos><superficie_m2>100</superficie_m2><capacidad_fisica>120</capacidad_fisica><accesibilidad_vial>8</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km></candidato_nuevo>
```

**Respuesta.** HTTP 201 (esperado 201) · 171 ms · traza `5c2b8973-f226-44b2-8730-23e08125139a`

```xml
<?xml version='1.0' encoding='utf-8'?>
<candidato xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>260</id><clave>FL-AB350</clave><nombre>Ubicación del flujo AB350</nombre><latitud>25.760195</latitud><longitud>-100.370891</longitud><renta_estimada>15000.00</renta_estimada><nomina_estimada>36000.00</nomina_estimada><servicios_estimados>6000.00</servicios_estimados><otros_costos>4000.00</otros_costos><costo_fijo>61000.00</costo_fijo><superficie_m2>100</superficie_m2><capacidad_fisica>120</capacidad_fisica><accesibilidad_vial>8</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato>
```

**Evidencia en PostgreSQL.** `SELECT id, clave, nombre, costo_fijo, decision FROM ubicacion_candidata WHERE clave = %s`

```json
[
  {
    "id": 260,
    "clave": "FL-AB350",
    "nombre": "Ubicación del flujo AB350",
    "costo_fijo": "61000.00",
    "decision": "pendiente"
  }
]
```

### F1-02 · El planeador simula la operación de la candidata · PASA

**Objetivo.** Capacidad, utilización y decisión sugerida (MongoDB).

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/260/simular`

```http
Accept: application/json
X-Traza-Id: 4e501300-7159-41f8-b365-1c3f6fbf18db
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

**Respuesta.** HTTP 200 (esperado 200) · 343 ms · traza `4e501300-7159-41f8-b365-1c3f6fbf18db`

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
X-Traza-Id: 3df68eb9-eff3-48af-9449-3b6d1ce5abae
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "candidato_id": 260,
  "pedidos_dia": 100,
  "ticket": 180,
  "margen_bruto": 0.3,
  "costos_fijos": 61000,
  "costo_variable_pedido": 22
}
```

**Respuesta.** HTTP 200 (esperado 200) · 58 ms · traza `3df68eb9-eff3-48af-9449-3b6d1ce5abae`

```json
{
  "id": null,
  "nombre": null,
  "objeto": {
    "tipo": "candidato",
    "id": 260,
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

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/260/decision`

```http
Accept: application/json
X-Traza-Id: aa83b731-c0a2-4927-a58c-fd980179471f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aceptado",
  "motivo": "Cubre la zona del cliente y la demanda esperada supera el equilibrio."
}
```

**Respuesta.** HTTP 200 (esperado 200) · 65 ms · traza `aa83b731-c0a2-4927-a58c-fd980179471f`

```json
{
  "id": 260,
  "clave": "********",
  "nombre": "Ubicación del flujo AB350",
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
X-Traza-Id: 6031fa39-63b8-4cc4-a65d-e2d13bf08826
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "clave": "********",
  "nombre": "Microhub AB350",
  "direccion": "Ubicación aprobada en planeación",
  "latitud": 25.760195,
  "longitud": -100.370891,
  "radio_km": 1.5,
  "capacidad_turno": 120
}
```

**Respuesta.** HTTP 201 (esperado 201) · 91 ms · traza `6031fa39-63b8-4cc4-a65d-e2d13bf08826`

```json
{
  "id": 12,
  "clave": "********",
  "nombre": "Microhub AB350",
  "latitud": 25.760195,
  "longitud": -100.370891,
  "radio_km": 1.5,
  "estatus": "activo"
}
```

## Servicio capacidad · puerto 5117

### F1-06 · Asignar personal al microhub · PASA

**Objetivo.** Operadores, repartidores y capacidad física.

**Petición.** `PUT http://capacidad:5117/api/v1/capacidad/recursos/12`

```http
Accept: application/json
X-Traza-Id: 2f307b3f-6a10-49e9-9e65-50d506071c58
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

**Respuesta.** HTTP 200 (esperado 200) · 197 ms · traza `2f307b3f-6a10-49e9-9e65-50d506071c58`

```json
{
  "microhub": {
    "id": 12,
    "nombre": "Microhub AB350"
  },
  "operadores": 2,
  "repartidores": 2,
  "capacidad_fisica": 120,
  "actualizado_en": "2026-11-26T23:11:40-06:00"
}
```

## Servicio usuarios · puerto 5102

### F1-07 · Crear la cuenta del operador · PASA

**Objetivo.** Cuenta nueva con su perfil y su microhub.

**Petición.** `POST http://usuarios:5102/api/v1/usuarios`

```http
Accept: application/json
X-Traza-Id: e03f8345-2d0e-4bfa-a0d2-35daa54551b7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Operador",
  "apellidos": "AB350",
  "correo": "operador.ab350@ejemplo.mx",
  "clave": "********",
  "rol": "operador",
  "microhub_id": 12
}
```

**Respuesta.** HTTP 201 (esperado 201) · 185 ms · traza `e03f8345-2d0e-4bfa-a0d2-35daa54551b7`

```json
{
  "id": 64,
  "nombre": "Operador",
  "apellidos": "AB350",
  "correo": "operador.ab350@ejemplo.mx",
  "telefono": null,
  "rol": "operador",
  "microhub": {
    "id": 12,
    "clave": "********",
    "nombre": "Microhub AB350"
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
X-Traza-Id: 343ebcc5-bf30-45aa-9ffb-d053d84451ed
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "origen_microhub_id": 1,
  "destino_microhub_id": 12,
  "producto_id": 31,
  "cantidad": 12,
  "motivo": "Inventario inicial del microhub nuevo",
  "operacion_uuid": "3ff7caa4-e691-4988-8794-94a0f644f478"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 164 ms · traza `343ebcc5-bf30-45aa-9ffb-d053d84451ed`

```json
{
  "producto_id": 31,
  "cantidad": 12,
  "duplicado": false,
  "origen": {
    "microhub_id": 1,
    "existencia": 117,
    "movimiento_id": 2603
  },
  "destino": {
    "microhub_id": 12,
    "existencia": 12,
    "movimiento_id": 2604
  }
}
```

### F1-08b · Surtir el microhub nuevo · PASA

**Objetivo.** Transferencia atómica desde MH-01.

**Petición.** `POST http://inventario:5111/api/v1/inventario/transferencias`

```http
Accept: application/json
X-Traza-Id: be910375-1121-4e27-9db4-2b9f4ee8f5b1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "origen_microhub_id": 1,
  "destino_microhub_id": 12,
  "producto_id": 36,
  "cantidad": 12,
  "motivo": "Inventario inicial del microhub nuevo",
  "operacion_uuid": "952ba379-f908-4850-a885-eb2089eb49b7"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 92 ms · traza `be910375-1121-4e27-9db4-2b9f4ee8f5b1`

```json
{
  "producto_id": 36,
  "cantidad": 12,
  "duplicado": false,
  "origen": {
    "microhub_id": 1,
    "existencia": 35,
    "movimiento_id": 2605
  },
  "destino": {
    "microhub_id": 12,
    "existencia": 12,
    "movimiento_id": 2606
  }
}
```

## Servicio pedidos · puerto 5104

### F1-09 · Android (JSON): el cliente hace su pedido · PASA

**Objetivo.** El motor lo asigna al microhub más cercano que tiene todo: el nuevo.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: 9227541e-367a-483c-a269-bd4000b8d50a
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
      "producto_id": 36,
      "cantidad": 3
    }
  ],
  "operacion_uuid": "2ba9e708-de94-4585-8b92-cc7d2ce10795"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 297 ms · traza `9227541e-367a-483c-a269-bd4000b8d50a`

```json
{
  "id": 669,
  "folio": "PED-20261126-000669",
  "estado": "asignado",
  "zona_id": 3,
  "microhub_id": 12,
  "subtotal": 312.0,
  "costo_envio": 0.0,
  "total": 312.0,
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
    "microhub_ganador_id": 12,
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
    "producto_id": 36,
    "cantidad": -3,
    "existencia_resultante": 9
  }
]
```

### F1-10 · El operador prepara el pedido · PASA

**Objetivo.** La transición la valida el motor.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/669/estado`

```http
Accept: application/json
X-Traza-Id: 7f35116e-860b-4c4f-bb07-bb2e484dbbd0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NCIs…(296 caracteres)
Content-Type: application/json
```

```json
{
  "estado": "en_preparacion"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 102 ms · traza `7f35116e-860b-4c4f-bb07-bb2e484dbbd0`

```json
{
  "id": 669,
  "folio": "PED-20261126-000669",
  "estado": "en_preparacion",
  "zona": {
    "id": 3,
    "nombre": "Paseo de San Bernabé"
  },
  "microhub_id": 12,
  "total": 312.0,
  "creado_en": "2026-11-26T23:11:41-06:00"
}
```

### F1-11 · El operador lo marca listo · PASA

**Objetivo.** Queda disponible para despacho.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/669/listo`

```http
Accept: application/json
X-Traza-Id: ab4b3a8f-41d3-474a-830a-577954ee47d7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NCIs…(296 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 200 (esperado 200) · 65 ms · traza `ab4b3a8f-41d3-474a-830a-577954ee47d7`

```json
{
  "id": 669,
  "estado": "en_preparacion",
  "listo_en": "2026-11-26T23:11:42-06:00"
}
```

## Servicio rutas · puerto 5118

### F1-12 · Proponer la ruta de despacho · PASA

**Objetivo.** Agrupa, asigna repartidor y ordena las paradas (algoritmo de rutas).

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/json
X-Traza-Id: 8883d478-e21c-4faf-91a0-200474c88dd5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NCIs…(296 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 12,
  "pedido_ids": [
    669
  ],
  "repartidor_ids": [
    7
  ],
  "metodo": "automatico",
  "guardar": true
}
```

**Respuesta.** HTTP 201 (esperado 201) · 291 ms · traza `8883d478-e21c-4faf-91a0-200474c88dd5`

```json
{
  "id": 112,
  "estado": "propuesto",
  "version": 1,
  "microhub": {
    "id": 12,
    "nombre": "Microhub AB350"
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
            "id": 669,
            "folio": "PED-20261126-000669"
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
X-Traza-Id: 465dfa76-9926-4147-a05d-0afc661c43be
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NCIs…(296 caracteres)
Content-Type: application/json
```

```json
{
  "pedido_id": 669,
  "repartidor_id": 7,
  "orden_parada": 1
}
```

**Respuesta.** HTTP 201 (esperado 201) · 96 ms · traza `465dfa76-9926-4147-a05d-0afc661c43be`

```json
{
  "entrega_id": 366,
  "pedido_id": 669,
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
    "referencia_id": "366"
  }
]
```

### F1-14 · Android: el repartidor ve su parada · PASA

**Objetivo.** Sesión validada en Redis.

**Petición.** `GET http://entregas:5105/api/v1/entregas/mias?por_pagina=50`

```http
Accept: application/json
X-Traza-Id: 9616ee3d-3d23-4735-9506-29e2d07f9df1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 56 ms · traza `9616ee3d-3d23-4735-9506-29e2d07f9df1`

```json
{
  "datos": [
    {
      "id": 366,
      "pedido_id": 669,
      "folio": "PED-20261126-000669",
      "estado_pedido": "en_ruta",
      "orden_parada": 1,
      "direccion": "Nogal 1440, Paseo de San Bernabé",
      "zona": "Paseo de San Bernabé",
      "distancia_km": null,
      "minutos_estimados": null,
      "total": 312.0
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

**Evidencia en Redis.** `SCARD auth:sesion:7`

```json
[
  {
    "comando": "SCARD auth:sesion:7",
    "valor": 25
  }
]
```

## Servicio seguimiento · puerto 5110

### F1-15 · El repartidor envía su recorrido · PASA

**Objetivo.** Puntos GPS en MongoDB (2dsphere).

**Petición.** `POST http://seguimiento:5110/api/v1/seguimiento/366/ubicaciones`

```http
Accept: application/json
X-Traza-Id: 7fe5c9ba-b063-43ae-98df-d35763b1dbfe
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "puntos": [
    {
      "latitud": 25.760195,
      "longitud": -100.370891,
      "capturado_en": "2026-11-27T05:07:42.748861+00:00"
    },
    {
      "latitud": 25.759995,
      "longitud": -100.371091,
      "capturado_en": "2026-11-27T05:10:42.748891+00:00"
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 35 ms · traza `7fe5c9ba-b063-43ae-98df-d35763b1dbfe`

```json
{
  "recibidos": 2
}
```

## Servicio documentos · puerto 5107

### F1-16 · La foto de evidencia queda en el almacén · PASA

**Objetivo.** En la base solo sus datos; se descarga con un enlace firmado.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b09110e5f817588ebd63bd2/enlace`

```http
Accept: application/json
X-Traza-Id: 756603c1-e674-4bb4-97b1-c92c92e58345
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 31 ms · traza `756603c1-e674-4bb4-97b1-c92c92e58345`

```json
{
  "id": "6b09110e5f817588ebd63bd2",
  "nombre": "evidencia-flujo1-AB350.jpg",
  "url_firmada": "http://documentos:5107/api/v1/documentos/descarga?k=document…(208 caracteres)",
  "metodo": "GET",
  "segundos": 300,
  "expira_en": "2026-11-26T23:16:42-06:00"
}
```

**Evidencia en MongoDB.** `db.documentos.findOne({_id}) sin contenido`

```json
{
  "_id": "6b09110e5f817588ebd63bd2",
  "nombre": "evidencia-flujo1-AB350.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "366"
  },
  "subido_por": 7,
  "creado_en": "2026-11-27 05:11:42.814000+00:00",
  "ruta": "documentos/2026/11/6b09110e5f817588ebd63bd2.jpg",
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

**Petición.** `POST http://entregas:5105/api/v1/entregas/366/resultado`

```http
Accept: application/json
X-Traza-Id: d54885ce-5831-4566-a010-04d9949f53a8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 312.0,
  "cambio_entregado": 0,
  "ubicacion": {
    "latitud": 25.759995,
    "longitud": -100.371091
  },
  "evidencia_ids": [
    "6b09110e5f817588ebd63bd2"
  ],
  "capturado_en": "2026-11-27T05:11:43.090298+00:00",
  "id_cliente_local": "a0f42c6d-c2bb-421e-89cb-4c26ef15a6c0"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 110 ms · traza `d54885ce-5831-4566-a010-04d9949f53a8`

```json
{
  "entrega_id": 366,
  "pedido_id": 669,
  "estado_pedido": "entregado",
  "cerrado_en": "2026-11-26T23:11:43-06:00",
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
    "usuario_id": 64,
    "proceso": null
  },
  {
    "estado_anterior": "en_preparacion",
    "estado_nuevo": "en_ruta",
    "usuario_id": 64,
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
X-Traza-Id: e8632ca9-5612-44d0-aad6-7dbd6fcdfecb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 75 ms · traza `e8632ca9-5612-44d0-aad6-7dbd6fcdfecb`

```json
{
  "datos": [
    {
      "id": 1008,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000669",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "669"
      },
      "creada_en": "2026-11-26T23:11:43-06:00"
    },
    {
      "id": 992,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261020-000065",
      "mensaje": "El pedido cambió a entrega_fallida.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "65"
      },
      "creada_en": "2026-11-26T23:10:49-06:00"
    },
    {
      "id": 980,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000655",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "655"
      },
      "creada_en": "2026-11-26T23:08:32-06:00"
    },
    {
      "id": 979,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000653",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "653"
      },
      "creada_en": "2026-11-26T23:08:30-06:00"
    },
    {
      "id": 963,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000645",
      "mensaje": "El pedido cambió a entrega_fallida.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "645"
      },
      "creada_en": "2026-11-26T23:08:05-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 26,
    "paginas": 6
  }
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F1-19 · El auditor reconstruye la historia del pedido · PASA

**Objetivo.** Bitácora, estados, inventario y archivos en una línea de tiempo.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/pedido/669`

```http
Accept: application/json
X-Traza-Id: 252b07f9-4973-4ae3-829b-5a19feedd617
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 181 ms · traza `252b07f9-4973-4ae3-829b-5a19feedd617`

```json
{
  "objeto": {
    "tipo": "pedido",
    "id": "669"
  },
  "total": 15,
  "eventos": [
    {
      "fecha": "2026-11-26T23:11:41-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "actualizado_en = 2026-11-26T23:11:41.883637-06:00; asignado_en = None; cerrado_en = None; cliente_id = 1",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "669"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": null,
          "nuevo": "2026-11-26T23:11:41.883637-06:00"
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
          "nuevo": "2026-11-26T23:11:41.883637-06:00"
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
          "nuevo": "PED-20261126-000669"
        },
        {
          "campo": "id",
          "anterior": null,
          "nuevo": "669"
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
      "fecha": "2026-11-26T23:11:41-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "asignado_en = 2026-11-26T23:11:41.883637-06:00; estado: creado → asignado; microhub_id = 12",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "669"
      },
      "cambios": [
        {
          "campo": "asignado_en",
          "anterior": null,
          "nuevo": "2026-11-26T23:11:41.883637-06:00"
        },
        {
          "campo": "estado",
          "anterior": "creado",
          "nuevo": "asignado"
        },
        {
          "campo": "microhub_id",
          "anterior": null,
          "nuevo": "12"
        }
      ]
    },
    {
      "fecha": "2026-11-26T23:11:41-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "nuevo → creado",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "669"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T23:11:41-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "creado → asignado",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "669"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T23:11:41-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -3 de producto 31 en microhub 12 (existencia 9)",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "12-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T23:11:41-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -3 de producto 36 en microhub 12 (existencia 9)",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "12-36"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T23:11:42-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-26T23:11:41.883637-06:00 → 2026-11-26T23:11:42.135016-06:00; estado: asignado → en_preparacion",
      "usuario": {
        "id": 64,
        "nombre": "Operador AB350"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "669"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-26T23:11:41.883637-06:00",
          "nuevo": "2026-11-26T23:11:42.135016-06:00"
        },
        {
          "campo": "estado",
          "anterior": "asignado",
          "nuevo": "en_preparacion"
        }
      ]
    },
    {
      "fecha": "2026-11-26T23:11:42-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "asignado → en_preparacion",
      "usuario": {
        "id": 64,
        "nombre": "Operador AB350"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "669"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T23:11:42-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "listo_en = 2026-11-26T23:11:42.232367-06:00",
      "usuario": {
        "id": 64,
        "nombre": "Operador AB350"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "669"
      },
      "cambios": [
        {
          "campo": "listo_en",
          "anterior": null,
          "nuevo": "2026-11-26T23:11:42.232367-06:00"
        }
      ]
    },
    {
      "fecha": "2026-11-26T23:11:42-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "asignada_en = 2026-11-26T23:11:42.589925-06:00; cambio_entregado = None; capturado_en = None; cerrada_por_usuario_id = None",
      "usuario": {
        "id": 64,
        "nombre": "Operador AB350"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "366"
      },
      "cambios": [
        {
          "campo": "asignada_en",
          "anterior": null,
          "nuevo": "2026-11-26T23:11:42.589925-06:00"
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
      "fecha": "2026-11-26T23:11:42-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-26T23:11:42.135016-06:00 → 2026-11-26T23:11:42.589925-06:00; estado: en_preparacion → en_ruta",
      "usuario": {
        "id": 64,
        "nombre": "Operador AB350"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "669"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-26T23:11:42.135016-06:00",
          "nuevo": "2026-11-26T23:11:42.589925-06:00"
        },
        {
          "campo": "estado",
          "anterior": "en_preparacion",
          "nuevo": "en_ruta"
        }
      ]
    },
    {
      "fecha": "2026-11-26T23:11:42-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "en_preparacion → en_ruta",
      "usuario": {
        "id": 64,
        "nombre": "Operador AB350"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "669"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T23:11:43-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "cambio_entregado = 0.0; capturado_en = 2026-11-26T23:11:43.0…(145 caracteres)",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "366"
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
          "nuevo": "2026-11-26T23:11:43.090298-06:00"
        },
        {
          "campo": "cerrada_por_usuario_id",
          "anterior": null,
          "nuevo": "7"
        },
        {
          "campo": "cierre_en",
          "anterior": null,
          "nuevo": "2026-11-26T23:11:43.135124-06:00"
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
          "nuevo": "[\"6b09110e5f817588ebd63bd2\"]"
        },
        {
          "campo": "evidencia_url",
          "anterior": null,
          "nuevo": "/api/v1/documentos/6b09110e5f817588ebd63bd2"
        },
        {
          "campo": "id_cliente_local",
          "anterior": null,
          "nuevo": "a0f42c6d-c2bb-421e-89cb-4c26ef15a6c0"
        },
        {
          "campo": "monto_cobrado",
          "anterior": null,
          "nuevo": "312.0"
        },
        {
          "campo": "resultado",
          "anterior": null,
          "nuevo": "entregado"
        }
      ]
    },
    {
      "fecha": "2026-11-26T23:11:43-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-26T23:11:42.589925-06:00 → 2026-11-2…(159 caracteres)",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "669"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-26T23:11:42.589925-06:00",
          "nuevo": "2026-11-26T23:11:43.135124-06:00"
        },
        {
          "campo": "cerrado_en",
          "anterior": null,
          "nuevo": "2026-11-26T23:11:43.135124-06:00"
        },
        {
          "campo": "estado",
          "anterior": "en_ruta",
          "nuevo": "entregado"
        }
      ]
    },
    {
      "fecha": "2026-11-26T23:11:43-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "en_ruta → entregado",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "669"
      },
      "cambios": []
    }
  ]
}
```

## Servicio reportes · puerto 5123

### F1-20 · Visualización: el microhub nuevo ya aparece en la comparación · PASA

**Objetivo.** Datos listos para Highcharts.

**Petición.** `GET http://reportes:5123/api/v1/reportes/comparacion_microhubs/grafica?microhub_id=12`

```http
Accept: application/json
X-Traza-Id: 654b4bd6-4805-4bea-8f47-e829a8ce18e1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 226 ms · traza `654b4bd6-4805-4bea-8f47-e829a8ce18e1`

```json
{
  "reporte": "comparacion_microhubs",
  "titulo": "Comparación entre microhubs",
  "tipo": "column",
  "unidad": "pedidos / MXN",
  "categorias": [
    "Microhub AB350"
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
        312.0
      ]
    }
  ]
}
```

## Servicio microhubs · puerto 5109

### F1-21 · Cierre: dar de baja el microhub de la demostración · PASA

**Objetivo.** Baja lógica; conserva su historia.

**Petición.** `DELETE http://microhubs:5109/api/v1/microhubs/12`

```http
Accept: application/json
X-Traza-Id: 2e1a5001-6b96-4744-8d1c-932211c9ebff
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 49 ms · traza `2e1a5001-6b96-4744-8d1c-932211c9ebff`

```json
(sin cuerpo)
```

## Servicio pedidos · puerto 5104

### F2-01 · Android: un cliente compra y el inventario baja · PASA

**Objetivo.** El motor descuenta inventario en la misma transacción.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: 21eae261-ea46-496e-ba62-6a9322e8a358
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
  "operacion_uuid": "20f17906-dd6d-40fb-8c01-3ef94fd79cab"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 210 ms · traza `21eae261-ea46-496e-ba62-6a9322e8a358`

```json
{
  "id": 670,
  "folio": "PED-20261126-000670",
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
    "existencia_resultante": 42
  }
]
```

## Servicio inventario · puerto 5111

### F2-02 · El operador fija el mínimo y nace la alerta · PASA

**Objetivo.** El trigger avisa del faltante.

**Petición.** `PATCH http://inventario:5111/api/v1/inventario/1/31/minimo`

```http
Accept: application/json
X-Traza-Id: 27e5eba0-0ce0-4afb-aa6c-f5f771d4365e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "minimo": 127
}
```

**Respuesta.** HTTP 200 (esperado 200) · 244 ms · traza `27e5eba0-0ce0-4afb-aa6c-f5f771d4365e`

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
  "existencia": 117,
  "minimo": 127,
  "reservado": 0,
  "disponible": 117,
  "estado": "bajo_minimo",
  "actualizado_en": "2026-11-26T23:11:45-06:00"
}
```

### F2-03 · La alerta de faltante · PASA

**Objetivo.** Qué producto, cuánto falta y qué tan grave es.

**Petición.** `GET http://inventario:5111/api/v1/inventario/alertas?microhub_id=1&por_pagina=100`

```http
Accept: application/json
X-Traza-Id: 286fd64d-371e-4f65-a980-619623430f4d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 96 ms · traza `286fd64d-371e-4f65-a980-619623430f4d`

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
        "id": 31,
        "clave_interna": "LA-003",
        "nombre": "Queso fresco"
      },
      "existencia": 117,
      "minimo": 127,
      "disponible": 117,
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
X-Traza-Id: 4a4a5179-b3d9-41c0-842d-1914d55211f7
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

**Respuesta.** HTTP 201 (esperado 201) · 136 ms · traza `4a4a5179-b3d9-41c0-842d-1914d55211f7`

```json
{
  "id": 73,
  "folio": "SC-20261126-000073",
  "microhub_id": 1,
  "estado": "pendiente",
  "motivo": "Faltante detectado por el sistema",
  "solicitada_por": 2,
  "decidida_por": null,
  "decision_motivo": null,
  "decidida_en": null,
  "creada_en": "2026-11-26T23:11:45-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/73/decision`

```http
Accept: application/json
X-Traza-Id: db5c94b3-703c-433e-9681-40dab0b6dd7f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aprobada",
  "motivo": "Con presupuesto"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 96 ms · traza `db5c94b3-703c-433e-9681-40dab0b6dd7f`

```json
{
  "id": 73,
  "folio": "SC-20261126-000073",
  "microhub_id": 1,
  "estado": "aprobada",
  "motivo": "Faltante detectado por el sistema",
  "solicitada_por": 2,
  "decidida_por": 1,
  "decision_motivo": "Con presupuesto",
  "decidida_en": "2026-11-26T23:11:45-06:00",
  "creada_en": "2026-11-26T23:11:45-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/73/ordenar`

```http
Accept: application/json
X-Traza-Id: 84dd3e81-b23c-4545-aeb1-0379b75669d9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 201 (esperado 201) · 346 ms · traza `84dd3e81-b23c-4545-aeb1-0379b75669d9`

```json
{
  "solicitud_id": 73,
  "ordenes": [
    {
      "id": 44,
      "folio": "OC-20261126-000044",
      "solicitud_id": 73,
      "proveedor": {
        "id": 1,
        "nombre": "Abarrotes del Norte"
      },
      "microhub_id": 1,
      "estado": "emitida",
      "fecha_esperada": "2026-11-28",
      "total": 4060.0,
      "creada_en": "2026-11-26T23:11:45-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/44/recepcion`

```http
Accept: application/json
X-Traza-Id: b9eac0f3-46f7-4b10-8608-26d03879bc6d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "operacion_uuid": "8f38fa56-4dc3-4d4b-8822-c7396df7b5e1",
  "nota": "Completo",
  "lineas": [
    {
      "producto_id": 31,
      "cantidad": 100
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 282 ms · traza `b9eac0f3-46f7-4b10-8608-26d03879bc6d`

```json
{
  "orden": {
    "id": 44,
    "folio": "OC-20261126-000044",
    "solicitud_id": 73,
    "proveedor": {
      "id": 1,
      "nombre": "Abarrotes del Norte"
    },
    "microhub_id": 1,
    "estado": "recibida",
    "fecha_esperada": "2026-11-28",
    "total": 4060.0,
    "creada_en": "2026-11-26T23:11:45-06:00",
    "cerrada_en": "2026-11-26T23:11:46-06:00",
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
    "existencia": 217,
    "minimo": 127
  }
]
```

## Servicio documentos · puerto 5107

### F2-08 · La remisión firmada queda en el almacén · PASA

**Objetivo.** Archivo con enlace firmado.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b091112f796dcc0841d6c9b/enlace`

```http
Accept: application/json
X-Traza-Id: 495dc142-442c-4512-809e-bd13475a330a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 28 ms · traza `495dc142-442c-4512-809e-bd13475a330a`

```json
{
  "id": "6b091112f796dcc0841d6c9b",
  "nombre": "remision-44.jpg",
  "url_firmada": "http://documentos:5107/api/v1/documentos/descarga?k=document…(197 caracteres)",
  "metodo": "GET",
  "segundos": 300,
  "expira_en": "2026-11-26T23:16:46-06:00"
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F2-09 · Trazabilidad del producto en el microhub · PASA

**Objetivo.** Salida por pedido y recepción por orden.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/inventario?microhub_id=1&producto_id=31`

```http
Accept: application/json
X-Traza-Id: f4af469f-7050-468e-b699-b43f5f09b7f2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 50 ms · traza `f4af469f-7050-468e-b699-b43f5f09b7f2`

```json
{
  "objeto": {
    "tipo": "inventario",
    "id": "1-31"
  },
  "total": 12,
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
X-Traza-Id: 6998c0f3-a6e1-4522-875c-c3424335d7d8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 187 ms · traza `6998c0f3-a6e1-4522-875c-c3424335d7d8`

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
X-Traza-Id: b0f38d91-88e7-44b1-ae9a-c4df52fd3a5f
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

**Respuesta.** HTTP 201 (esperado 201) · 274 ms · traza `b0f38d91-88e7-44b1-ae9a-c4df52fd3a5f`

```json
{
  "id": 671,
  "folio": "PED-20261126-000671",
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
X-Traza-Id: 38de5187-a222-4947-9f10-83c126eb2c41
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
Content-Type: application/json
```

```json
{
  "pedido_id": 671,
  "repartidor_id": 7
}
```

**Respuesta.** HTTP 201 (esperado 201) · 67 ms · traza `38de5187-a222-4947-9f10-83c126eb2c41`

```json
{
  "entrega_id": 367,
  "pedido_id": 671,
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
X-Traza-Id: 22ba6d93-872d-4ca2-8898-b5fae66d2edb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "c800d374-5c53-4ab4-b91e-957280f50ede",
  "dispositivo": "android-flujo-7b87fd",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "3194ef82-5d85-4759-ba82-b8fb80f256ef",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-27T04:51:48.973141+00:00",
      "datos": {
        "entrega_id": 367,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-27T04:51:48.973161+00:00"
          },
          {
            "latitud": 25.7491,
            "longitud": -100.3611,
            "capturado_en": "2026-11-27T04:56:48.973167+00:00"
          }
        ]
      }
    },
    {
      "operacion_uuid": "9b7f5638-7010-4c93-b936-f465f0548348",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-27T04:59:48.973178+00:00",
      "datos": {
        "entrega_id": 367,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "El cliente no estaba en su domicilio",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b091114f796dcc0841d6ca0"
        ],
        "capturado_en": "2026-11-27T04:59:48.973183+00:00"
      }
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 390 ms · traza `22ba6d93-872d-4ca2-8898-b5fae66d2edb`

```json
{
  "id": 212,
  "lote_uuid": "c800d374-5c53-4ab4-b91e-957280f50ede",
  "dispositivo": "android-flujo-7b87fd",
  "recibido_en": "2026-11-26T23:11:49-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 0,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "3194ef82-5d85-4759-ba82-b8fb80f256ef",
      "tipo": "ubicaciones",
      "estado": "aplicada",
      "duplicada": false,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    },
    {
      "operacion_uuid": "9b7f5638-7010-4c93-b936-f465f0548348",
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
    "creada_en": "2026-11-26 22:51:48.973141-06:00"
  },
  {
    "tipo": "entrega_resultado",
    "estado": "aplicada",
    "intentos": 1,
    "creada_en": "2026-11-26 22:59:48.973178-06:00"
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
X-Traza-Id: 26a1e77e-429e-407b-a5f1-cb2735e05023
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "c800d374-5c53-4ab4-b91e-957280f50ede",
  "dispositivo": "android-flujo-7b87fd",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "3194ef82-5d85-4759-ba82-b8fb80f256ef",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-27T04:51:48.973141+00:00",
      "datos": {
        "entrega_id": 367,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-27T04:51:48.973161+00:00"
          },
          {
            "latitud": 25.7491,
            "longitud": -100.3611,
            "capturado_en": "2026-11-27T04:56:48.973167+00:00"
          }
        ]
      }
    },
    {
      "operacion_uuid": "9b7f5638-7010-4c93-b936-f465f0548348",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-27T04:59:48.973178+00:00",
      "datos": {
        "entrega_id": 367,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "El cliente no estaba en su domicilio",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b091114f796dcc0841d6ca0"
        ],
        "capturado_en": "2026-11-27T04:59:48.973183+00:00"
      }
    }
  ]
}
```

**Respuesta.** HTTP 200 (esperado 200) · 153 ms · traza `26a1e77e-429e-407b-a5f1-cb2735e05023`

```json
{
  "id": 212,
  "lote_uuid": "c800d374-5c53-4ab4-b91e-957280f50ede",
  "dispositivo": "android-flujo-7b87fd",
  "recibido_en": "2026-11-26T23:11:49-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 2,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "3194ef82-5d85-4759-ba82-b8fb80f256ef",
      "tipo": "ubicaciones",
      "estado": "aplicada",
      "duplicada": true,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    },
    {
      "operacion_uuid": "9b7f5638-7010-4c93-b936-f465f0548348",
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
X-Traza-Id: 7b9d1b77-db41-42e8-9382-5946b8029b07
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 43 ms · traza `7b9d1b77-db41-42e8-9382-5946b8029b07`

```json
{
  "datos": [
    {
      "id": 1015,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000671",
      "mensaje": "El pedido cambió a entrega_fallida.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "671"
      },
      "creada_en": "2026-11-26T23:11:49-06:00"
    },
    {
      "id": 1013,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000670",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "670"
      },
      "creada_en": "2026-11-26T23:11:46-06:00"
    },
    {
      "id": 1008,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000669",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "669"
      },
      "creada_en": "2026-11-26T23:11:43-06:00"
    },
    {
      "id": 992,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261020-000065",
      "mensaje": "El pedido cambió a entrega_fallida.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "65"
      },
      "creada_en": "2026-11-26T23:10:49-06:00"
    },
    {
      "id": 980,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000655",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "655"
      },
      "creada_en": "2026-11-26T23:08:32-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 28,
    "paginas": 6
  }
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F3-06 · El auditor revisa la entrega · PASA

**Objetivo.** Bitácora y archivos de la entrega.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/entrega/367`

```http
Accept: application/json
X-Traza-Id: 977ca79d-d7ac-47df-9f85-884a2a28cbf5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 55 ms · traza `977ca79d-d7ac-47df-9f85-884a2a28cbf5`

```json
{
  "objeto": {
    "tipo": "entrega",
    "id": "367"
  },
  "total": 3,
  "eventos": [
    {
      "fecha": "2026-11-26T23:11:48-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "asignada_en = 2026-11-26T23:11:48.865619-06:00; cambio_entregado = None; capturado_en = None; cerrada_por_usuario_id = None",
      "usuario": {
        "id": 3,
        "nombre": "María José Cedillo Mata"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "367"
      },
      "cambios": [
        {
          "campo": "asignada_en",
          "anterior": null,
          "nuevo": "2026-11-26T23:11:48.865619-06:00"
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
      "fecha": "2026-11-26T23:11:48-06:00",
      "origen": "documentos",
      "accion": "documento_subido",
      "descripcion": "evidencia-flujo3-367.jpg (276 bytes, sha256 7f6025cd8a98…)",
      "usuario": {
        "id": 7,
        "nombre": null
      },
      "entidad": {
        "tipo": "documento",
        "id": "6b091114f796dcc0841d6ca0"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T23:11:49-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "cambio_entregado = 0.0; capturado_en = 2026-11-26T22:59:48.9…(144 caracteres)",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "367"
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
          "nuevo": "2026-11-26T22:59:48.973183-06:00"
        },
        {
          "campo": "cerrada_por_usuario_id",
          "anterior": null,
          "nuevo": "7"
        },
        {
          "campo": "cierre_en",
          "anterior": null,
          "nuevo": "2026-11-26T23:11:49.20354-06:00"
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
          "nuevo": "[\"6b091114f796dcc0841d6ca0\"]"
        },
        {
          "campo": "evidencia_url",
          "anterior": null,
          "nuevo": "/api/v1/documentos/6b091114f796dcc0841d6ca0"
        },
        {
          "campo": "id_cliente_local",
          "anterior": null,
          "nuevo": "9b7f5638-7010-4c93-b936-f465f0548348"
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
X-Traza-Id: bdbdc229-6aed-4ebb-a13b-23c2bd95caa2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 56 ms · traza `bdbdc229-6aed-4ebb-a13b-23c2bd95caa2`

```json
{
  "datos": [
    {
      "id": 2615,
      "microhub_id": 2,
      "producto_id": 51,
      "tipo": "devolucion_cancelacion",
      "cantidad": 3,
      "existencia_resultante": 67,
      "referencia": {
        "tipo": "pedido",
        "id": "671"
      },
      "motivo": "Entrega fallida: la mercancía regresa al microhub.",
      "usuario_id": 7,
      "fecha": "2026-11-26T23:11:49-06:00"
    },
    {
      "id": 2614,
      "microhub_id": 2,
      "producto_id": 32,
      "tipo": "devolucion_cancelacion",
      "cantidad": 3,
      "existencia_resultante": 24,
      "referencia": {
        "tipo": "pedido",
        "id": "671"
      },
      "motivo": "Entrega fallida: la mercancía regresa al microhub.",
      "usuario_id": 7,
      "fecha": "2026-11-26T23:11:49-06:00"
    },
    {
      "id": 2613,
      "microhub_id": 2,
      "producto_id": 51,
      "tipo": "salida_pedido",
      "cantidad": -3,
      "existencia_resultante": 64,
      "referencia": {
        "tipo": "pedido",
        "id": "671"
      },
      "motivo": null,
      "usuario_id": 9,
      "fecha": "2026-11-26T23:11:48-06:00"
    },
    {
      "id": 2612,
      "microhub_id": 2,
      "producto_id": 32,
      "tipo": "salida_pedido",
      "cantidad": -3,
      "existencia_resultante": 21,
      "referencia": {
        "tipo": "pedido",
        "id": "671"
      },
      "motivo": null,
      "usuario_id": 9,
      "fecha": "2026-11-26T23:11:48-06:00"
    },
    {
      "id": 2611,
      "microhub_id": 2,
      "producto_id": 31,
      "tipo": "devolucion_cancelacion",
      "cantidad": 10,
      "existencia_resultante": 52,
      "referencia": {
        "tipo": "pedido",
        "id": "670"
      },
      "motivo": "Cierre del flujo de demostración",
      "usuario_id": 1,
      "fecha": "2026-11-26T23:11:46-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 884,
    "paginas": 177
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
    "existencia_resultante": 21
  },
  {
    "tipo": "salida_pedido",
    "producto_id": 51,
    "cantidad": -3,
    "existencia_resultante": 64
  },
  {
    "tipo": "devolucion_cancelacion",
    "producto_id": 32,
    "cantidad": 3,
    "existencia_resultante": 24
  },
  {
    "tipo": "devolucion_cancelacion",
    "producto_id": 51,
    "cantidad": 3,
    "existencia_resultante": 67
  }
]
```

## Servicio reportes · puerto 5123

### F3-08 · Reporte del periodo en CSV · PASA

**Objetivo.** La entrega ya cuenta en los reportes.

**Petición.** `GET http://reportes:5123/api/v1/reportes/pedidos_por_dia/exportar?formato=csv`

```http
Accept: application/json
X-Traza-Id: b3bd13a4-be28-4ff3-87cb-917fb226d42c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 178 ms · traza `b3bd13a4-be28-4ff3-87cb-917fb226d42c`

```json
﻿Día,Pedidos,Unidades,Venta,Ticket promedio,Demanda no atendida
2026-11-25,56,282,8032.40,143.44,0
2026-11-26,180,916,29161.80,162.01,5
Total,236,1198,37194.20,157.60,5

```

**Evidencia en PostgreSQL.** `SELECT reporte, formato, filas, left(sha256, 16) AS sha256 FROM reporte_exportacion ORDER BY id DESC LIMIT 1`

```json
[
  {
    "reporte": "pedidos_por_dia",
    "formato": "csv",
    "filas": 2,
    "sha256": "8881ab5b093be25c"
  }
]
```
