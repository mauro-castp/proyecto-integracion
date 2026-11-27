# Procesos integrales de principio a fin


Generado el 2026-11-27 05:29 contra los servicios en ejecución. 40 de 40 casos pasan.

## Servicio planeacion · puerto 5106

### F1-01 · Escritorio (XML): el planeador registra una ubicación candidata · PASA

**Objetivo.** Planeación de ubicación.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos`

```http
Accept: application/xml
X-Traza-Id: 46a15017-9439-458b-a3b7-17d03b473d84
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><candidato_nuevo xmlns="urn:microhubs:v1"><clave>********</clave><nombre>Ubicación del flujo 64AC6</nombre><latitud>25.760195</latitud><longitud>-100.370891</longitud><renta_estimada>15000.00</renta_estimada><nomina_estimada>36000.00</nomina_estimada><servicios_estimados>6000.00</servicios_estimados><otros_costos>4000.00</otros_costos><superficie_m2>100</superficie_m2><capacidad_fisica>120</capacidad_fisica><accesibilidad_vial>8</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km></candidato_nuevo>
```

**Respuesta.** HTTP 201 (esperado 201) · 66 ms · traza `46a15017-9439-458b-a3b7-17d03b473d84`

```xml
<?xml version='1.0' encoding='utf-8'?>
<candidato xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>90</id><clave>FL-64AC6</clave><nombre>Ubicación del flujo 64AC6</nombre><latitud>25.760195</latitud><longitud>-100.370891</longitud><renta_estimada>15000.00</renta_estimada><nomina_estimada>36000.00</nomina_estimada><servicios_estimados>6000.00</servicios_estimados><otros_costos>4000.00</otros_costos><costo_fijo>61000.00</costo_fijo><superficie_m2>100</superficie_m2><capacidad_fisica>120</capacidad_fisica><accesibilidad_vial>8</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato>
```

**Evidencia en PostgreSQL.** `SELECT id, clave, nombre, costo_fijo, decision FROM ubicacion_candidata WHERE clave = %s`

```json
[
  {
    "id": 90,
    "clave": "FL-64AC6",
    "nombre": "Ubicación del flujo 64AC6",
    "costo_fijo": "61000.00",
    "decision": "pendiente"
  }
]
```

### F1-02 · El planeador simula la operación de la candidata · PASA

**Objetivo.** Capacidad, utilización y decisión sugerida (MongoDB).

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/90/simular`

```http
Accept: application/json
X-Traza-Id: debe666b-2800-4822-8c1c-02e97f7f4bcb
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

**Respuesta.** HTTP 200 (esperado 200) · 195 ms · traza `debe666b-2800-4822-8c1c-02e97f7f4bcb`

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
X-Traza-Id: a74ddac7-b8a6-4522-a115-317d2d78cc48
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "candidato_id": 90,
  "pedidos_dia": 100,
  "ticket": 180,
  "margen_bruto": 0.3,
  "costos_fijos": 61000,
  "costo_variable_pedido": 22
}
```

**Respuesta.** HTTP 200 (esperado 200) · 41 ms · traza `a74ddac7-b8a6-4522-a115-317d2d78cc48`

```json
{
  "id": null,
  "nombre": null,
  "objeto": {
    "tipo": "candidato",
    "id": 90,
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

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/90/decision`

```http
Accept: application/json
X-Traza-Id: c1bc7328-7fb0-4f95-94a2-ccfd63f582d0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aceptado",
  "motivo": "Cubre la zona del cliente y la demanda esperada supera el equilibrio."
}
```

**Respuesta.** HTTP 200 (esperado 200) · 35 ms · traza `c1bc7328-7fb0-4f95-94a2-ccfd63f582d0`

```json
{
  "id": 90,
  "clave": "********",
  "nombre": "Ubicación del flujo 64AC6",
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
X-Traza-Id: 90e555df-df64-4227-babb-cf4aefa391ec
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "clave": "********",
  "nombre": "Microhub 64AC6",
  "direccion": "Ubicación aprobada en planeación",
  "latitud": 25.760195,
  "longitud": -100.370891,
  "radio_km": 1.5,
  "capacidad_turno": 120
}
```

**Respuesta.** HTTP 201 (esperado 201) · 54 ms · traza `90e555df-df64-4227-babb-cf4aefa391ec`

```json
{
  "id": 7,
  "clave": "********",
  "nombre": "Microhub 64AC6",
  "latitud": 25.760195,
  "longitud": -100.370891,
  "radio_km": 1.5,
  "estatus": "activo"
}
```

## Servicio capacidad · puerto 5117

### F1-06 · Asignar personal al microhub · PASA

**Objetivo.** Operadores, repartidores y capacidad física.

**Petición.** `PUT http://capacidad:5117/api/v1/capacidad/recursos/7`

```http
Accept: application/json
X-Traza-Id: 7ac9e5d7-ec8e-4df9-a8e2-e714fb644b92
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

**Respuesta.** HTTP 200 (esperado 200) · 129 ms · traza `7ac9e5d7-ec8e-4df9-a8e2-e714fb644b92`

```json
{
  "microhub": {
    "id": 7,
    "nombre": "Microhub 64AC6"
  },
  "operadores": 2,
  "repartidores": 2,
  "capacidad_fisica": 120,
  "actualizado_en": "2026-11-26T23:28:55-06:00"
}
```

## Servicio usuarios · puerto 5102

### F1-07 · Crear la cuenta del operador · PASA

**Objetivo.** Cuenta nueva con su perfil y su microhub.

**Petición.** `POST http://usuarios:5102/api/v1/usuarios`

