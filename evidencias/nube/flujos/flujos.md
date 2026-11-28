# Procesos integrales de principio a fin


Generado el 2026-11-28 02:31 contra los servicios en ejecución. 41 de 41 casos pasan.

## Servicio planeacion · puerto 5106

### F1-01 · Escritorio (XML): el planeador registra una ubicación candidata · PASA

**Objetivo.** Planeación de ubicación.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos`

```http
Accept: application/xml
X-Traza-Id: 826ad6c3-1645-4a6f-8898-15d3778d1709
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><candidato_nuevo xmlns="urn:microhubs:v1"><clave>********</clave><nombre>Ubicación del flujo C04AC</nombre><latitud>25.760195</latitud><longitud>-100.370891</longitud><renta_estimada>15000.00</renta_estimada><nomina_estimada>36000.00</nomina_estimada><servicios_estimados>6000.00</servicios_estimados><otros_costos>4000.00</otros_costos><superficie_m2>100</superficie_m2><capacidad_fisica>120</capacidad_fisica><accesibilidad_vial>8</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km></candidato_nuevo>
```

**Respuesta.** HTTP 201 (esperado 201) · 47 ms · traza `826ad6c3-1645-4a6f-8898-15d3778d1709`

```xml
<?xml version='1.0' encoding='utf-8'?>
<candidato xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>232</id><clave>FL-C04AC</clave><nombre>Ubicación del flujo C04AC</nombre><latitud>25.760195</latitud><longitud>-100.370891</longitud><renta_estimada>15000.00</renta_estimada><nomina_estimada>36000.00</nomina_estimada><servicios_estimados>6000.00</servicios_estimados><otros_costos>4000.00</otros_costos><costo_fijo>61000.00</costo_fijo><superficie_m2>100</superficie_m2><capacidad_fisica>120</capacidad_fisica><accesibilidad_vial>8</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato>
```

**Evidencia en PostgreSQL.** `SELECT id, clave, nombre, costo_fijo, decision FROM ubicacion_candidata WHERE clave = %s`

```json
[
  {
    "id": 232,
    "clave": "FL-C04AC",
    "nombre": "Ubicación del flujo C04AC",
    "costo_fijo": "61000.00",
    "decision": "pendiente"
  }
]
```

### F1-02 · El planeador simula la operación de la candidata · PASA

**Objetivo.** Capacidad, utilización y decisión sugerida (MongoDB).

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/232/simular`

```http
Accept: application/json
X-Traza-Id: f0387757-c5d8-4c12-9ab6-1996ddabf463
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

**Respuesta.** HTTP 200 (esperado 200) · 200 ms · traza `f0387757-c5d8-4c12-9ab6-1996ddabf463`

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
X-Traza-Id: 96df7b65-fa12-46cf-9f65-599914e01486
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "candidato_id": 232,
  "pedidos_dia": 100,
  "ticket": 180,
  "margen_bruto": 0.3,
  "costos_fijos": 61000,
  "costo_variable_pedido": 22
}
```

**Respuesta.** HTTP 200 (esperado 200) · 24 ms · traza `96df7b65-fa12-46cf-9f65-599914e01486`

```json
{
  "id": null,
  "nombre": null,
  "objeto": {
    "tipo": "candidato",
    "id": 232,
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

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/232/decision`

```http
Accept: application/json
X-Traza-Id: 18bcc53e-75a6-4a1f-88bb-981fb2904279
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aceptado",
  "motivo": "Cubre la zona del cliente y la demanda esperada supera el equilibrio."
}
```

**Respuesta.** HTTP 200 (esperado 200) · 44 ms · traza `18bcc53e-75a6-4a1f-88bb-981fb2904279`

```json
{
  "id": 232,
  "clave": "********",
  "nombre": "Ubicación del flujo C04AC",
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
X-Traza-Id: 678ee578-0666-4299-884c-6008190fcebd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "clave": "********",
  "nombre": "Microhub C04AC",
  "direccion": "Ubicación aprobada en planeación",
  "latitud": 25.760195,
  "longitud": -100.370891,
  "radio_km": 1.5,
  "capacidad_turno": 120
}
```

**Respuesta.** HTTP 201 (esperado 201) · 47 ms · traza `678ee578-0666-4299-884c-6008190fcebd`

```json
{
  "id": 16,
  "clave": "********",
  "nombre": "Microhub C04AC",
  "latitud": 25.760195,
  "longitud": -100.370891,
  "radio_km": 1.5,
  "estatus": "activo"
}
```

## Servicio capacidad · puerto 5117

### F1-06 · Asignar personal al microhub · PASA

**Objetivo.** Operadores, repartidores y capacidad física.

**Petición.** `PUT http://capacidad:5117/api/v1/capacidad/recursos/16`

```http
Accept: application/json
X-Traza-Id: c3956ebb-c9f6-418f-a2c1-21c01827f3ae
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

**Respuesta.** HTTP 200 (esperado 200) · 114 ms · traza `c3956ebb-c9f6-418f-a2c1-21c01827f3ae`

```json
{
  "microhub": {
    "id": 16,
    "nombre": "Microhub C04AC"
  },
  "operadores": 2,
  "repartidores": 2,
  "capacidad_fisica": 120,
  "actualizado_en": "2026-11-27T20:31:26-06:00"
}
```

## Servicio usuarios · puerto 5102

### F1-07 · Crear la cuenta del operador · PASA

**Objetivo.** Cuenta nueva con su perfil y su microhub.

**Petición.** `POST http://usuarios:5102/api/v1/usuarios`

```http
Accept: application/json
X-Traza-Id: e67b0967-a29b-4b54-a3bd-aae5d39d8f1b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Operador",
  "apellidos": "C04AC",
  "correo": "operador.c04ac@ejemplo.mx",
  "clave": "********",
  "rol": "operador",
  "microhub_id": 16
}
```

