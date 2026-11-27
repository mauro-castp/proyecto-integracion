# Procesos integrales de principio a fin


Generado el 2026-11-27 17:38 contra los servicios en ejecución. 40 de 40 casos pasan.

## Servicio planeacion · puerto 5106

### F1-01 · Escritorio (XML): el planeador registra una ubicación candidata · PASA

**Objetivo.** Planeación de ubicación.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos`

```http
Accept: application/xml
X-Traza-Id: 72548496-f8cd-44bd-b061-0bb25462bc1a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><candidato_nuevo xmlns="urn:microhubs:v1"><clave>********</clave><nombre>Ubicación del flujo 7F09B</nombre><latitud>25.760195</latitud><longitud>-100.370891</longitud><renta_estimada>15000.00</renta_estimada><nomina_estimada>36000.00</nomina_estimada><servicios_estimados>6000.00</servicios_estimados><otros_costos>4000.00</otros_costos><superficie_m2>100</superficie_m2><capacidad_fisica>120</capacidad_fisica><accesibilidad_vial>8</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km></candidato_nuevo>
```

**Respuesta.** HTTP 201 (esperado 201) · 62 ms · traza `72548496-f8cd-44bd-b061-0bb25462bc1a`

```xml
<?xml version='1.0' encoding='utf-8'?>
<candidato xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>366</id><clave>FL-7F09B</clave><nombre>Ubicación del flujo 7F09B</nombre><latitud>25.760195</latitud><longitud>-100.370891</longitud><renta_estimada>15000.00</renta_estimada><nomina_estimada>36000.00</nomina_estimada><servicios_estimados>6000.00</servicios_estimados><otros_costos>4000.00</otros_costos><costo_fijo>61000.00</costo_fijo><superficie_m2>100</superficie_m2><capacidad_fisica>120</capacidad_fisica><accesibilidad_vial>8</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato>
```

**Evidencia en PostgreSQL.** `SELECT id, clave, nombre, costo_fijo, decision FROM ubicacion_candidata WHERE clave = %s`

```json
[
  {
    "id": 366,
    "clave": "FL-7F09B",
    "nombre": "Ubicación del flujo 7F09B",
    "costo_fijo": "61000.00",
    "decision": "pendiente"
  }
]
```

### F1-02 · El planeador simula la operación de la candidata · PASA

**Objetivo.** Capacidad, utilización y decisión sugerida (MongoDB).

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/366/simular`

```http
Accept: application/json
X-Traza-Id: 45523eb6-f632-4e9a-bdda-6d008f78dfed
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

**Respuesta.** HTTP 200 (esperado 200) · 394 ms · traza `45523eb6-f632-4e9a-bdda-6d008f78dfed`

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
X-Traza-Id: 2c191558-06eb-44ff-8795-f2b05603fdc2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "candidato_id": 366,
  "pedidos_dia": 100,
  "ticket": 180,
  "margen_bruto": 0.3,
  "costos_fijos": 61000,
  "costo_variable_pedido": 22
}
```

**Respuesta.** HTTP 200 (esperado 200) · 63 ms · traza `2c191558-06eb-44ff-8795-f2b05603fdc2`

```json
{
  "id": null,
  "nombre": null,
  "objeto": {
    "tipo": "candidato",
    "id": 366,
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

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/366/decision`

```http
Accept: application/json
X-Traza-Id: 8030022e-55a4-48c5-9f27-e723bb40bfef
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aceptado",
  "motivo": "Cubre la zona del cliente y la demanda esperada supera el equilibrio."
}
```

**Respuesta.** HTTP 200 (esperado 200) · 82 ms · traza `8030022e-55a4-48c5-9f27-e723bb40bfef`

```json
{
  "id": 366,
  "clave": "********",
  "nombre": "Ubicación del flujo 7F09B",
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
X-Traza-Id: 8d9d8af7-c015-49f0-92ec-b304e92c5b07
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "clave": "********",
  "nombre": "Microhub 7F09B",
  "direccion": "Ubicación aprobada en planeación",
  "latitud": 25.760195,
  "longitud": -100.370891,
  "radio_km": 1.5,
  "capacidad_turno": 120
}
```

**Respuesta.** HTTP 201 (esperado 201) · 67 ms · traza `8d9d8af7-c015-49f0-92ec-b304e92c5b07`

```json
{
  "id": 27,
  "clave": "********",
  "nombre": "Microhub 7F09B",
  "latitud": 25.760195,
  "longitud": -100.370891,
  "radio_km": 1.5,
  "estatus": "activo"
}
```

## Servicio capacidad · puerto 5117

### F1-06 · Asignar personal al microhub · PASA

**Objetivo.** Operadores, repartidores y capacidad física.

**Petición.** `PUT http://capacidad:5117/api/v1/capacidad/recursos/27`

```http
Accept: application/json
X-Traza-Id: a36f0b09-b773-4f49-af44-1c5db2bb5bbf
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

**Respuesta.** HTTP 200 (esperado 200) · 175 ms · traza `a36f0b09-b773-4f49-af44-1c5db2bb5bbf`

```json
{
  "microhub": {
    "id": 27,
    "nombre": "Microhub 7F09B"
  },
  "operadores": 2,
  "repartidores": 2,
  "capacidad_fisica": 120,
  "actualizado_en": "2026-11-27T11:38:10-06:00"
}
```

## Servicio usuarios · puerto 5102

### F1-07 · Crear la cuenta del operador · PASA

**Objetivo.** Cuenta nueva con su perfil y su microhub.

**Petición.** `POST http://usuarios:5102/api/v1/usuarios`