```http
Accept: application/json
X-Traza-Id: 49138eba-9753-4d9b-8471-3ed2be9c8e80
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Operador",
  "apellidos": "64AC6",
  "correo": "operador.64ac6@ejemplo.mx",
  "clave": "********",
  "rol": "operador",
  "microhub_id": 7
}
```

**Respuesta.** HTTP 201 (esperado 201) · 132 ms · traza `49138eba-9753-4d9b-8471-3ed2be9c8e80`

```json
{
  "id": 51,
  "nombre": "Operador",
  "apellidos": "64AC6",
  "correo": "operador.64ac6@ejemplo.mx",
  "telefono": null,
  "rol": "operador",
  "microhub": {
    "id": 7,
    "clave": "********",
    "nombre": "Microhub 64AC6"
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
X-Traza-Id: d0be8998-cc41-4e79-a54d-e5fb113c6533
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "origen_microhub_id": 1,
  "destino_microhub_id": 7,
  "producto_id": 51,
  "cantidad": 12,
  "motivo": "Inventario inicial del microhub nuevo",
  "operacion_uuid": "fd4aa7a2-1124-46be-a88d-9f700578e9b5"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 96 ms · traza `d0be8998-cc41-4e79-a54d-e5fb113c6533`

```json
{
  "producto_id": 51,
  "cantidad": 12,
  "duplicado": false,
  "origen": {
    "microhub_id": 1,
    "existencia": 117,
    "movimiento_id": 1819
  },
  "destino": {
    "microhub_id": 7,
    "existencia": 12,
    "movimiento_id": 1820
  }
}
```

### F1-08b · Surtir el microhub nuevo · PASA

**Objetivo.** Transferencia atómica desde MH-01.

**Petición.** `POST http://inventario:5111/api/v1/inventario/transferencias`

```http
Accept: application/json
X-Traza-Id: ca51db33-2940-4108-9236-11238d827bb6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "origen_microhub_id": 1,
  "destino_microhub_id": 7,
  "producto_id": 31,
  "cantidad": 12,
  "motivo": "Inventario inicial del microhub nuevo",
  "operacion_uuid": "e7bcece0-6eac-496d-9bc6-2c31564c1779"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 75 ms · traza `ca51db33-2940-4108-9236-11238d827bb6`

```json
{
  "producto_id": 31,
  "cantidad": 12,
  "duplicado": false,
  "origen": {
    "microhub_id": 1,
    "existencia": 33,
    "movimiento_id": 1821
  },
  "destino": {
    "microhub_id": 7,
    "existencia": 12,
    "movimiento_id": 1822
  }
}
```

## Servicio pedidos · puerto 5104

### F1-09 · Android (JSON): el cliente hace su pedido · PASA

**Objetivo.** El motor lo asigna al microhub más cercano que tiene todo: el nuevo.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: 54f1f132-88ef-4bfd-a294-dd9b25416283
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
  ],
  "operacion_uuid": "0e3a1c9a-d229-488b-833c-92d0b7b1f723"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 196 ms · traza `54f1f132-88ef-4bfd-a294-dd9b25416283`

```json
{
  "id": 386,
  "folio": "PED-20261126-000386",
  "estado": "asignado",
  "zona_id": 3,
  "microhub_id": 7,
  "subtotal": 378.0,
  "costo_envio": 0.0,
  "total": 378.0,
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
    "microhub_ganador_id": 7,
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
    "producto_id": 51,
    "cantidad": -3,
    "existencia_resultante": 9
  }
]
```

### F1-10 · El operador prepara el pedido · PASA

**Objetivo.** La transición la valida el motor.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/386/estado`

```http
Accept: application/json
X-Traza-Id: f691c711-2ea7-447e-8cf5-51b4f065fea8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1MSIs…(295 caracteres)
Content-Type: application/json
```

```json
{
  "estado": "en_preparacion"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 62 ms · traza `f691c711-2ea7-447e-8cf5-51b4f065fea8`

```json
{
  "id": 386,
  "folio": "PED-20261126-000386",
  "estado": "en_preparacion",
  "zona": {
    "id": 3,
    "nombre": "Paseo de San Bernabé"
  },
  "microhub_id": 7,
  "total": 378.0,
  "creado_en": "2026-11-26T23:28:56-06:00"
}
```

### F1-11 · El operador lo marca listo · PASA

**Objetivo.** Queda disponible para despacho.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/386/listo`

```http
Accept: application/json
X-Traza-Id: 6ff995eb-792a-4dfa-a05f-d49067daf9c0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1MSIs…(295 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 200 (esperado 200) · 43 ms · traza `6ff995eb-792a-4dfa-a05f-d49067daf9c0`

```json
{
  "id": 386,
  "estado": "en_preparacion",
  "listo_en": "2026-11-26T23:28:56-06:00"
}
```

## Servicio rutas · puerto 5118

### F1-12 · Proponer la ruta de despacho · PASA

**Objetivo.** Agrupa, asigna repartidor y ordena las paradas (algoritmo de rutas).

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/json
X-Traza-Id: ce1566e5-2678-4a9a-9dd8-92f447f3c203
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1MSIs…(295 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 7,
  "pedido_ids": [
    386
  ],
  "repartidor_ids": [
    7
  ],
  "metodo": "automatico",
  "guardar": true
}
```