**Respuesta.** HTTP 201 (esperado 201) · 112 ms · traza `e67b0967-a29b-4b54-a3bd-aae5d39d8f1b`

```json
{
  "id": 64,
  "nombre": "Operador",
  "apellidos": "C04AC",
  "correo": "operador.c04ac@ejemplo.mx",
  "telefono": null,
  "rol": "operador",
  "microhub": {
    "id": 16,
    "clave": "********",
    "nombre": "Microhub C04AC"
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
X-Traza-Id: ef903629-a9d6-4799-98f0-bffe85a3f143
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "origen_microhub_id": 1,
  "destino_microhub_id": 16,
  "producto_id": 51,
  "cantidad": 12,
  "motivo": "Inventario inicial del microhub nuevo",
  "operacion_uuid": "685638fb-4cbd-4fc1-937b-6cc738535a30"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 71 ms · traza `ef903629-a9d6-4799-98f0-bffe85a3f143`

```json
{
  "producto_id": 51,
  "cantidad": 12,
  "duplicado": false,
  "origen": {
    "microhub_id": 1,
    "existencia": 557,
    "movimiento_id": 2958
  },
  "destino": {
    "microhub_id": 16,
    "existencia": 12,
    "movimiento_id": 2959
  }
}
```

### F1-08b · Surtir el microhub nuevo · PASA

**Objetivo.** Transferencia atómica desde MH-01.

**Petición.** `POST http://inventario:5111/api/v1/inventario/transferencias`

```http
Accept: application/json
X-Traza-Id: a2a05d96-801e-4e9b-b681-b2304ab44b7e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "origen_microhub_id": 1,
  "destino_microhub_id": 16,
  "producto_id": 18,
  "cantidad": 12,
  "motivo": "Inventario inicial del microhub nuevo",
  "operacion_uuid": "6557390f-0559-4b7b-bbeb-34f69214194c"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 74 ms · traza `a2a05d96-801e-4e9b-b681-b2304ab44b7e`

```json
{
  "producto_id": 18,
  "cantidad": 12,
  "duplicado": false,
  "origen": {
    "microhub_id": 1,
    "existencia": 44,
    "movimiento_id": 2960
  },
  "destino": {
    "microhub_id": 16,
    "existencia": 12,
    "movimiento_id": 2961
  }
}
```

## Servicio pedidos · puerto 5104

### F1-09 · Android (JSON): el cliente hace su pedido · PASA

**Objetivo.** El motor lo asigna al microhub más cercano que tiene todo: el nuevo.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: fac77bad-75e1-485e-b915-7a661809a107
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
      "producto_id": 18,
      "cantidad": 3
    }
  ],
  "operacion_uuid": "60b060b3-66bb-4e30-badf-99e43edd3c74"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 187 ms · traza `fac77bad-75e1-485e-b915-7a661809a107`

```json
{
  "id": 702,
  "folio": "PED-20261127-000702",
  "estado": "asignado",
  "zona_id": 3,
  "microhub_id": 16,
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
    "microhub_ganador_id": 16,
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
    "producto_id": 51,
    "cantidad": -3,
    "existencia_resultante": 9
  }
]
```

### F1-10 · El operador prepara el pedido · PASA

**Objetivo.** La transición la valida el motor.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/702/estado`

```http
Accept: application/json
X-Traza-Id: d2bc5b46-5623-4ff0-b87b-d47e4a93ab1c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NCIs…(296 caracteres)
Content-Type: application/json
```

```json
{
  "estado": "en_preparacion"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 72 ms · traza `d2bc5b46-5623-4ff0-b87b-d47e4a93ab1c`

```json
{
  "id": 702,
  "folio": "PED-20261127-000702",
  "estado": "en_preparacion",
  "zona": {
    "id": 3,
    "nombre": "Paseo de San Bernabé"
  },
  "microhub_id": 16,
  "total": 336.0,
  "creado_en": "2026-11-27T20:31:26-06:00"
}
```

### F1-11 · El operador lo marca listo · PASA

**Objetivo.** Queda disponible para despacho.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/702/listo`

```http
Accept: application/json
X-Traza-Id: 95f64897-a603-4e52-ba55-736dced91e74
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NCIs…(296 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 200 (esperado 200) · 56 ms · traza `95f64897-a603-4e52-ba55-736dced91e74`

```json
{
  "id": 702,
  "estado": "en_preparacion",
  "listo_en": "2026-11-27T20:31:27-06:00"
}
```

## Servicio usuarios · puerto 5102

### F1-07b · Crear la cuenta del repartidor del microhub · PASA

**Objetivo.** RN41: cada repartidor pertenece a un microhub.

**Petición.** `POST http://usuarios:5102/api/v1/usuarios`

```http
Accept: application/json
X-Traza-Id: 06ff6304-9bf2-4c6e-927f-1cf4e9e5606a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Repartidor",
  "apellidos": "C04AC",
  "correo": "repartidor.c04ac@ejemplo.mx",
  "clave": "********",
  "rol": "repartidor",
  "microhub_id": 16
}
```

**Respuesta.** HTTP 201 (esperado 201) · 128 ms · traza `06ff6304-9bf2-4c6e-927f-1cf4e9e5606a`

```json
{
  "id": 65,
  "nombre": "Repartidor",
  "apellidos": "C04AC",
  "correo": "repartidor.c04ac@ejemplo.mx",
  "telefono": null,
  "rol": "repartidor",
  "microhub": {
    "id": 16,
    "clave": "********",
    "nombre": "Microhub C04AC"
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
X-Traza-Id: a7de66bf-d0ce-4a11-a9a8-a383e374f278
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NCIs…(296 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 16,
  "pedido_ids": [
    702
  ],
  "repartidor_ids": [
    65
  ],
  "metodo": "automatico",
  "guardar": true
}
```