```http
Accept: application/json
X-Traza-Id: 148ce525-ae55-46e7-8774-6fbdd337e766
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Operador",
  "apellidos": "7F09B",
  "correo": "operador.7f09b@ejemplo.mx",
  "clave": "********",
  "rol": "operador",
  "microhub_id": 27
}
```

**Respuesta.** HTTP 201 (esperado 201) · 160 ms · traza `148ce525-ae55-46e7-8774-6fbdd337e766`

```json
{
  "id": 88,
  "nombre": "Operador",
  "apellidos": "7F09B",
  "correo": "operador.7f09b@ejemplo.mx",
  "telefono": null,
  "rol": "operador",
  "microhub": {
    "id": 27,
    "clave": "********",
    "nombre": "Microhub 7F09B"
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
X-Traza-Id: 45879034-f50a-4da9-ac68-8ea7a1990194
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "origen_microhub_id": 1,
  "destino_microhub_id": 27,
  "producto_id": 31,
  "cantidad": 12,
  "motivo": "Inventario inicial del microhub nuevo",
  "operacion_uuid": "c46c15d3-af41-431c-8226-4deb7dea3f58"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 97 ms · traza `45879034-f50a-4da9-ac68-8ea7a1990194`

```json
{
  "producto_id": 31,
  "cantidad": 12,
  "duplicado": false,
  "origen": {
    "microhub_id": 1,
    "existencia": 555,
    "movimiento_id": 3417
  },
  "destino": {
    "microhub_id": 27,
    "existencia": 12,
    "movimiento_id": 3418
  }
}
```

### F1-08b · Surtir el microhub nuevo · PASA

**Objetivo.** Transferencia atómica desde MH-01.

**Petición.** `POST http://inventario:5111/api/v1/inventario/transferencias`