**Respuesta.** HTTP 201 (esperado 201) · 176 ms · traza `ce1566e5-2678-4a9a-9dd8-92f447f3c203`

```json
{
  "id": 14,
  "estado": "propuesto",
  "version": 1,
  "microhub": {
    "id": 7,
    "nombre": "Microhub 64AC6"
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
            "id": 386,
            "folio": "PED-20261126-000386"
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
X-Traza-Id: 700db20e-e287-4c4d-a528-1e0cd0f78cf3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1MSIs…(295 caracteres)
Content-Type: application/json
```

```json
{
  "pedido_id": 386,
  "repartidor_id": 7,
  "orden_parada": 1
}
```

**Respuesta.** HTTP 201 (esperado 201) · 46 ms · traza `700db20e-e287-4c4d-a528-1e0cd0f78cf3`

```json
{
  "entrega_id": 149,
  "pedido_id": 386,
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
    "referencia_id": "149"
  }
]
```

### F1-14 · Android: el repartidor ve su parada · PASA

**Objetivo.** Sesión validada en Redis.

**Petición.** `GET http://entregas:5105/api/v1/entregas/mias?por_pagina=50`

```http
Accept: application/json
X-Traza-Id: 2871c414-15f6-477b-bf8d-b8d58fc6beea
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 40 ms · traza `2871c414-15f6-477b-bf8d-b8d58fc6beea`

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
      "id": 149,
      "pedido_id": 386,
      "folio": "PED-20261126-000386",
      "estado_pedido": "en_ruta",
      "orden_parada": 1,
      "direccion": "Nogal 1440, Paseo de San Bernabé",
      "zona": "Paseo de San Bernabé",
      "distancia_km": null,
      "minutos_estimados": null,
      "total": 378.0
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

**Petición.** `POST http://seguimiento:5110/api/v1/seguimiento/149/ubicaciones`

```http
Accept: application/json
X-Traza-Id: ef25b460-1aad-4149-a0a8-433a780807a0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "puntos": [
    {
      "latitud": 25.760195,
      "longitud": -100.370891,
      "capturado_en": "2026-11-27T05:24:56.814241+00:00"
    },
    {
      "latitud": 25.759995,
      "longitud": -100.371091,
      "capturado_en": "2026-11-27T05:27:56.814266+00:00"
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 39 ms · traza `ef25b460-1aad-4149-a0a8-433a780807a0`

```json
{
  "recibidos": 2
}
```

## Servicio documentos · puerto 5107

### F1-16 · La foto de evidencia queda en el almacén · PASA

**Objetivo.** En la base solo sus datos; se descarga con un enlace firmado.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b09151845ba3a5d167639b4/enlace`

```http
Accept: application/json
X-Traza-Id: 423a9a78-05aa-4917-8d97-918646152063
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 152 ms · traza `423a9a78-05aa-4917-8d97-918646152063`

```json
{
  "id": "6b09151845ba3a5d167639b4",
  "nombre": "evidencia-flujo1-64AC6.jpg",
  "url_firmada": "https://storage.googleapis.com/microhubs-evidencias-637044/d…(1005 caracteres)",
  "metodo": "GET",
  "segundos": 300,
  "expira_en": "2026-11-26T23:33:57-06:00"
}
```

**Evidencia en MongoDB.** `db.documentos.findOne({_id}) sin contenido`

```json
{
  "_id": "6b09151845ba3a5d167639b4",
  "nombre": "evidencia-flujo1-64AC6.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "149"
  },
  "subido_por": 7,
  "creado_en": "2026-11-27 05:28:56.872000+00:00",
  "ruta": "documentos/2026/11/6b09151845ba3a5d167639b4.jpg",
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

**Petición.** `POST http://entregas:5105/api/v1/entregas/149/resultado`