**Respuesta.** HTTP 201 (esperado 201) · 174 ms · traza `a7de66bf-d0ce-4a11-a9a8-a383e374f278`

```json
{
  "id": 34,
  "estado": "propuesto",
  "version": 1,
  "microhub": {
    "id": 16,
    "nombre": "Microhub C04AC"
  },
  "fecha": "2026-11-27",
  "metodo_pedido": "automatico",
  "rutas": [
    {
      "repartidor": {
        "id": 65,
        "nombre": "Repartidor C04AC"
      },
      "metodo": "TSP exacto",
      "zonas": [
        "Paseo de San Bernabé"
      ],
      "paradas": [
        {
          "orden": 1,
          "pedido": {
            "id": 702,
            "folio": "PED-20261127-000702"
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
X-Traza-Id: 328bfc16-1b12-4758-ad18-dc82830eac2b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NCIs…(296 caracteres)
Content-Type: application/json
```

```json
{
  "pedido_id": 702,
  "repartidor_id": 65,
  "orden_parada": 1
}
```

**Respuesta.** HTTP 201 (esperado 201) · 63 ms · traza `328bfc16-1b12-4758-ad18-dc82830eac2b`

```json
{
  "entrega_id": 219,
  "pedido_id": 702,
  "repartidor_id": 65,
  "estado_pedido": "en_ruta"
}
```

**Evidencia en PostgreSQL.** `SELECT titulo, tipo, referencia_id FROM web_notificacion WHERE destinatario_id = %s ORDER BY id DESC LIMIT 1`

```json
[
  {
    "titulo": "Nueva entrega asignada",
    "tipo": "entrega",
    "referencia_id": "219"
  }
]
```

### F1-14 · Android: el repartidor ve su parada · PASA

**Objetivo.** Sesión validada en Redis.

**Petición.** `GET http://entregas:5105/api/v1/entregas/mias?por_pagina=50`