```http
Accept: application/json
X-Traza-Id: e118c4e7-4e8f-43fc-8880-f5e57d33ebd1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "origen_microhub_id": 1,
  "destino_microhub_id": 27,
  "producto_id": 1,
  "cantidad": 12,
  "motivo": "Inventario inicial del microhub nuevo",
  "operacion_uuid": "4864bce4-1c04-4205-af88-60a83640f20d"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 99 ms · traza `e118c4e7-4e8f-43fc-8880-f5e57d33ebd1`

```json
{
  "producto_id": 1,
  "cantidad": 12,
  "duplicado": false,
  "origen": {
    "microhub_id": 1,
    "existencia": 44,
    "movimiento_id": 3419
  },
  "destino": {
    "microhub_id": 27,
    "existencia": 12,
    "movimiento_id": 3420
  }
}
```

## Servicio pedidos · puerto 5104

### F1-09 · Android (JSON): el cliente hace su pedido · PASA

**Objetivo.** El motor lo asigna al microhub más cercano que tiene todo: el nuevo.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: b95cbf5f-ce52-4942-bf97-fc0b5d60a3b2
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
      "producto_id": 1,
      "cantidad": 3
    }
  ],
  "operacion_uuid": "9dad87ce-c4c3-44ec-a7c1-cc34b42e6164"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 274 ms · traza `b95cbf5f-ce52-4942-bf97-fc0b5d60a3b2`

```json
{
  "id": 884,
  "folio": "PED-20261127-000884",
  "estado": "asignado",
  "zona_id": 3,
  "microhub_id": 27,
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
    "microhub_ganador_id": 27,
    "motivo": null
  }
]
```

**Evidencia en PostgreSQL.** `SELECT tipo, producto_id, cantidad, existencia_resultante FROM movimiento_inventario WHERE referencia_tipo = 'pedido' AND referencia_id = %s`

```json
[
  {
    "tipo": "salida_pedido",
    "producto_id": 1,
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

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/884/estado`

```http
Accept: application/json
X-Traza-Id: e92a3d24-c2ca-42c5-b19a-fabc8f63d449
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4OCIs…(296 caracteres)
Content-Type: application/json
```

```json
{
  "estado": "en_preparacion"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 95 ms · traza `e92a3d24-c2ca-42c5-b19a-fabc8f63d449`

```json
{
  "id": 884,
  "folio": "PED-20261127-000884",
  "estado": "en_preparacion",
  "zona": {
    "id": 3,
    "nombre": "Paseo de San Bernabé"
  },
  "microhub_id": 27,
  "total": 289.5,
  "creado_en": "2026-11-27T11:38:11-06:00"
}
```

### F1-11 · El operador lo marca listo · PASA

**Objetivo.** Queda disponible para despacho.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/884/listo`

```http
Accept: application/json
X-Traza-Id: 2ed7fabf-47dd-494c-997f-a71095adc93c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4OCIs…(296 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 200 (esperado 200) · 61 ms · traza `2ed7fabf-47dd-494c-997f-a71095adc93c`

```json
{
  "id": 884,
  "estado": "en_preparacion",
  "listo_en": "2026-11-27T11:38:11-06:00"
}
```

## Servicio rutas · puerto 5118

### F1-12 · Proponer la ruta de despacho · PASA

**Objetivo.** Agrupa, asigna repartidor y ordena las paradas (algoritmo de rutas).

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/json
X-Traza-Id: 190011f2-2848-4ba9-b89e-f620a409cc46
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4OCIs…(296 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 27,
  "pedido_ids": [
    884
  ],
  "repartidor_ids": [
    7
  ],
  "metodo": "automatico",
  "guardar": true
}
```

**Respuesta.** HTTP 201 (esperado 201) · 176 ms · traza `190011f2-2848-4ba9-b89e-f620a409cc46`

```json
{
  "id": 164,
  "estado": "propuesto",
  "version": 1,
  "microhub": {
    "id": 27,
    "nombre": "Microhub 7F09B"
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
            "id": 884,
            "folio": "PED-20261127-000884"
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
X-Traza-Id: 97d89f41-b1e5-429c-a1fd-d8444716d683
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4OCIs…(296 caracteres)
Content-Type: application/json
```

```json
{
  "pedido_id": 884,
  "repartidor_id": 7,
  "orden_parada": 1
}
```

**Respuesta.** HTTP 201 (esperado 201) · 61 ms · traza `97d89f41-b1e5-429c-a1fd-d8444716d683`

```json
{
  "entrega_id": 505,
  "pedido_id": 884,
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
    "referencia_id": "505"
  }
]
```

### F1-14 · Android: el repartidor ve su parada · PASA

**Objetivo.** Sesión validada en Redis.

**Petición.** `GET http://entregas:5105/api/v1/entregas/mias?por_pagina=50`

```http
Accept: application/json
X-Traza-Id: 733c8344-c987-4ef5-925b-27c7a5cffada
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 66 ms · traza `733c8344-c987-4ef5-925b-27c7a5cffada`

```json
{
  "datos": [
    {
      "id": 493,
      "pedido_id": 866,
      "folio": "PED-20261127-000866",
      "estado_pedido": "en_ruta",
      "orden_parada": 1,
      "direccion": "Valle de Santiago 416, San Bernabé",
      "zona": "San Bernabé Centro",
      "distancia_km": 0.38,
      "minutos_estimados": 5.0,
      "total": 123.0
    },
    {
      "id": 505,
      "pedido_id": 884,
      "folio": "PED-20261127-000884",
      "estado_pedido": "en_ruta",
      "orden_parada": 1,
      "direccion": "Nogal 1440, Paseo de San Bernabé",
      "zona": "Paseo de San Bernabé",
      "distancia_km": null,
      "minutos_estimados": null,
      "total": 289.5
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
      "id": 468,
      "pedido_id": 808,
      "folio": "PED-20261127-000808",
      "estado_pedido": "en_ruta",
      "orden_parada": 2,
      "direccion": "Valle Alto 2774, Valles de San Bernabé",
      "zona": "Valles de San Bernabé",
      "distancia_km": 0.64,
      "minutos_estimados": 11.5,
      "total": 128.0
    },
    {
      "id": 494,
      "pedido_id": 868,
      "folio": "PED-20261127-000868",
      "estado_pedido": "en_ruta",
      "orden_parada": 2,
      "direccion": "Valle de Santiago 416, San Bernabé",
      "zona": "San Bernabé Centro",
      "distancia_km": 0.0,
      "minutos_estimados": 9.0,
      "total": 211.5
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
      "id": 495,
      "pedido_id": 867,
      "folio": "PED-20261127-000867",
      "estado_pedido": "en_ruta",
      "orden_parada": 3,
      "direccion": "Los Ángeles 2920, San Bernabé",
      "zona": "San Bernabé Centro",
      "distancia_km": 0.44,
      "minutos_estimados": 14.2,
      "total": 163.0
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
    "total": 8,
    "paginas": 1
  }
}
```

**Evidencia en Redis.** `SCARD auth:sesion:7`

```json
[
  {
    "comando": "SCARD auth:sesion:7",
    "valor": 36
  }
]
```

## Servicio seguimiento · puerto 5110

### F1-15 · El repartidor envía su recorrido · PASA

**Objetivo.** Puntos GPS en MongoDB (2dsphere).

**Petición.** `POST http://seguimiento:5110/api/v1/seguimiento/505/ubicaciones`

```http
Accept: application/json
X-Traza-Id: ad2fe52a-657e-4b7b-b4fa-0e69d7f76b52
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "puntos": [
    {
      "latitud": 25.760195,
      "longitud": -100.370891,
      "capturado_en": "2026-11-27T17:34:12.036599+00:00"
    },
    {
      "latitud": 25.759995,
      "longitud": -100.371091,
      "capturado_en": "2026-11-27T17:37:12.036625+00:00"
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 28 ms · traza `ad2fe52a-657e-4b7b-b4fa-0e69d7f76b52`

```json
{
  "recibidos": 2
}
```

## Servicio documentos · puerto 5107

### F1-16 · La foto de evidencia queda en el almacén · PASA

**Objetivo.** En la base solo sus datos; se descarga con un enlace firmado.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b09c0041bec79631659468d/enlace`

```http
Accept: application/json
X-Traza-Id: 23fd32d7-7f12-41d5-805b-74e459ace446
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 29 ms · traza `23fd32d7-7f12-41d5-805b-74e459ace446`

```json
{
  "id": "6b09c0041bec79631659468d",
  "nombre": "evidencia-flujo1-7F09B.jpg",
  "url_firmada": "http://documentos:5107/api/v1/documentos/descarga?k=document…(208 caracteres)",
  "metodo": "GET",
  "segundos": 300,
  "expira_en": "2026-11-27T11:43:12-06:00"
}
```

**Evidencia en MongoDB.** `db.documentos.findOne({_id}) sin contenido`

```json
{
  "_id": "6b09c0041bec79631659468d",
  "nombre": "evidencia-flujo1-7F09B.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "505"
  },
  "subido_por": 7,
  "creado_en": "2026-11-27 17:38:12.092000+00:00",
  "ruta": "documentos/2026/11/6b09c0041bec79631659468d.jpg",
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

**Petición.** `POST http://entregas:5105/api/v1/entregas/505/resultado`

```http
Accept: application/json
X-Traza-Id: 750a8a02-5982-409a-b07b-e9329fb66058
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
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
    "6b09c0041bec79631659468d"
  ],
  "capturado_en": "2026-11-27T17:38:12.316194+00:00",
  "id_cliente_local": "a54a1903-7934-4b21-89d2-1cc20d8e5d57"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 98 ms · traza `750a8a02-5982-409a-b07b-e9329fb66058`

```json
{
  "entrega_id": 505,
  "pedido_id": 884,
  "estado_pedido": "entregado",
  "cerrado_en": "2026-11-27T11:38:12-06:00",
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
    "usuario_id": 88,
    "proceso": null
  },
  {
    "estado_anterior": "en_preparacion",
    "estado_nuevo": "en_ruta",
    "usuario_id": 88,
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
X-Traza-Id: 831ff800-3310-4cf4-adb7-7a265ac11877
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 50 ms · traza `831ff800-3310-4cf4-adb7-7a265ac11877`

```json
{
  "datos": [
    {
      "id": 1568,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000884",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "884"
      },
      "creada_en": "2026-11-27T11:38:12-06:00"
    },
    {
      "id": 1566,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000882",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "882"
      },
      "creada_en": "2026-11-27T11:37:28-06:00"
    },
    {
      "id": 1561,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000881",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "881"
      },
      "creada_en": "2026-11-27T11:37:25-06:00"
    },
    {
      "id": 1520,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000862",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "862"
      },
      "creada_en": "2026-11-27T11:32:53-06:00"
    },
    {
      "id": 1515,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000861",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "861"
      },
      "creada_en": "2026-11-27T11:32:50-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 55,
    "paginas": 11
  }
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F1-19 · El auditor reconstruye la historia del pedido · PASA

**Objetivo.** Bitácora, estados, inventario y archivos en una línea de tiempo.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/pedido/884`

```http
Accept: application/json
X-Traza-Id: bc8d1a4f-2e00-4318-a2b0-e0625f39078a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 106 ms · traza `bc8d1a4f-2e00-4318-a2b0-e0625f39078a`

```json
{
  "objeto": {
    "tipo": "pedido",
    "id": "884"
  },
  "total": 15,
  "eventos": [
    {
      "fecha": "2026-11-27T11:38:11-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "actualizado_en = 2026-11-27T11:38:11.391577-06:00; asignado_en = None; cerrado_en = None; cliente_id = 1",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "884"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": null,
          "nuevo": "2026-11-27T11:38:11.391577-06:00"
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
          "nuevo": "2026-11-27T11:38:11.391577-06:00"
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
          "nuevo": "PED-20261127-000884"
        },
        {
          "campo": "id",
          "anterior": null,
          "nuevo": "884"
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
      "fecha": "2026-11-27T11:38:11-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "asignado_en = 2026-11-27T11:38:11.391577-06:00; estado: creado → asignado; microhub_id = 27",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "884"
      },
      "cambios": [
        {
          "campo": "asignado_en",
          "anterior": null,
          "nuevo": "2026-11-27T11:38:11.391577-06:00"
        },
        {
          "campo": "estado",
          "anterior": "creado",
          "nuevo": "asignado"
        },
        {
          "campo": "microhub_id",
          "anterior": null,
          "nuevo": "27"
        }
      ]
    },
    {
      "fecha": "2026-11-27T11:38:11-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "nuevo → creado",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "884"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T11:38:11-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "creado → asignado",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "884"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T11:38:11-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -3 de producto 1 en microhub 27 (existencia 9)",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "27-1"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T11:38:11-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -3 de producto 31 en microhub 27 (existencia 9)",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "27-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T11:38:11-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-27T11:38:11.391577-06:00 → 2026-11-27T11:38:11.576025-06:00; estado: asignado → en_preparacion",
      "usuario": {
        "id": 88,
        "nombre": "Operador 7F09B"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "884"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-27T11:38:11.391577-06:00",
          "nuevo": "2026-11-27T11:38:11.576025-06:00"
        },
        {
          "campo": "estado",
          "anterior": "asignado",
          "nuevo": "en_preparacion"
        }
      ]
    },
    {
      "fecha": "2026-11-27T11:38:11-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "asignado → en_preparacion",
      "usuario": {
        "id": 88,
        "nombre": "Operador 7F09B"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "884"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T11:38:11-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "listo_en = 2026-11-27T11:38:11.672281-06:00",
      "usuario": {
        "id": 88,
        "nombre": "Operador 7F09B"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "884"
      },
      "cambios": [
        {
          "campo": "listo_en",
          "anterior": null,
          "nuevo": "2026-11-27T11:38:11.672281-06:00"
        }
      ]
    },
    {
      "fecha": "2026-11-27T11:38:11-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "asignada_en = 2026-11-27T11:38:11.90388-06:00; cambio_entregado = None; capturado_en = None; cerrada_por_usuario_id = None",
      "usuario": {
        "id": 88,
        "nombre": "Operador 7F09B"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "505"
      },
      "cambios": [
        {
          "campo": "asignada_en",
          "anterior": null,
          "nuevo": "2026-11-27T11:38:11.90388-06:00"
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
      "fecha": "2026-11-27T11:38:11-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-27T11:38:11.576025-06:00 → 2026-11-27T11:38:11.90388-06:00; estado: en_preparacion → en_ruta",
      "usuario": {
        "id": 88,
        "nombre": "Operador 7F09B"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "884"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-27T11:38:11.576025-06:00",
          "nuevo": "2026-11-27T11:38:11.90388-06:00"
        },
        {
          "campo": "estado",
          "anterior": "en_preparacion",
          "nuevo": "en_ruta"
        }
      ]
    },
    {
      "fecha": "2026-11-27T11:38:11-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "en_preparacion → en_ruta",
      "usuario": {
        "id": 88,
        "nombre": "Operador 7F09B"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "884"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T11:38:12-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "cambio_entregado = 0.0; capturado_en = 2026-11-27T11:38:12.3…(145 caracteres)",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "505"
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
          "nuevo": "2026-11-27T11:38:12.316194-06:00"
        },
        {
          "campo": "cerrada_por_usuario_id",
          "anterior": null,
          "nuevo": "7"
        },
        {
          "campo": "cierre_en",
          "anterior": null,
          "nuevo": "2026-11-27T11:38:12.362307-06:00"
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
          "nuevo": "[\"6b09c0041bec79631659468d\"]"
        },
        {
          "campo": "evidencia_url",
          "anterior": null,
          "nuevo": "/api/v1/documentos/6b09c0041bec79631659468d"
        },
        {
          "campo": "id_cliente_local",
          "anterior": null,
          "nuevo": "a54a1903-7934-4b21-89d2-1cc20d8e5d57"
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
      "fecha": "2026-11-27T11:38:12-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-27T11:38:11.90388-06:00 → 2026-11-27…(158 caracteres)",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "884"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-27T11:38:11.90388-06:00",
          "nuevo": "2026-11-27T11:38:12.362307-06:00"
        },
        {
          "campo": "cerrado_en",
          "anterior": null,
          "nuevo": "2026-11-27T11:38:12.362307-06:00"
        },
        {
          "campo": "estado",
          "anterior": "en_ruta",
          "nuevo": "entregado"
        }
      ]
    },
    {
      "fecha": "2026-11-27T11:38:12-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "en_ruta → entregado",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "884"
      },
      "cambios": []
    }
  ]
}
```

## Servicio reportes · puerto 5123

### F1-20 · Visualización: el microhub nuevo ya aparece en la comparación · PASA

**Objetivo.** Datos listos para Highcharts.

**Petición.** `GET http://reportes:5123/api/v1/reportes/comparacion_microhubs/grafica?microhub_id=27`

```http
Accept: application/json
X-Traza-Id: ba6badd9-631e-4e8a-911e-870f82150352
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 110 ms · traza `ba6badd9-631e-4e8a-911e-870f82150352`

```json
{
  "reporte": "comparacion_microhubs",
  "titulo": "Comparación entre microhubs",
  "tipo": "column",
  "unidad": "pedidos / MXN",
  "categorias": [
    "Microhub 7F09B"
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

**Petición.** `DELETE http://microhubs:5109/api/v1/microhubs/27`

```http
Accept: application/json
X-Traza-Id: 9538525e-04bc-4f16-90fa-baae74cc1854
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 45 ms · traza `9538525e-04bc-4f16-90fa-baae74cc1854`

```json
(sin cuerpo)
```

## Servicio pedidos · puerto 5104

### F2-01 · Android: un cliente compra y el inventario baja · PASA

**Objetivo.** El motor descuenta inventario en la misma transacción.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: a4aff505-96ec-40cd-b5b0-64862242687a
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
  "operacion_uuid": "278eb288-eea9-4a2e-9489-70067626cd71"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 223 ms · traza `a4aff505-96ec-40cd-b5b0-64862242687a`

```json
{
  "id": 885,
  "folio": "PED-20261127-000885",
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
    "existencia_resultante": 24
  }
]
```

## Servicio inventario · puerto 5111

### F2-02 · El operador fija el mínimo y nace la alerta · PASA

**Objetivo.** El trigger avisa del faltante.

**Petición.** `PATCH http://inventario:5111/api/v1/inventario/1/31/minimo`

```http
Accept: application/json
X-Traza-Id: 11f96c05-fca1-4cf6-8c07-910fec7bd1ba
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "minimo": 565
}
```

**Respuesta.** HTTP 200 (esperado 200) · 157 ms · traza `11f96c05-fca1-4cf6-8c07-910fec7bd1ba`

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
  "existencia": 555,
  "minimo": 565,
  "reservado": 0,
  "disponible": 555,
  "estado": "bajo_minimo",
  "actualizado_en": "2026-11-27T11:38:14-06:00"
}
```

### F2-03 · La alerta de faltante · PASA

**Objetivo.** Qué producto, cuánto falta y qué tan grave es.

**Petición.** `GET http://inventario:5111/api/v1/inventario/alertas?microhub_id=1&por_pagina=100`

```http
Accept: application/json
X-Traza-Id: 7fb82a2e-6212-486b-8258-f867dacf2eeb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 111 ms · traza `7fb82a2e-6212-486b-8258-f867dacf2eeb`

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
      "existencia": 555,
      "minimo": 565,
      "disponible": 555,
      "faltante": 10,
      "severidad": "baja"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 100,
    "total": 1,
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
X-Traza-Id: ac51189d-b3ab-46e3-8d03-681e4b6b0816
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

**Respuesta.** HTTP 201 (esperado 201) · 90 ms · traza `ac51189d-b3ab-46e3-8d03-681e4b6b0816`

```json
{
  "id": 119,
  "folio": "SC-20261127-000119",
  "microhub_id": 1,
  "estado": "pendiente",
  "motivo": "Faltante detectado por el sistema",
  "solicitada_por": 2,
  "decidida_por": null,
  "decision_motivo": null,
  "decidida_en": null,
  "creada_en": "2026-11-27T11:38:14-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/119/decision`

```http
Accept: application/json
X-Traza-Id: 4ecde880-5159-4eb5-8a28-6f0b36549a7e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aprobada",
  "motivo": "Con presupuesto"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 97 ms · traza `4ecde880-5159-4eb5-8a28-6f0b36549a7e`

```json
{
  "id": 119,
  "folio": "SC-20261127-000119",
  "microhub_id": 1,
  "estado": "aprobada",
  "motivo": "Faltante detectado por el sistema",
  "solicitada_por": 2,
  "decidida_por": 1,
  "decision_motivo": "Con presupuesto",
  "decidida_en": "2026-11-27T11:38:14-06:00",
  "creada_en": "2026-11-27T11:38:14-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/119/ordenar`

```http
Accept: application/json
X-Traza-Id: 625457cb-0f74-4627-be05-d5d8e54ffae0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 201 (esperado 201) · 215 ms · traza `625457cb-0f74-4627-be05-d5d8e54ffae0`

```json
{
  "solicitud_id": 119,
  "ordenes": [
    {
      "id": 78,
      "folio": "OC-20261127-000078",
      "solicitud_id": 119,
      "proveedor": {
        "id": 1,
        "nombre": "Abarrotes del Norte"
      },
      "microhub_id": 1,
      "estado": "emitida",
      "fecha_esperada": "2026-11-29",
      "total": 4060.0,
      "creada_en": "2026-11-27T11:38:14-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/78/recepcion`

```http
Accept: application/json
X-Traza-Id: 1cbdd7ac-82dd-438f-8ee3-b1146b2ecc59
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "operacion_uuid": "7e44279b-9502-4824-8864-e226cb08218d",
  "nota": "Completo",
  "lineas": [
    {
      "producto_id": 31,
      "cantidad": 100
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 294 ms · traza `1cbdd7ac-82dd-438f-8ee3-b1146b2ecc59`

```json
{
  "orden": {
    "id": 78,
    "folio": "OC-20261127-000078",
    "solicitud_id": 119,
    "proveedor": {
      "id": 1,
      "nombre": "Abarrotes del Norte"
    },
    "microhub_id": 1,
    "estado": "recibida",
    "fecha_esperada": "2026-11-29",
    "total": 4060.0,
    "creada_en": "2026-11-27T11:38:14-06:00",
    "cerrada_en": "2026-11-27T11:38:15-06:00",
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
    "existencia": 655,
    "minimo": 565
  }
]
```

## Servicio documentos · puerto 5107

### F2-08 · La remisión firmada queda en el almacén · PASA

**Objetivo.** Archivo con enlace firmado.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b09c0071bec796316594692/enlace`

```http
Accept: application/json
X-Traza-Id: ca2348bb-f217-4c54-9dc7-b5f981fd5302
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 28 ms · traza `ca2348bb-f217-4c54-9dc7-b5f981fd5302`

```json
{
  "id": "6b09c0071bec796316594692",
  "nombre": "remision-78.jpg",
  "url_firmada": "http://documentos:5107/api/v1/documentos/descarga?k=document…(197 caracteres)",
  "metodo": "GET",
  "segundos": 300,
  "expira_en": "2026-11-27T11:43:15-06:00"
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F2-09 · Trazabilidad del producto en el microhub · PASA

**Objetivo.** Salida por pedido y recepción por orden.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/inventario?microhub_id=1&producto_id=31`

```http
Accept: application/json
X-Traza-Id: d9018e93-75b2-44cd-857a-aae9380e9aa6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 48 ms · traza `d9018e93-75b2-44cd-857a-aae9380e9aa6`

```json
{
  "objeto": {
    "tipo": "inventario",
    "id": "1-31"
  },
  "total": 27,
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
X-Traza-Id: f5db220b-8b18-43af-8a89-073ac5b2f72e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 166 ms · traza `f5db220b-8b18-43af-8a89-073ac5b2f72e`

```json
﻿Microhub,Producto,Existencia,Mínimo,Disponible,Faltante,Severidad

```

## Servicio pedidos · puerto 5104

### F3-01 · El cliente hace un pedido · PASA

**Objetivo.** Punto de partida del recorrido.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: d1e2678c-84ba-44f1-80c1-2c264d9472f6
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

**Respuesta.** HTTP 201 (esperado 201) · 209 ms · traza `d1e2678c-84ba-44f1-80c1-2c264d9472f6`

```json
{
  "id": 886,
  "folio": "PED-20261127-000886",
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
X-Traza-Id: 34b10f45-f738-4cdf-bfab-718c02c0838c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
Content-Type: application/json
```

```json
{
  "pedido_id": 886,
  "repartidor_id": 7
}
```

**Respuesta.** HTTP 201 (esperado 201) · 71 ms · traza `34b10f45-f738-4cdf-bfab-718c02c0838c`

```json
{
  "entrega_id": 506,
  "pedido_id": 886,
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
X-Traza-Id: b6a1802a-00d9-4781-8fe7-254070dfa39d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "d28bb0b3-62e7-432e-bc97-853030cc52c8",
  "dispositivo": "android-flujo-e33eb4",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "1afcebcf-2702-4696-8cf9-78c903ddc7f7",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-27T17:18:17.472859+00:00",
      "datos": {
        "entrega_id": 506,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-27T17:18:17.472882+00:00"
          },
          {
            "latitud": 25.7491,
            "longitud": -100.3611,
            "capturado_en": "2026-11-27T17:23:17.472888+00:00"
          }
        ]
      }
    },
    {
      "operacion_uuid": "603619a8-4f47-4faf-9159-1624205eff15",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-27T17:26:17.472906+00:00",
      "datos": {
        "entrega_id": 506,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "El cliente no estaba en su domicilio",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b09c0091bec796316594697"
        ],
        "capturado_en": "2026-11-27T17:26:17.472911+00:00"
      }
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 423 ms · traza `b6a1802a-00d9-4781-8fe7-254070dfa39d`

```json
{
  "id": 290,
  "lote_uuid": "d28bb0b3-62e7-432e-bc97-853030cc52c8",
  "dispositivo": "android-flujo-e33eb4",
  "recibido_en": "2026-11-27T11:38:17-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 0,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "1afcebcf-2702-4696-8cf9-78c903ddc7f7",
      "tipo": "ubicaciones",
      "estado": "aplicada",
      "duplicada": false,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    },
    {
      "operacion_uuid": "603619a8-4f47-4faf-9159-1624205eff15",
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
    "creada_en": "2026-11-27 11:18:17.472859-06:00"
  },
  {
    "tipo": "entrega_resultado",
    "estado": "aplicada",
    "intentos": 1,
    "creada_en": "2026-11-27 11:26:17.472906-06:00"
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
X-Traza-Id: 40a99feb-de91-4ff2-97a8-38aeeddb7887
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "d28bb0b3-62e7-432e-bc97-853030cc52c8",
  "dispositivo": "android-flujo-e33eb4",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "1afcebcf-2702-4696-8cf9-78c903ddc7f7",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-27T17:18:17.472859+00:00",
      "datos": {
        "entrega_id": 506,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-27T17:18:17.472882+00:00"
          },
          {
            "latitud": 25.7491,
            "longitud": -100.3611,
            "capturado_en": "2026-11-27T17:23:17.472888+00:00"
          }
        ]
      }
    },
    {
      "operacion_uuid": "603619a8-4f47-4faf-9159-1624205eff15",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-27T17:26:17.472906+00:00",
      "datos": {
        "entrega_id": 506,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "El cliente no estaba en su domicilio",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b09c0091bec796316594697"
        ],
        "capturado_en": "2026-11-27T17:26:17.472911+00:00"
      }
    }
  ]
}
```

**Respuesta.** HTTP 200 (esperado 200) · 168 ms · traza `40a99feb-de91-4ff2-97a8-38aeeddb7887`

```json
{
  "id": 290,
  "lote_uuid": "d28bb0b3-62e7-432e-bc97-853030cc52c8",
  "dispositivo": "android-flujo-e33eb4",
  "recibido_en": "2026-11-27T11:38:17-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 2,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "1afcebcf-2702-4696-8cf9-78c903ddc7f7",
      "tipo": "ubicaciones",
      "estado": "aplicada",
      "duplicada": true,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    },
    {
      "operacion_uuid": "603619a8-4f47-4faf-9159-1624205eff15",
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
X-Traza-Id: ee1096a4-7bd1-4f09-ac87-ffd01829c07c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 45 ms · traza `ee1096a4-7bd1-4f09-ac87-ffd01829c07c`

```json
{
  "datos": [
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
    },
    {
      "id": 1573,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000885",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "885"
      },
      "creada_en": "2026-11-27T11:38:15-06:00"
    },
    {
      "id": 1568,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000884",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "884"
      },
      "creada_en": "2026-11-27T11:38:12-06:00"
    },
    {
      "id": 1566,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000882",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "882"
      },
      "creada_en": "2026-11-27T11:37:28-06:00"
    },
    {
      "id": 1561,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000881",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "881"
      },
      "creada_en": "2026-11-27T11:37:25-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 57,
    "paginas": 12
  }
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F3-06 · El auditor revisa la entrega · PASA

**Objetivo.** Bitácora y archivos de la entrega.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/entrega/506`

```http
Accept: application/json
X-Traza-Id: a299fd3a-0a09-4b71-8558-2812710e3237
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 52 ms · traza `a299fd3a-0a09-4b71-8558-2812710e3237`

```json
{
  "objeto": {
    "tipo": "entrega",
    "id": "506"
  },
  "total": 3,
  "eventos": [
    {
      "fecha": "2026-11-27T11:38:17-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "asignada_en = 2026-11-27T11:38:17.342853-06:00; cambio_entregado = None; capturado_en = None; cerrada_por_usuario_id = None",
      "usuario": {
        "id": 3,
        "nombre": "María José Cedillo Mata"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "506"
      },
      "cambios": [
        {
          "campo": "asignada_en",
          "anterior": null,
          "nuevo": "2026-11-27T11:38:17.342853-06:00"
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
      "fecha": "2026-11-27T11:38:17-06:00",
      "origen": "documentos",
      "accion": "documento_subido",
      "descripcion": "evidencia-flujo3-506.jpg (276 bytes, sha256 7f6025cd8a98…)",
      "usuario": {
        "id": 7,
        "nombre": null
      },
      "entidad": {
        "tipo": "documento",
        "id": "6b09c0091bec796316594697"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T11:38:17-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "cambio_entregado = 0.0; capturado_en = 2026-11-27T11:26:17.4…(145 caracteres)",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "506"
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
          "nuevo": "2026-11-27T11:26:17.472911-06:00"
        },
        {
          "campo": "cerrada_por_usuario_id",
          "anterior": null,
          "nuevo": "7"
        },
        {
          "campo": "cierre_en",
          "anterior": null,
          "nuevo": "2026-11-27T11:38:17.743393-06:00"
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
          "nuevo": "[\"6b09c0091bec796316594697\"]"
        },
        {
          "campo": "evidencia_url",
          "anterior": null,
          "nuevo": "/api/v1/documentos/6b09c0091bec796316594697"
        },
        {
          "campo": "id_cliente_local",
          "anterior": null,
          "nuevo": "603619a8-4f47-4faf-9159-1624205eff15"
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
X-Traza-Id: 57aa5b76-f335-475c-86eb-e71ebd556d95
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 46 ms · traza `57aa5b76-f335-475c-86eb-e71ebd556d95`

```json
{
  "datos": [
    {
      "id": 3429,
      "microhub_id": 2,
      "producto_id": 51,
      "tipo": "devolucion_cancelacion",
      "cantidad": 3,
      "existencia_resultante": 52,
      "referencia": {
        "tipo": "pedido",
        "id": "886"
      },
      "motivo": "Entrega fallida: la mercancía regresa al microhub.",
      "usuario_id": 7,
      "fecha": "2026-11-27T11:38:17-06:00"
    },
    {
      "id": 3428,
      "microhub_id": 2,
      "producto_id": 31,
      "tipo": "devolucion_cancelacion",
      "cantidad": 3,
      "existencia_resultante": 34,
      "referencia": {
        "tipo": "pedido",
        "id": "886"
      },
      "motivo": "Entrega fallida: la mercancía regresa al microhub.",
      "usuario_id": 7,
      "fecha": "2026-11-27T11:38:17-06:00"
    },
    {
      "id": 3427,
      "microhub_id": 2,
      "producto_id": 51,
      "tipo": "salida_pedido",
      "cantidad": -3,
      "existencia_resultante": 49,
      "referencia": {
        "tipo": "pedido",
        "id": "886"
      },
      "motivo": null,
      "usuario_id": 9,
      "fecha": "2026-11-27T11:38:16-06:00"
    },
    {
      "id": 3426,
      "microhub_id": 2,
      "producto_id": 31,
      "tipo": "salida_pedido",
      "cantidad": -3,
      "existencia_resultante": 31,
      "referencia": {
        "tipo": "pedido",
        "id": "886"
      },
      "motivo": null,
      "usuario_id": 9,
      "fecha": "2026-11-27T11:38:16-06:00"
    },
    {
      "id": 3425,
      "microhub_id": 2,
      "producto_id": 31,
      "tipo": "devolucion_cancelacion",
      "cantidad": 10,
      "existencia_resultante": 34,
      "referencia": {
        "tipo": "pedido",
        "id": "885"
      },
      "motivo": "Cierre del flujo de demostración",
      "usuario_id": 1,
      "fecha": "2026-11-27T11:38:15-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 1159,
    "paginas": 232
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
    "existencia_resultante": 31
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
    "existencia_resultante": 34
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
X-Traza-Id: 66b85173-5936-4176-bfec-7cc29c63707c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 173 ms · traza `66b85173-5936-4176-bfec-7cc29c63707c`

```json
﻿Día,Pedidos,Unidades,Venta,Ticket promedio,Demanda no atendida
2026-11-25,56,282,8032.40,143.44,0
2026-11-26,212,1096,34991.60,165.05,8
2026-11-27,102,563,19241.10,188.64,7
Total,370,1941,62265.10,168.28,15

```

**Evidencia en PostgreSQL.** `SELECT reporte, formato, filas, left(sha256, 16) AS sha256 FROM reporte_exportacion ORDER BY id DESC LIMIT 1`

```json
[
  {
    "reporte": "pedidos_por_dia",
    "formato": "csv",
    "filas": 3,
    "sha256": "fc36a32d86409c30"
  }
]
```