```http
Accept: application/json
X-Traza-Id: 3fe47ece-b793-4f8b-8787-7217b3e43400
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 378.0,
  "cambio_entregado": 0,
  "ubicacion": {
    "latitud": 25.759995,
    "longitud": -100.371091
  },
  "evidencia_ids": [
    "6b09151845ba3a5d167639b4"
  ],
  "capturado_en": "2026-11-27T05:28:57.239364+00:00",
  "id_cliente_local": "7887c802-d35f-42e3-a074-ab2261089855"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 92 ms · traza `3fe47ece-b793-4f8b-8787-7217b3e43400`

```json
{
  "entrega_id": 149,
  "pedido_id": 386,
  "estado_pedido": "entregado",
  "cerrado_en": "2026-11-26T23:28:57-06:00",
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
    "usuario_id": 51,
    "proceso": null
  },
  {
    "estado_anterior": "en_preparacion",
    "estado_nuevo": "en_ruta",
    "usuario_id": 51,
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
X-Traza-Id: fc72e069-cb34-4e79-84e1-e79b891c834c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 52 ms · traza `fc72e069-cb34-4e79-84e1-e79b891c834c`

```json
{
  "datos": [
    {
      "id": 319,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000386",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "386"
      },
      "creada_en": "2026-11-26T23:28:57-06:00"
    },
    {
      "id": 317,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000385",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "385"
      },
      "creada_en": "2026-11-26T15:59:12-06:00"
    },
    {
      "id": 289,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000374",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "374"
      },
      "creada_en": "2026-11-26T15:50:54-06:00"
    },
    {
      "id": 288,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000373",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "373"
      },
      "creada_en": "2026-11-26T15:50:33-06:00"
    },
    {
      "id": 287,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000372",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "372"
      },
      "creada_en": "2026-11-26T15:50:20-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 179,
    "paginas": 36
  }
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F1-19 · El auditor reconstruye la historia del pedido · PASA

**Objetivo.** Bitácora, estados, inventario y archivos en una línea de tiempo.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/pedido/386`

```http
Accept: application/json
X-Traza-Id: beb39fe0-499c-4a0a-a160-e66e720ab5a4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 124 ms · traza `beb39fe0-499c-4a0a-a160-e66e720ab5a4`

```json
{
  "objeto": {
    "tipo": "pedido",
    "id": "386"
  },
  "total": 15,
  "eventos": [
    {
      "fecha": "2026-11-26T23:28:56-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "actualizado_en = 2026-11-26T23:28:56.270774-06:00; asignado_en = None; cerrado_en = None; cliente_id = 1",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "386"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": null,
          "nuevo": "2026-11-26T23:28:56.270774-06:00"
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
          "nuevo": "2026-11-26T23:28:56.270774-06:00"
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
          "nuevo": "PED-20261126-000386"
        },
        {
          "campo": "id",
          "anterior": null,
          "nuevo": "386"
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
      "fecha": "2026-11-26T23:28:56-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "asignado_en = 2026-11-26T23:28:56.270774-06:00; estado: creado → asignado; microhub_id = 7",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "386"
      },
      "cambios": [
        {
          "campo": "asignado_en",
          "anterior": null,
          "nuevo": "2026-11-26T23:28:56.270774-06:00"
        },
        {
          "campo": "estado",
          "anterior": "creado",
          "nuevo": "asignado"
        },
        {
          "campo": "microhub_id",
          "anterior": null,
          "nuevo": "7"
        }
      ]
    },
    {
      "fecha": "2026-11-26T23:28:56-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "nuevo → creado",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "386"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T23:28:56-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "creado → asignado",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "386"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T23:28:56-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -3 de producto 31 en microhub 7 (existencia 9)",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "7-31"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T23:28:56-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -3 de producto 51 en microhub 7 (existencia 9)",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "7-51"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T23:28:56-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-26T23:28:56.270774-06:00 → 2026-11-26T23:28:56.443825-06:00; estado: asignado → en_preparacion",
      "usuario": {
        "id": 51,
        "nombre": "Operador 64AC6"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "386"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-26T23:28:56.270774-06:00",
          "nuevo": "2026-11-26T23:28:56.443825-06:00"
        },
        {
          "campo": "estado",
          "anterior": "asignado",
          "nuevo": "en_preparacion"
        }
      ]
    },
    {
      "fecha": "2026-11-26T23:28:56-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "asignado → en_preparacion",
      "usuario": {
        "id": 51,
        "nombre": "Operador 64AC6"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "386"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T23:28:56-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "listo_en = 2026-11-26T23:28:56.506459-06:00",
      "usuario": {
        "id": 51,
        "nombre": "Operador 64AC6"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "386"
      },
      "cambios": [
        {
          "campo": "listo_en",
          "anterior": null,
          "nuevo": "2026-11-26T23:28:56.506459-06:00"
        }
      ]
    },
    {
      "fecha": "2026-11-26T23:28:56-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "asignada_en = 2026-11-26T23:28:56.722734-06:00; cambio_entregado = None; capturado_en = None; cerrada_por_usuario_id = None",
      "usuario": {
        "id": 51,
        "nombre": "Operador 64AC6"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "149"
      },
      "cambios": [
        {
          "campo": "asignada_en",
          "anterior": null,
          "nuevo": "2026-11-26T23:28:56.722734-06:00"
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
      "fecha": "2026-11-26T23:28:56-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-26T23:28:56.443825-06:00 → 2026-11-26T23:28:56.722734-06:00; estado: en_preparacion → en_ruta",
      "usuario": {
        "id": 51,
        "nombre": "Operador 64AC6"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "386"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-26T23:28:56.443825-06:00",
          "nuevo": "2026-11-26T23:28:56.722734-06:00"
        },
        {
          "campo": "estado",
          "anterior": "en_preparacion",
          "nuevo": "en_ruta"
        }
      ]
    },
    {
      "fecha": "2026-11-26T23:28:56-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "en_preparacion → en_ruta",
      "usuario": {
        "id": 51,
        "nombre": "Operador 64AC6"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "386"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T23:28:57-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "cambio_entregado = 0.0; capturado_en = 2026-11-26T23:28:57.2…(145 caracteres)",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "149"
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
          "nuevo": "2026-11-26T23:28:57.239364-06:00"
        },
        {
          "campo": "cerrada_por_usuario_id",
          "anterior": null,
          "nuevo": "7"
        },
        {
          "campo": "cierre_en",
          "anterior": null,
          "nuevo": "2026-11-26T23:28:57.273982-06:00"
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
          "nuevo": "[\"6b09151845ba3a5d167639b4\"]"
        },
        {
          "campo": "evidencia_url",
          "anterior": null,
          "nuevo": "/api/v1/documentos/6b09151845ba3a5d167639b4"
        },
        {
          "campo": "id_cliente_local",
          "anterior": null,
          "nuevo": "7887c802-d35f-42e3-a074-ab2261089855"
        },
        {
          "campo": "monto_cobrado",
          "anterior": null,
          "nuevo": "378.0"
        },
        {
          "campo": "resultado",
          "anterior": null,
          "nuevo": "entregado"
        }
      ]
    },
    {
      "fecha": "2026-11-26T23:28:57-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-26T23:28:56.722734-06:00 → 2026-11-2…(159 caracteres)",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "386"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-26T23:28:56.722734-06:00",
          "nuevo": "2026-11-26T23:28:57.273982-06:00"
        },
        {
          "campo": "cerrado_en",
          "anterior": null,
          "nuevo": "2026-11-26T23:28:57.273982-06:00"
        },
        {
          "campo": "estado",
          "anterior": "en_ruta",
          "nuevo": "entregado"
        }
      ]
    },
    {
      "fecha": "2026-11-26T23:28:57-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "en_ruta → entregado",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "386"
      },
      "cambios": []
    }
  ]
}
```

## Servicio reportes · puerto 5123

### F1-20 · Visualización: el microhub nuevo ya aparece en la comparación · PASA

**Objetivo.** Datos listos para Highcharts.

**Petición.** `GET http://reportes:5123/api/v1/reportes/comparacion_microhubs/grafica?microhub_id=7`