```http
Accept: application/json
X-Traza-Id: b8e8e77c-8801-4380-bd68-6b7a77d16898
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NSIs…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 57 ms · traza `b8e8e77c-8801-4380-bd68-6b7a77d16898`

```json
{
  "datos": [
    {
      "id": 219,
      "pedido_id": 702,
      "folio": "PED-20261127-000702",
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
    "total": 1,
    "paginas": 1
  }
}
```

**Evidencia en Redis.** `SCARD auth:sesion:65`

```json
[
  {
    "comando": "SCARD auth:sesion:65",
    "valor": 1
  }
]
```

## Servicio seguimiento · puerto 5110

### F1-15 · El repartidor envía su recorrido · PASA

**Objetivo.** Puntos GPS en MongoDB (2dsphere).

**Petición.** `POST http://seguimiento:5110/api/v1/seguimiento/219/ubicaciones`

```http
Accept: application/json
X-Traza-Id: 57e3756d-9a35-4711-8d89-32bfb19715a5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NSIs…(302 caracteres)
Content-Type: application/json
```

```json
{
  "puntos": [
    {
      "latitud": 25.760195,
      "longitud": -100.370891,
      "capturado_en": "2026-11-28T02:27:27.760677+00:00"
    },
    {
      "latitud": 25.759995,
      "longitud": -100.371091,
      "capturado_en": "2026-11-28T02:30:27.760703+00:00"
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 29 ms · traza `57e3756d-9a35-4711-8d89-32bfb19715a5`

```json
{
  "recibidos": 2
}
```

## Servicio documentos · puerto 5107

### F1-16 · La foto de evidencia queda en el almacén · PASA

**Objetivo.** En la base solo sus datos; se descarga con un enlace firmado.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b0a3cff342f910fc3b1766a/enlace`

```http
Accept: application/json
X-Traza-Id: 0cf9e046-7a81-4955-b552-84aae23c1f5c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 122 ms · traza `0cf9e046-7a81-4955-b552-84aae23c1f5c`

```json
{
  "id": "6b0a3cff342f910fc3b1766a",
  "nombre": "evidencia-flujo1-C04AC.jpg",
  "url_firmada": "https://storage.googleapis.com/microhubs-evidencias-637044/d…(1005 caracteres)",
  "metodo": "GET",
  "segundos": 300,
  "expira_en": "2026-11-27T20:36:27-06:00"
}
```

**Evidencia en MongoDB.** `db.documentos.findOne({_id}) sin contenido`

```json
{
  "_id": "6b0a3cff342f910fc3b1766a",
  "nombre": "evidencia-flujo1-C04AC.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "219"
  },
  "subido_por": 65,
  "creado_en": "2026-11-28 02:31:27.816000+00:00",
  "ruta": "documentos/2026/11/6b0a3cff342f910fc3b1766a.jpg",
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

**Petición.** `POST http://entregas:5105/api/v1/entregas/219/resultado`

```http
Accept: application/json
X-Traza-Id: 8cc5a2ff-b56b-4aa2-9768-19ef41d35e60
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NSIs…(302 caracteres)
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
    "6b0a3cff342f910fc3b1766a"
  ],
  "capturado_en": "2026-11-28T02:31:28.118058+00:00",
  "id_cliente_local": "53aad664-6f17-446c-a844-65e266ef778a"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 80 ms · traza `8cc5a2ff-b56b-4aa2-9768-19ef41d35e60`

```json
{
  "entrega_id": 219,
  "pedido_id": 702,
  "estado_pedido": "entregado",
  "cerrado_en": "2026-11-27T20:31:28-06:00",
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
    "usuario_id": 65,
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
X-Traza-Id: 31043eba-ec2b-48b1-b215-a0c5865f5ee1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 37 ms · traza `31043eba-ec2b-48b1-b215-a0c5865f5ee1`

```json
{
  "datos": [
    {
      "id": 770,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000702",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "702"
      },
      "creada_en": "2026-11-27T20:31:28-06:00"
    },
    {
      "id": 768,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000701",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "701"
      },
      "creada_en": "2026-11-27T20:31:04-06:00"
    },
    {
      "id": 763,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000700",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "700"
      },
      "creada_en": "2026-11-27T20:31:01-06:00"
    },
    {
      "id": 760,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000698",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "698"
      },
      "creada_en": "2026-11-27T20:29:42-06:00"
    },
    {
      "id": 732,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000689",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "689"
      },
      "creada_en": "2026-11-27T20:28:50-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 361,
    "paginas": 73
  }
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F1-19 · El auditor reconstruye la historia del pedido · PASA

**Objetivo.** Bitácora, estados, inventario y archivos en una línea de tiempo.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/pedido/702`

```http
Accept: application/json
X-Traza-Id: 2c19097e-4ed1-4080-a49c-cff1ced7dc13
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 75 ms · traza `2c19097e-4ed1-4080-a49c-cff1ced7dc13`

```json
{
  "objeto": {
    "tipo": "pedido",
    "id": "702"
  },
  "total": 15,
  "eventos": [
    {
      "fecha": "2026-11-27T20:31:26-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "actualizado_en = 2026-11-27T20:31:26.818958-06:00; asignado_en = None; cerrado_en = None; cliente_id = 1",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "702"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": null,
          "nuevo": "2026-11-27T20:31:26.818958-06:00"
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
          "nuevo": "2026-11-27T20:31:26.818958-06:00"
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
          "nuevo": "PED-20261127-000702"
        },
        {
          "campo": "id",
          "anterior": null,
          "nuevo": "702"
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
      "fecha": "2026-11-27T20:31:26-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "asignado_en = 2026-11-27T20:31:26.818958-06:00; estado: creado → asignado; microhub_id = 16",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "702"
      },
      "cambios": [
        {
          "campo": "asignado_en",
          "anterior": null,
          "nuevo": "2026-11-27T20:31:26.818958-06:00"
        },
        {
          "campo": "estado",
          "anterior": "creado",
          "nuevo": "asignado"
        },
        {
          "campo": "microhub_id",
          "anterior": null,
          "nuevo": "16"
        }
      ]
    },
    {
      "fecha": "2026-11-27T20:31:26-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "nuevo → creado",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "702"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T20:31:26-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "creado → asignado",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "702"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T20:31:26-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -3 de producto 18 en microhub 16 (existencia 9)",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "16-18"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T20:31:26-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -3 de producto 51 en microhub 16 (existencia 9)",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "16-51"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T20:31:26-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-27T20:31:26.818958-06:00 → 2026-11-27T20:31:26.972994-06:00; estado: asignado → en_preparacion",
      "usuario": {
        "id": 64,
        "nombre": "Operador C04AC"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "702"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-27T20:31:26.818958-06:00",
          "nuevo": "2026-11-27T20:31:26.972994-06:00"
        },
        {
          "campo": "estado",
          "anterior": "asignado",
          "nuevo": "en_preparacion"
        }
      ]
    },
    {
      "fecha": "2026-11-27T20:31:26-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "asignado → en_preparacion",
      "usuario": {
        "id": 64,
        "nombre": "Operador C04AC"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "702"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T20:31:27-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "listo_en = 2026-11-27T20:31:27.051052-06:00",
      "usuario": {
        "id": 64,
        "nombre": "Operador C04AC"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "702"
      },
      "cambios": [
        {
          "campo": "listo_en",
          "anterior": null,
          "nuevo": "2026-11-27T20:31:27.051052-06:00"
        }
      ]
    },
    {
      "fecha": "2026-11-27T20:31:27-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "asignada_en = 2026-11-27T20:31:27.639328-06:00; cambio_entregado = None; capturado_en = None; cerrada_por_usuario_id = None",
      "usuario": {
        "id": 64,
        "nombre": "Operador C04AC"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "219"
      },
      "cambios": [
        {
          "campo": "asignada_en",
          "anterior": null,
          "nuevo": "2026-11-27T20:31:27.639328-06:00"
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
      "fecha": "2026-11-27T20:31:27-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-27T20:31:26.972994-06:00 → 2026-11-27T20:31:27.639328-06:00; estado: en_preparacion → en_ruta",
      "usuario": {
        "id": 64,
        "nombre": "Operador C04AC"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "702"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-27T20:31:26.972994-06:00",
          "nuevo": "2026-11-27T20:31:27.639328-06:00"
        },
        {
          "campo": "estado",
          "anterior": "en_preparacion",
          "nuevo": "en_ruta"
        }
      ]
    },
    {
      "fecha": "2026-11-27T20:31:27-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "en_preparacion → en_ruta",
      "usuario": {
        "id": 64,
        "nombre": "Operador C04AC"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "702"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T20:31:28-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "cambio_entregado = 0.0; capturado_en = 2026-11-27T20:31:28.1…(146 caracteres)",
      "usuario": {
        "id": 65,
        "nombre": "Repartidor C04AC"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "219"
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
          "nuevo": "2026-11-27T20:31:28.118058-06:00"
        },
        {
          "campo": "cerrada_por_usuario_id",
          "anterior": null,
          "nuevo": "65"
        },
        {
          "campo": "cierre_en",
          "anterior": null,
          "nuevo": "2026-11-27T20:31:28.157899-06:00"
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
          "nuevo": "[\"6b0a3cff342f910fc3b1766a\"]"
        },
        {
          "campo": "evidencia_url",
          "anterior": null,
          "nuevo": "/api/v1/documentos/6b0a3cff342f910fc3b1766a"
        },
        {
          "campo": "id_cliente_local",
          "anterior": null,
          "nuevo": "53aad664-6f17-446c-a844-65e266ef778a"
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
      "fecha": "2026-11-27T20:31:28-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-27T20:31:27.639328-06:00 → 2026-11-2…(159 caracteres)",
      "usuario": {
        "id": 65,
        "nombre": "Repartidor C04AC"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "702"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-27T20:31:27.639328-06:00",
          "nuevo": "2026-11-27T20:31:28.157899-06:00"
        },
        {
          "campo": "cerrado_en",
          "anterior": null,
          "nuevo": "2026-11-27T20:31:28.157899-06:00"
        },
        {
          "campo": "estado",
          "anterior": "en_ruta",
          "nuevo": "entregado"
        }
      ]
    },
    {
      "fecha": "2026-11-27T20:31:28-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "en_ruta → entregado",
      "usuario": {
        "id": 65,
        "nombre": "Repartidor C04AC"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "702"
      },
      "cambios": []
    }
  ]
}
```

## Servicio reportes · puerto 5123

### F1-20 · Visualización: el microhub nuevo ya aparece en la comparación · PASA

**Objetivo.** Datos listos para Highcharts.

**Petición.** `GET http://reportes:5123/api/v1/reportes/comparacion_microhubs/grafica?microhub_id=16`

```http
Accept: application/json
X-Traza-Id: 2abac76f-c16f-43a9-9ba4-cd43bf1d75a5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 100 ms · traza `2abac76f-c16f-43a9-9ba4-cd43bf1d75a5`

```json
{
  "reporte": "comparacion_microhubs",
  "titulo": "Comparación entre microhubs",
  "tipo": "column",
  "unidad": "pedidos / MXN",
  "categorias": [
    "Microhub C04AC"
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

**Petición.** `DELETE http://microhubs:5109/api/v1/microhubs/16`

```http
Accept: application/json
X-Traza-Id: 4fc9f223-3e19-428e-9261-4dca19e407df
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 89 ms · traza `4fc9f223-3e19-428e-9261-4dca19e407df`

```json
(sin cuerpo)
```

## Servicio pedidos · puerto 5104

### F2-01 · Android: un cliente compra y el inventario baja · PASA

**Objetivo.** El motor descuenta inventario en la misma transacción.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: b866aff5-f2a7-4739-845e-ef1b4cbfcc07
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
  "operacion_uuid": "2c428356-e53c-4836-921d-30c93534fea5"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 225 ms · traza `b866aff5-f2a7-4739-845e-ef1b4cbfcc07`

```json
{
  "id": 703,
  "folio": "PED-20261127-000703",
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
    "existencia_resultante": 50
  }
]
```

## Servicio inventario · puerto 5111

### F2-02 · El operador fija el mínimo y nace la alerta · PASA

**Objetivo.** El trigger avisa del faltante.

**Petición.** `PATCH http://inventario:5111/api/v1/inventario/1/51/minimo`

```http
Accept: application/json
X-Traza-Id: eacb65af-015d-4175-a4a2-2d1be215eb55
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "minimo": 567
}
```

**Respuesta.** HTTP 200 (esperado 200) · 222 ms · traza `eacb65af-015d-4175-a4a2-2d1be215eb55`

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
  "existencia": 557,
  "minimo": 567,
  "reservado": 0,
  "disponible": 557,
  "estado": "bajo_minimo",
  "actualizado_en": "2026-11-27T20:31:29-06:00"
}
```

### F2-03 · La alerta de faltante · PASA

**Objetivo.** Qué producto, cuánto falta y qué tan grave es.

**Petición.** `GET http://inventario:5111/api/v1/inventario/alertas?microhub_id=1&por_pagina=100`

```http
Accept: application/json
X-Traza-Id: 504faeab-8eb1-43b5-a6bd-53e15cfe1a62
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 83 ms · traza `504faeab-8eb1-43b5-a6bd-53e15cfe1a62`

```json
{
  "datos": [
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
      "existencia": 557,
      "minimo": 567,
      "disponible": 557,
      "faltante": 10,
      "severidad": "baja"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 34,
        "clave_interna": "LA-006",
        "nombre": "Yogur natural"
      },
      "existencia": 7,
      "minimo": 8,
      "disponible": 7,
      "faltante": 1,
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
X-Traza-Id: fc431121-cc1d-4dde-8024-c1a571ac730c
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

**Respuesta.** HTTP 201 (esperado 201) · 74 ms · traza `fc431121-cc1d-4dde-8024-c1a571ac730c`

```json
{
  "id": 35,
  "folio": "SC-20261127-000035",
  "microhub_id": 1,
  "estado": "pendiente",
  "motivo": "Faltante detectado por el sistema",
  "solicitada_por": 2,
  "decidida_por": null,
  "decision_motivo": null,
  "decidida_en": null,
  "creada_en": "2026-11-27T20:31:30-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/35/decision`

```http
Accept: application/json
X-Traza-Id: 57cf5ba2-5fe9-4b2a-9332-25be850ed69a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aprobada",
  "motivo": "Con presupuesto"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 73 ms · traza `57cf5ba2-5fe9-4b2a-9332-25be850ed69a`

```json
{
  "id": 35,
  "folio": "SC-20261127-000035",
  "microhub_id": 1,
  "estado": "aprobada",
  "motivo": "Faltante detectado por el sistema",
  "solicitada_por": 2,
  "decidida_por": 1,
  "decision_motivo": "Con presupuesto",
  "decidida_en": "2026-11-27T20:31:30-06:00",
  "creada_en": "2026-11-27T20:31:30-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/35/ordenar`

```http
Accept: application/json
X-Traza-Id: c9b0e1ec-6664-4eb1-bebd-778ed0ec33e2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 201 (esperado 201) · 212 ms · traza `c9b0e1ec-6664-4eb1-bebd-778ed0ec33e2`

```json
{
  "solicitud_id": 35,
  "ordenes": [
    {
      "id": 31,
      "folio": "OC-20261127-000031",
      "solicitud_id": 35,
      "proveedor": {
        "id": 3,
        "nombre": "Mayorista San Nicolás"
      },
      "microhub_id": 1,
      "estado": "emitida",
      "fecha_esperada": "2026-12-01",
      "total": 4624.0,
      "creada_en": "2026-11-27T20:31:30-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/31/recepcion`

```http
Accept: application/json
X-Traza-Id: 6fd8c6ea-58cd-4ae8-bb45-eee02417c4dd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "operacion_uuid": "61007d40-f764-4772-86ce-f96ab8a61dc3",
  "nota": "Completo",
  "lineas": [
    {
      "producto_id": 51,
      "cantidad": 100
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 210 ms · traza `6fd8c6ea-58cd-4ae8-bb45-eee02417c4dd`

```json
{
  "orden": {
    "id": 31,
    "folio": "OC-20261127-000031",
    "solicitud_id": 35,
    "proveedor": {
      "id": 3,
      "nombre": "Mayorista San Nicolás"
    },
    "microhub_id": 1,
    "estado": "recibida",
    "fecha_esperada": "2026-12-01",
    "total": 4624.0,
    "creada_en": "2026-11-27T20:31:30-06:00",
    "cerrada_en": "2026-11-27T20:31:30-06:00",
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
    "existencia": 657,
    "minimo": 567
  }
]
```

## Servicio documentos · puerto 5107

### F2-08 · La remisión firmada queda en el almacén · PASA

**Objetivo.** Archivo con enlace firmado.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b0a3d0264537d891830d1c9/enlace`

```http
Accept: application/json
X-Traza-Id: a2988253-0167-43ff-addd-837668aa5a77
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 91 ms · traza `a2988253-0167-43ff-addd-837668aa5a77`

```json
{
  "id": "6b0a3d0264537d891830d1c9",
  "nombre": "remision-31.jpg",
  "url_firmada": "https://storage.googleapis.com/microhubs-evidencias-637044/d…(994 caracteres)",
  "metodo": "GET",
  "segundos": 300,
  "expira_en": "2026-11-27T20:36:30-06:00"
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F2-09 · Trazabilidad del producto en el microhub · PASA

**Objetivo.** Salida por pedido y recepción por orden.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/inventario?microhub_id=1&producto_id=51`

```http
Accept: application/json
X-Traza-Id: 949c77b3-5a34-4d26-8677-3ff0f89fe85e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 36 ms · traza `949c77b3-5a34-4d26-8677-3ff0f89fe85e`

```json
{
  "objeto": {
    "tipo": "inventario",
    "id": "1-51"
  },
  "total": 21,
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
    },
    {
      "fecha": "2026-11-26T23:28:55-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "transferencia_salida: -12 de producto 51 en microhub 1 (existencia 117). Inventario inicial del microhub nuevo",
      "usuario": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "1-51"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T23:28:59-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "recepcion: +100 de producto 51 en microhub 1 (existencia 217). Recepción de la orden OC-20261126-000011: Completo",
      "usuario": {
        "id": 2,
        "nombre": "Ruth Elizabeth Soriano"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "1-51"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T01:30:00-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "transferencia_salida: -12 de producto 51 en microhub 1 (existencia 205). Inventario inicial del microhub nuevo",
      "usuario": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "1-51"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T01:30:03-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "recepcion: +100 de producto 51 en microhub 1 (existencia 305). Recepción de la orden OC-20261127-000019: Completo",
      "usuario": {
        "id": 2,
        "nombre": "Ruth Elizabeth Soriano"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "1-51"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T11:42:35-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "transferencia_salida: -12 de producto 51 en microhub 1 (existencia 293). Inventario inicial del microhub nuevo",
      "usuario": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "1-51"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T11:42:39-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "recepcion: +100 de producto 51 en microhub 1 (existencia 393). Recepción de la orden OC-20261127-000023: Completo",
      "usuario": {
        "id": 2,
        "nombre": "Ruth Elizabeth Soriano"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "1-51"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T20:28:45-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "transferencia_salida: -12 de producto 51 en microhub 1 (existencia 381). Inventario inicial del microhub nuevo",
      "usuario": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "1-51"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T20:28:49-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "recepcion: +100 de producto 51 en microhub 1 (existencia 481). Recepción de la orden OC-20261127-000027: Completo",
      "usuario": {
        "id": 2,
        "nombre": "Ruth Elizabeth Soriano"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "1-51"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T20:31:00-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "transferencia_salida: -12 de producto 51 en microhub 1 (existencia 469). Inventario inicial del microhub nuevo",
      "usuario": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "1-51"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T20:31:03-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "recepcion: +100 de producto 51 en microhub 1 (existencia 569). Recepción de la orden OC-20261127-000030: Completo",
      "usuario": {
        "id": 2,
        "nombre": "Ruth Elizabeth Soriano"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "1-51"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T20:31:26-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "transferencia_salida: -12 de producto 51 en microhub 1 (existencia 557). Inventario inicial del microhub nuevo",
      "usuario": {
        "id": 1,
        "nombre": "Mauro Castillo Peña"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "1-51"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T20:31:30-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "recepcion: +100 de producto 51 en microhub 1 (existencia 657). Recepción de la orden OC-20261127-000031: Completo",
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
X-Traza-Id: 3e1eb9e3-c8a2-4cfe-9a66-befdc59dca1b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 166 ms · traza `3e1eb9e3-c8a2-4cfe-9a66-befdc59dca1b`

```json
﻿Microhub,Producto,Existencia,Mínimo,Disponible,Faltante,Severidad
Microhub San Bernabé Centro,Yogur natural,7,8,7,1,baja
Total,,,,,1,

```

## Servicio pedidos · puerto 5104

### F3-01 · El cliente hace un pedido · PASA

**Objetivo.** Punto de partida del recorrido.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: 5d0dbea6-10dd-4e7f-b787-7581eb2852df
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

**Respuesta.** HTTP 201 (esperado 201) · 138 ms · traza `5d0dbea6-10dd-4e7f-b787-7581eb2852df`

```json
{
  "id": 704,
  "folio": "PED-20261127-000704",
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
X-Traza-Id: 0723c51a-fe4a-48c5-b68d-e22da025402f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
Content-Type: application/json
```

```json
{
  "pedido_id": 704,
  "repartidor_id": 8
}
```

**Respuesta.** HTTP 201 (esperado 201) · 41 ms · traza `0723c51a-fe4a-48c5-b68d-e22da025402f`

```json
{
  "entrega_id": 220,
  "pedido_id": 704,
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
X-Traza-Id: 10596d37-ac47-414c-9f5c-d7b7a3c358b9
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4Iiwi…(292 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "24c975ee-5513-474b-b762-b5cfc5b27bf9",
  "dispositivo": "android-flujo-069084",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "07519ef8-d63b-4c5c-b430-f733e76b6e86",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-28T02:11:32.692553+00:00",
      "datos": {
        "entrega_id": 220,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-28T02:11:32.692571+00:00"
          },
          {
            "latitud": 25.7491,
            "longitud": -100.3611,
            "capturado_en": "2026-11-28T02:16:32.692577+00:00"
          }
        ]
      }
    },
    {
      "operacion_uuid": "11087635-8cb0-4d08-a1ca-9e3f1cb86c01",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-28T02:19:32.692587+00:00",
      "datos": {
        "entrega_id": 220,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "El cliente no estaba en su domicilio",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b0a3d04342f910fc3b1766f"
        ],
        "capturado_en": "2026-11-28T02:19:32.692592+00:00"
      }
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 247 ms · traza `10596d37-ac47-414c-9f5c-d7b7a3c358b9`

```json
{
  "id": 23,
  "lote_uuid": "24c975ee-5513-474b-b762-b5cfc5b27bf9",
  "dispositivo": "android-flujo-069084",
  "recibido_en": "2026-11-27T20:31:32-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 0,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "07519ef8-d63b-4c5c-b430-f733e76b6e86",
      "tipo": "ubicaciones",
      "estado": "aplicada",
      "duplicada": false,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    },
    {
      "operacion_uuid": "11087635-8cb0-4d08-a1ca-9e3f1cb86c01",
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
    "creada_en": "2026-11-27 20:11:32.692553-06:00"
  },
  {
    "tipo": "entrega_resultado",
    "estado": "aplicada",
    "intentos": 1,
    "creada_en": "2026-11-27 20:19:32.692587-06:00"
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
X-Traza-Id: 69183856-c9ad-424f-ba99-de6d0176e5bb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4Iiwi…(292 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "24c975ee-5513-474b-b762-b5cfc5b27bf9",
  "dispositivo": "android-flujo-069084",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "07519ef8-d63b-4c5c-b430-f733e76b6e86",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-28T02:11:32.692553+00:00",
      "datos": {
        "entrega_id": 220,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-28T02:11:32.692571+00:00"
          },
          {
            "latitud": 25.7491,
            "longitud": -100.3611,
            "capturado_en": "2026-11-28T02:16:32.692577+00:00"
          }
        ]
      }
    },
    {
      "operacion_uuid": "11087635-8cb0-4d08-a1ca-9e3f1cb86c01",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-28T02:19:32.692587+00:00",
      "datos": {
        "entrega_id": 220,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "El cliente no estaba en su domicilio",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b0a3d04342f910fc3b1766f"
        ],
        "capturado_en": "2026-11-28T02:19:32.692592+00:00"
      }
    }
  ]
}
```

**Respuesta.** HTTP 200 (esperado 200) · 109 ms · traza `69183856-c9ad-424f-ba99-de6d0176e5bb`

```json
{
  "id": 23,
  "lote_uuid": "24c975ee-5513-474b-b762-b5cfc5b27bf9",
  "dispositivo": "android-flujo-069084",
  "recibido_en": "2026-11-27T20:31:32-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 2,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "07519ef8-d63b-4c5c-b430-f733e76b6e86",
      "tipo": "ubicaciones",
      "estado": "aplicada",
      "duplicada": true,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    },
    {
      "operacion_uuid": "11087635-8cb0-4d08-a1ca-9e3f1cb86c01",
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
X-Traza-Id: c761e091-ff1b-4273-81f8-92e7bcf3ac07
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 35 ms · traza `c761e091-ff1b-4273-81f8-92e7bcf3ac07`

```json
{
  "datos": [
    {
      "id": 777,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000704",
      "mensaje": "El pedido cambió a entrega_fallida.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "704"
      },
      "creada_en": "2026-11-27T20:31:32-06:00"
    },
    {
      "id": 775,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000703",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "703"
      },
      "creada_en": "2026-11-27T20:31:31-06:00"
    },
    {
      "id": 770,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000702",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "702"
      },
      "creada_en": "2026-11-27T20:31:28-06:00"
    },
    {
      "id": 768,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000701",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "701"
      },
      "creada_en": "2026-11-27T20:31:04-06:00"
    },
    {
      "id": 763,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000700",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "700"
      },
      "creada_en": "2026-11-27T20:31:01-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 363,
    "paginas": 73
  }
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F3-06 · El auditor revisa la entrega · PASA

**Objetivo.** Bitácora y archivos de la entrega.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/entrega/220`

```http
Accept: application/json
X-Traza-Id: 862ae203-7683-4956-9c89-59b06f0b6c6d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 41 ms · traza `862ae203-7683-4956-9c89-59b06f0b6c6d`

```json
{
  "objeto": {
    "tipo": "entrega",
    "id": "220"
  },
  "total": 3,
  "eventos": [
    {
      "fecha": "2026-11-27T20:31:32-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "asignada_en = 2026-11-27T20:31:32.585062-06:00; cambio_entregado = None; capturado_en = None; cerrada_por_usuario_id = None",
      "usuario": {
        "id": 3,
        "nombre": "María José Cedillo Mata"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "220"
      },
      "cambios": [
        {
          "campo": "asignada_en",
          "anterior": null,
          "nuevo": "2026-11-27T20:31:32.585062-06:00"
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
      "fecha": "2026-11-27T20:31:32-06:00",
      "origen": "documentos",
      "accion": "documento_subido",
      "descripcion": "evidencia-flujo3-220.jpg (276 bytes, sha256 7f6025cd8a98…)",
      "usuario": {
        "id": 8,
        "nombre": null
      },
      "entidad": {
        "tipo": "documento",
        "id": "6b0a3d04342f910fc3b1766f"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T20:31:32-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "cambio_entregado = 0.0; capturado_en = 2026-11-27T20:19:32.6…(145 caracteres)",
      "usuario": {
        "id": 8,
        "nombre": "Diana Sepúlveda Ibarra"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "220"
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
          "nuevo": "2026-11-27T20:19:32.692592-06:00"
        },
        {
          "campo": "cerrada_por_usuario_id",
          "anterior": null,
          "nuevo": "8"
        },
        {
          "campo": "cierre_en",
          "anterior": null,
          "nuevo": "2026-11-27T20:31:32.839426-06:00"
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
          "nuevo": "[\"6b0a3d04342f910fc3b1766f\"]"
        },
        {
          "campo": "evidencia_url",
          "anterior": null,
          "nuevo": "/api/v1/documentos/6b0a3d04342f910fc3b1766f"
        },
        {
          "campo": "id_cliente_local",
          "anterior": null,
          "nuevo": "11087635-8cb0-4d08-a1ca-9e3f1cb86c01"
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
X-Traza-Id: 8cf437ca-fe04-41b7-976e-28fa18598964
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 34 ms · traza `8cf437ca-fe04-41b7-976e-28fa18598964`

```json
{
  "datos": [
    {
      "id": 2970,
      "microhub_id": 2,
      "producto_id": 51,
      "tipo": "devolucion_cancelacion",
      "cantidad": 3,
      "existencia_resultante": 60,
      "referencia": {
        "tipo": "pedido",
        "id": "704"
      },
      "motivo": "Entrega fallida: la mercancía regresa al microhub.",
      "usuario_id": 8,
      "fecha": "2026-11-27T20:31:32-06:00"
    },
    {
      "id": 2969,
      "microhub_id": 2,
      "producto_id": 31,
      "tipo": "devolucion_cancelacion",
      "cantidad": 3,
      "existencia_resultante": 67,
      "referencia": {
        "tipo": "pedido",
        "id": "704"
      },
      "motivo": "Entrega fallida: la mercancía regresa al microhub.",
      "usuario_id": 8,
      "fecha": "2026-11-27T20:31:32-06:00"
    },
    {
      "id": 2968,
      "microhub_id": 2,
      "producto_id": 51,
      "tipo": "salida_pedido",
      "cantidad": -3,
      "existencia_resultante": 57,
      "referencia": {
        "tipo": "pedido",
        "id": "704"
      },
      "motivo": null,
      "usuario_id": 9,
      "fecha": "2026-11-27T20:31:31-06:00"
    },
    {
      "id": 2967,
      "microhub_id": 2,
      "producto_id": 31,
      "tipo": "salida_pedido",
      "cantidad": -3,
      "existencia_resultante": 64,
      "referencia": {
        "tipo": "pedido",
        "id": "704"
      },
      "motivo": null,
      "usuario_id": 9,
      "fecha": "2026-11-27T20:31:31-06:00"
    },
    {
      "id": 2966,
      "microhub_id": 2,
      "producto_id": 51,
      "tipo": "devolucion_cancelacion",
      "cantidad": 10,
      "existencia_resultante": 60,
      "referencia": {
        "tipo": "pedido",
        "id": "703"
      },
      "motivo": "Cierre del flujo de demostración",
      "usuario_id": 1,
      "fecha": "2026-11-27T20:31:31-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 1929,
    "paginas": 386
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
    "existencia_resultante": 64
  },
  {
    "tipo": "salida_pedido",
    "producto_id": 51,
    "cantidad": -3,
    "existencia_resultante": 57
  },
  {
    "tipo": "devolucion_cancelacion",
    "producto_id": 31,
    "cantidad": 3,
    "existencia_resultante": 67
  },
  {
    "tipo": "devolucion_cancelacion",
    "producto_id": 51,
    "cantidad": 3,
    "existencia_resultante": 60
  }
]
```

## Servicio reportes · puerto 5123

### F3-08 · Reporte del periodo en CSV · PASA

**Objetivo.** La entrega ya cuenta en los reportes.

**Petición.** `GET http://reportes:5123/api/v1/reportes/pedidos_por_dia/exportar?formato=csv`

```http
Accept: application/json
X-Traza-Id: 6e6b532a-d238-40e3-8b7b-c5ce86ab621d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 159 ms · traza `6e6b532a-d238-40e3-8b7b-c5ce86ab621d`

```json
﻿Día,Pedidos,Unidades,Venta,Ticket promedio,Demanda no atendida
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
2026-11-26,72,408,17601.60,244.47,2
2026-11-27,50,274,10295.80,205.92,3
Total,211,1111,41334.90,195.90,38

```

**Evidencia en PostgreSQL.** `SELECT reporte, formato, filas, left(sha256, 16) AS sha256 FROM reporte_exportacion ORDER BY id DESC LIMIT 1`

```json
[
  {
    "reporte": "pedidos_por_dia",
    "formato": "csv",
    "filas": 29,
    "sha256": "4a9253d32319b43b"
  }
]
```