```http
Accept: application/json
X-Traza-Id: e9e13077-eea2-4fb3-9154-54a4d35bc23d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 107 ms · traza `e9e13077-eea2-4fb3-9154-54a4d35bc23d`

```json
{
  "reporte": "comparacion_microhubs",
  "titulo": "Comparación entre microhubs",
  "tipo": "column",
  "unidad": "pedidos / MXN",
  "categorias": [
    "Microhub 64AC6"
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
        378.0
      ]
    }
  ]
}
```

## Servicio microhubs · puerto 5109

### F1-21 · Cierre: dar de baja el microhub de la demostración · PASA

**Objetivo.** Baja lógica; conserva su historia.

**Petición.** `DELETE http://microhubs:5109/api/v1/microhubs/7`

```http
Accept: application/json
X-Traza-Id: d7fe5e22-c430-4413-8d71-80e0198fc805
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 41 ms · traza `d7fe5e22-c430-4413-8d71-80e0198fc805`

```json
(sin cuerpo)
```

## Servicio pedidos · puerto 5104

### F2-01 · Android: un cliente compra y el inventario baja · PASA

**Objetivo.** El motor descuenta inventario en la misma transacción.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: b6f7c76d-6f8b-4fbc-9b96-36e6572bbac8
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
  "operacion_uuid": "444b9fac-9d4d-477a-b636-27b0d66394ba"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 151 ms · traza `b6f7c76d-6f8b-4fbc-9b96-36e6572bbac8`

```json
{
  "id": 387,
  "folio": "PED-20261126-000387",
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
    "existencia_resultante": 62
  }
]
```

## Servicio inventario · puerto 5111

### F2-02 · El operador fija el mínimo y nace la alerta · PASA

**Objetivo.** El trigger avisa del faltante.

**Petición.** `PATCH http://inventario:5111/api/v1/inventario/1/51/minimo`

```http
Accept: application/json
X-Traza-Id: 7c0c4981-1b00-41f7-9208-a7cc9fe312d7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "minimo": 127
}
```

**Respuesta.** HTTP 200 (esperado 200) · 193 ms · traza `7c0c4981-1b00-41f7-9208-a7cc9fe312d7`

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
  "existencia": 117,
  "minimo": 127,
  "reservado": 0,
  "disponible": 117,
  "estado": "bajo_minimo",
  "actualizado_en": "2026-11-26T23:28:58-06:00"
}
```

### F2-03 · La alerta de faltante · PASA

**Objetivo.** Qué producto, cuánto falta y qué tan grave es.

**Petición.** `GET http://inventario:5111/api/v1/inventario/alertas?microhub_id=1&por_pagina=100`

```http
Accept: application/json
X-Traza-Id: 733e26e7-0e3e-4b84-9ab0-ff396612563b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 66 ms · traza `733e26e7-0e3e-4b84-9ab0-ff396612563b`

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
      "existencia": 117,
      "minimo": 127,
      "disponible": 117,
      "faltante": 10,
      "severidad": "baja"
    },
    {
      "microhub": {
        "id": 1,
        "nombre": "Microhub San Bernabé Centro"
      },
      "producto": {
        "id": 16,
        "clave_interna": "AB-016",
        "nombre": "Galletas María"
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
X-Traza-Id: 102e477c-d334-440b-9fbc-34c50f99dea7
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

**Respuesta.** HTTP 201 (esperado 201) · 82 ms · traza `102e477c-d334-440b-9fbc-34c50f99dea7`

```json
{
  "id": 15,
  "folio": "SC-20261126-000015",
  "microhub_id": 1,
  "estado": "pendiente",
  "motivo": "Faltante detectado por el sistema",
  "solicitada_por": 2,
  "decidida_por": null,
  "decision_motivo": null,
  "decidida_en": null,
  "creada_en": "2026-11-26T23:28:59-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/15/decision`

```http
Accept: application/json
X-Traza-Id: 0b012354-4887-47e2-a23e-e8aa5f0ade73
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aprobada",
  "motivo": "Con presupuesto"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 64 ms · traza `0b012354-4887-47e2-a23e-e8aa5f0ade73`

```json
{
  "id": 15,
  "folio": "SC-20261126-000015",
  "microhub_id": 1,
  "estado": "aprobada",
  "motivo": "Faltante detectado por el sistema",
  "solicitada_por": 2,
  "decidida_por": 1,
  "decision_motivo": "Con presupuesto",
  "decidida_en": "2026-11-26T23:28:59-06:00",
  "creada_en": "2026-11-26T23:28:59-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/15/ordenar`

```http
Accept: application/json
X-Traza-Id: 88585f7e-e71a-4ebe-9702-f65779ef3bd1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 201 (esperado 201) · 260 ms · traza `88585f7e-e71a-4ebe-9702-f65779ef3bd1`

```json
{
  "solicitud_id": 15,
  "ordenes": [
    {
      "id": 11,
      "folio": "OC-20261126-000011",
      "solicitud_id": 15,
      "proveedor": {
        "id": 3,
        "nombre": "Mayorista San Nicolás"
      },
      "microhub_id": 1,
      "estado": "emitida",
      "fecha_esperada": "2026-11-30",
      "total": 4624.0,
      "creada_en": "2026-11-26T23:28:59-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/11/recepcion`

```http
Accept: application/json
X-Traza-Id: da5a9bff-a998-4f36-9255-6742dd17030a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "operacion_uuid": "70be3dfc-83cc-45b7-a590-cbe3c6f2ad19",
  "nota": "Completo",
  "lineas": [
    {
      "producto_id": 51,
      "cantidad": 100
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 224 ms · traza `da5a9bff-a998-4f36-9255-6742dd17030a`

```json
{
  "orden": {
    "id": 11,
    "folio": "OC-20261126-000011",
    "solicitud_id": 15,
    "proveedor": {
      "id": 3,
      "nombre": "Mayorista San Nicolás"
    },
    "microhub_id": 1,
    "estado": "recibida",
    "fecha_esperada": "2026-11-30",
    "total": 4624.0,
    "creada_en": "2026-11-26T23:28:59-06:00",
    "cerrada_en": "2026-11-26T23:28:59-06:00",
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
    "existencia": 217,
    "minimo": 127
  }
]
```

## Servicio documentos · puerto 5107

### F2-08 · La remisión firmada queda en el almacén · PASA

**Objetivo.** Archivo con enlace firmado.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b09151bef30c8ea07f5f6ab/enlace`

```http
Accept: application/json
X-Traza-Id: 87ad9e81-ea9f-4aa2-b3e0-7b1eb5c83664
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 114 ms · traza `87ad9e81-ea9f-4aa2-b3e0-7b1eb5c83664`

```json
{
  "id": "6b09151bef30c8ea07f5f6ab",
  "nombre": "remision-11.jpg",
  "url_firmada": "https://storage.googleapis.com/microhubs-evidencias-637044/d…(994 caracteres)",
  "metodo": "GET",
  "segundos": 300,
  "expira_en": "2026-11-26T23:33:59-06:00"
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F2-09 · Trazabilidad del producto en el microhub · PASA

**Objetivo.** Salida por pedido y recepción por orden.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/inventario?microhub_id=1&producto_id=51`

```http
Accept: application/json
X-Traza-Id: 5e6300bd-e104-4620-9cb3-14f5b4721942
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 37 ms · traza `5e6300bd-e104-4620-9cb3-14f5b4721942`

```json
{
  "objeto": {
    "tipo": "inventario",
    "id": "1-51"
  },
  "total": 11,
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
X-Traza-Id: c52faf08-62cc-496e-a3ee-e25a4c249ffb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 643 ms · traza `c52faf08-62cc-496e-a3ee-e25a4c249ffb`

```json
﻿Microhub,Producto,Existencia,Mínimo,Disponible,Faltante,Severidad
Microhub San Bernabé Centro,Agua purificada,0,10,0,10,agotado
Microhub San Bernabé Centro,Galletas María,7,8,7,1,baja
Total,,,,,11,

```

## Servicio pedidos · puerto 5104

### F3-01 · El cliente hace un pedido · PASA

**Objetivo.** Punto de partida del recorrido.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: d44dbf02-4900-4dc9-8e9a-74ea3b9d295e
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

**Respuesta.** HTTP 201 (esperado 201) · 135 ms · traza `d44dbf02-4900-4dc9-8e9a-74ea3b9d295e`

```json
{
  "id": 388,
  "folio": "PED-20261126-000388",
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
X-Traza-Id: 70bcd147-eeb9-4bbe-872d-40f7b4c5fb2c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
Content-Type: application/json
```

```json
{
  "pedido_id": 388,
  "repartidor_id": 7
}
```

**Respuesta.** HTTP 201 (esperado 201) · 46 ms · traza `70bcd147-eeb9-4bbe-872d-40f7b4c5fb2c`

```json
{
  "entrega_id": 150,
  "pedido_id": 388,
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
X-Traza-Id: 98f7bfb7-3c2f-4933-ab9d-be2d2812ddf7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "0aa9b571-0b60-47bd-8f39-db7addbb0b17",
  "dispositivo": "android-flujo-db5020",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "3af4f17e-60ce-4293-855d-cffc991a1b38",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-27T05:09:02.004745+00:00",
      "datos": {
        "entrega_id": 150,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-27T05:09:02.004767+00:00"
          },
          {
            "latitud": 25.7491,
            "longitud": -100.3611,
            "capturado_en": "2026-11-27T05:14:02.004775+00:00"
          }
        ]
      }
    },
    {
      "operacion_uuid": "5623c267-3d16-45fb-a995-ac9392c3419e",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-27T05:17:02.004805+00:00",
      "datos": {
        "entrega_id": 150,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "El cliente no estaba en su domicilio",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b09151def30c8ea07f5f6b0"
        ],
        "capturado_en": "2026-11-27T05:17:02.004814+00:00"
      }
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 330 ms · traza `98f7bfb7-3c2f-4933-ab9d-be2d2812ddf7`

```json
{
  "id": 8,
  "lote_uuid": "0aa9b571-0b60-47bd-8f39-db7addbb0b17",
  "dispositivo": "android-flujo-db5020",
  "recibido_en": "2026-11-26T23:29:02-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 0,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "3af4f17e-60ce-4293-855d-cffc991a1b38",
      "tipo": "ubicaciones",
      "estado": "aplicada",
      "duplicada": false,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    },
    {
      "operacion_uuid": "5623c267-3d16-45fb-a995-ac9392c3419e",
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
    "creada_en": "2026-11-26 23:09:02.004745-06:00"
  },
  {
    "tipo": "entrega_resultado",
    "estado": "aplicada",
    "intentos": 1,
    "creada_en": "2026-11-26 23:17:02.004805-06:00"
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
X-Traza-Id: b6bbdc1f-1ced-4dfa-bf4b-e25679e90ed4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "0aa9b571-0b60-47bd-8f39-db7addbb0b17",
  "dispositivo": "android-flujo-db5020",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "3af4f17e-60ce-4293-855d-cffc991a1b38",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-27T05:09:02.004745+00:00",
      "datos": {
        "entrega_id": 150,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-27T05:09:02.004767+00:00"
          },
          {
            "latitud": 25.7491,
            "longitud": -100.3611,
            "capturado_en": "2026-11-27T05:14:02.004775+00:00"
          }
        ]
      }
    },
    {
      "operacion_uuid": "5623c267-3d16-45fb-a995-ac9392c3419e",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-27T05:17:02.004805+00:00",
      "datos": {
        "entrega_id": 150,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "El cliente no estaba en su domicilio",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b09151def30c8ea07f5f6b0"
        ],
        "capturado_en": "2026-11-27T05:17:02.004814+00:00"
      }
    }
  ]
}
```

**Respuesta.** HTTP 200 (esperado 200) · 161 ms · traza `b6bbdc1f-1ced-4dfa-bf4b-e25679e90ed4`

```json
{
  "id": 8,
  "lote_uuid": "0aa9b571-0b60-47bd-8f39-db7addbb0b17",
  "dispositivo": "android-flujo-db5020",
  "recibido_en": "2026-11-26T23:29:02-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 2,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "3af4f17e-60ce-4293-855d-cffc991a1b38",
      "tipo": "ubicaciones",
      "estado": "aplicada",
      "duplicada": true,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    },
    {
      "operacion_uuid": "5623c267-3d16-45fb-a995-ac9392c3419e",
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
X-Traza-Id: a52f4021-8115-45b5-8c72-3ffdd71cea9e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 32 ms · traza `a52f4021-8115-45b5-8c72-3ffdd71cea9e`

```json
{
  "datos": [
    {
      "id": 326,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000388",
      "mensaje": "El pedido cambió a entrega_fallida.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "388"
      },
      "creada_en": "2026-11-26T23:29:02-06:00"
    },
    {
      "id": 324,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000387",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "387"
      },
      "creada_en": "2026-11-26T23:29:00-06:00"
    },
    {
      "id": 319,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000386",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "386"
      },
      "creada_en": "2026-11-26T23:28:57-06:00"
    },
    {
      "id": 317,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000385",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "385"
      },
      "creada_en": "2026-11-26T15:59:12-06:00"
    },
    {
      "id": 289,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000374",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "374"
      },
      "creada_en": "2026-11-26T15:50:54-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 181,
    "paginas": 37
  }
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F3-06 · El auditor revisa la entrega · PASA

**Objetivo.** Bitácora y archivos de la entrega.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/entrega/150`

```http
Accept: application/json
X-Traza-Id: bebb0cb9-5859-4656-a407-52599ebc93fd
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 39 ms · traza `bebb0cb9-5859-4656-a407-52599ebc93fd`

```json
{
  "objeto": {
    "tipo": "entrega",
    "id": "150"
  },
  "total": 3,
  "eventos": [
    {
      "fecha": "2026-11-26T23:29:01-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "asignada_en = 2026-11-26T23:29:01.898027-06:00; cambio_entregado = None; capturado_en = None; cerrada_por_usuario_id = None",
      "usuario": {
        "id": 3,
        "nombre": "María José Cedillo Mata"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "150"
      },
      "cambios": [
        {
          "campo": "asignada_en",
          "anterior": null,
          "nuevo": "2026-11-26T23:29:01.898027-06:00"
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
      "fecha": "2026-11-26T23:29:01-06:00",
      "origen": "documentos",
      "accion": "documento_subido",
      "descripcion": "evidencia-flujo3-150.jpg (276 bytes, sha256 7f6025cd8a98…)",
      "usuario": {
        "id": 7,
        "nombre": null
      },
      "entidad": {
        "tipo": "documento",
        "id": "6b09151def30c8ea07f5f6b0"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-26T23:29:02-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "cambio_entregado = 0.0; capturado_en = 2026-11-26T23:17:02.0…(145 caracteres)",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "150"
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
          "nuevo": "2026-11-26T23:17:02.004814-06:00"
        },
        {
          "campo": "cerrada_por_usuario_id",
          "anterior": null,
          "nuevo": "7"
        },
        {
          "campo": "cierre_en",
          "anterior": null,
          "nuevo": "2026-11-26T23:29:02.197699-06:00"
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
          "nuevo": "[\"6b09151def30c8ea07f5f6b0\"]"
        },
        {
          "campo": "evidencia_url",
          "anterior": null,
          "nuevo": "/api/v1/documentos/6b09151def30c8ea07f5f6b0"
        },
        {
          "campo": "id_cliente_local",
          "anterior": null,
          "nuevo": "5623c267-3d16-45fb-a995-ac9392c3419e"
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
X-Traza-Id: 230f37f0-a818-4472-8709-e64568406163
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 41 ms · traza `230f37f0-a818-4472-8709-e64568406163`

```json
{
  "datos": [
    {
      "id": 1831,
      "microhub_id": 2,
      "producto_id": 51,
      "tipo": "devolucion_cancelacion",
      "cantidad": 3,
      "existencia_resultante": 72,
      "referencia": {
        "tipo": "pedido",
        "id": "388"
      },
      "motivo": "Entrega fallida: la mercancía regresa al microhub.",
      "usuario_id": 7,
      "fecha": "2026-11-26T23:29:02-06:00"
    },
    {
      "id": 1830,
      "microhub_id": 2,
      "producto_id": 32,
      "tipo": "devolucion_cancelacion",
      "cantidad": 3,
      "existencia_resultante": 22,
      "referencia": {
        "tipo": "pedido",
        "id": "388"
      },
      "motivo": "Entrega fallida: la mercancía regresa al microhub.",
      "usuario_id": 7,
      "fecha": "2026-11-26T23:29:02-06:00"
    },
    {
      "id": 1829,
      "microhub_id": 2,
      "producto_id": 51,
      "tipo": "salida_pedido",
      "cantidad": -3,
      "existencia_resultante": 69,
      "referencia": {
        "tipo": "pedido",
        "id": "388"
      },
      "motivo": null,
      "usuario_id": 9,
      "fecha": "2026-11-26T23:29:01-06:00"
    },
    {
      "id": 1828,
      "microhub_id": 2,
      "producto_id": 32,
      "tipo": "salida_pedido",
      "cantidad": -3,
      "existencia_resultante": 19,
      "referencia": {
        "tipo": "pedido",
        "id": "388"
      },
      "motivo": null,
      "usuario_id": 9,
      "fecha": "2026-11-26T23:29:01-06:00"
    },
    {
      "id": 1827,
      "microhub_id": 2,
      "producto_id": 51,
      "tipo": "devolucion_cancelacion",
      "cantidad": 10,
      "existencia_resultante": 72,
      "referencia": {
        "tipo": "pedido",
        "id": "387"
      },
      "motivo": "Cierre del flujo de demostración",
      "usuario_id": 1,
      "fecha": "2026-11-26T23:29:00-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 1129,
    "paginas": 226
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
    "existencia_resultante": 19
  },
  {
    "tipo": "salida_pedido",
    "producto_id": 51,
    "cantidad": -3,
    "existencia_resultante": 69
  },
  {
    "tipo": "devolucion_cancelacion",
    "producto_id": 32,
    "cantidad": 3,
    "existencia_resultante": 22
  },
  {
    "tipo": "devolucion_cancelacion",
    "producto_id": 51,
    "cantidad": 3,
    "existencia_resultante": 72
  }
]
```

## Servicio reportes · puerto 5123

### F3-08 · Reporte del periodo en CSV · PASA

**Objetivo.** La entrega ya cuenta en los reportes.

**Petición.** `GET http://reportes:5123/api/v1/reportes/pedidos_por_dia/exportar?formato=csv`

```http
Accept: application/json
X-Traza-Id: 4515bdeb-64eb-4891-82db-299a3ec59dd6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 417 ms · traza `4515bdeb-64eb-4891-82db-299a3ec59dd6`

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
2026-11-26,24,134,5807.00,241.96,1
Total,122,601,20501.80,168.05,38

```

**Evidencia en PostgreSQL.** `SELECT reporte, formato, filas, left(sha256, 16) AS sha256 FROM reporte_exportacion ORDER BY id DESC LIMIT 1`

```json
[
  {
    "reporte": "pedidos_por_dia",
    "formato": "csv",
    "filas": 29,
    "sha256": "a8981cf2621eb317"
  }
]
```
