# Procesos integrales de principio a fin


Generado el 2026-11-27 17:42 contra los servicios en ejecución. 40 de 40 casos pasan.

## Servicio planeacion · puerto 5106

### F1-01 · Escritorio (XML): el planeador registra una ubicación candidata · PASA

**Objetivo.** Planeación de ubicación.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos`

```http
Accept: application/xml
X-Traza-Id: 6fdd613b-bf3c-488d-99f4-7cdfb0800062
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><candidato_nuevo xmlns="urn:microhubs:v1"><clave>********</clave><nombre>Ubicación del flujo 17BD1</nombre><latitud>25.760195</latitud><longitud>-100.370891</longitud><renta_estimada>15000.00</renta_estimada><nomina_estimada>36000.00</nomina_estimada><servicios_estimados>6000.00</servicios_estimados><otros_costos>4000.00</otros_costos><superficie_m2>100</superficie_m2><capacidad_fisica>120</capacidad_fisica><accesibilidad_vial>8</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km></candidato_nuevo>
```

**Respuesta.** HTTP 201 (esperado 201) · 193 ms · traza `6fdd613b-bf3c-488d-99f4-7cdfb0800062`

```xml
<?xml version='1.0' encoding='utf-8'?>
<candidato xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>210</id><clave>FL-17BD1</clave><nombre>Ubicación del flujo 17BD1</nombre><latitud>25.760195</latitud><longitud>-100.370891</longitud><renta_estimada>15000.00</renta_estimada><nomina_estimada>36000.00</nomina_estimada><servicios_estimados>6000.00</servicios_estimados><otros_costos>4000.00</otros_costos><costo_fijo>61000.00</costo_fijo><superficie_m2>100</superficie_m2><capacidad_fisica>120</capacidad_fisica><accesibilidad_vial>8</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato>
```

**Evidencia en PostgreSQL.** `SELECT id, clave, nombre, costo_fijo, decision FROM ubicacion_candidata WHERE clave = %s`

```json
[
  {
    "id": 210,
    "clave": "FL-17BD1",
    "nombre": "Ubicación del flujo 17BD1",
    "costo_fijo": "61000.00",
    "decision": "pendiente"
  }
]
```

### F1-02 · El planeador simula la operación de la candidata · PASA

**Objetivo.** Capacidad, utilización y decisión sugerida (MongoDB).

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/210/simular`

```http
Accept: application/json
X-Traza-Id: f40dfc86-6541-437c-9104-b27191dc9d0c
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

**Respuesta.** HTTP 200 (esperado 200) · 313 ms · traza `f40dfc86-6541-437c-9104-b27191dc9d0c`

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
X-Traza-Id: 56a2b96a-b7fd-4bfb-b8a5-245bcb922513
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "candidato_id": 210,
  "pedidos_dia": 100,
  "ticket": 180,
  "margen_bruto": 0.3,
  "costos_fijos": 61000,
  "costo_variable_pedido": 22
}
```

**Respuesta.** HTTP 200 (esperado 200) · 31 ms · traza `56a2b96a-b7fd-4bfb-b8a5-245bcb922513`

```json
{
  "id": null,
  "nombre": null,
  "objeto": {
    "tipo": "candidato",
    "id": 210,
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

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/210/decision`

```http
Accept: application/json
X-Traza-Id: 03edb2c0-3af0-44d6-a25b-d7aa36708844
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aceptado",
  "motivo": "Cubre la zona del cliente y la demanda esperada supera el equilibrio."
}
```

**Respuesta.** HTTP 200 (esperado 200) · 61 ms · traza `03edb2c0-3af0-44d6-a25b-d7aa36708844`

```json
{
  "id": 210,
  "clave": "********",
  "nombre": "Ubicación del flujo 17BD1",
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
X-Traza-Id: 15f0b14d-8fc5-48d8-84a1-059ed2dbd664
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "clave": "********",
  "nombre": "Microhub 17BD1",
  "direccion": "Ubicación aprobada en planeación",
  "latitud": 25.760195,
  "longitud": -100.370891,
  "radio_km": 1.5,
  "capacidad_turno": 120
}
```

**Respuesta.** HTTP 201 (esperado 201) · 54 ms · traza `15f0b14d-8fc5-48d8-84a1-059ed2dbd664`

```json
{
  "id": 11,
  "clave": "********",
  "nombre": "Microhub 17BD1",
  "latitud": 25.760195,
  "longitud": -100.370891,
  "radio_km": 1.5,
  "estatus": "activo"
}
```

## Servicio capacidad · puerto 5117

### F1-06 · Asignar personal al microhub · PASA

**Objetivo.** Operadores, repartidores y capacidad física.

**Petición.** `PUT http://capacidad:5117/api/v1/capacidad/recursos/11`

```http
Accept: application/json
X-Traza-Id: ccfc6480-264a-4cc2-be76-7e125a2afb23
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

**Respuesta.** HTTP 200 (esperado 200) · 138 ms · traza `ccfc6480-264a-4cc2-be76-7e125a2afb23`

```json
{
  "microhub": {
    "id": 11,
    "nombre": "Microhub 17BD1"
  },
  "operadores": 2,
  "repartidores": 2,
  "capacidad_fisica": 120,
  "actualizado_en": "2026-11-27T11:42:35-06:00"
}
```

## Servicio usuarios · puerto 5102

### F1-07 · Crear la cuenta del operador · PASA

**Objetivo.** Cuenta nueva con su perfil y su microhub.

**Petición.** `POST http://usuarios:5102/api/v1/usuarios`

```http
Accept: application/json
X-Traza-Id: 40c55472-92d8-42f1-bcfc-8e5333512fe6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Operador",
  "apellidos": "17BD1",
  "correo": "operador.17bd1@ejemplo.mx",
  "clave": "********",
  "rol": "operador",
  "microhub_id": 11
}
```

**Respuesta.** HTTP 201 (esperado 201) · 112 ms · traza `40c55472-92d8-42f1-bcfc-8e5333512fe6`

```json
{
  "id": 56,
  "nombre": "Operador",
  "apellidos": "17BD1",
  "correo": "operador.17bd1@ejemplo.mx",
  "telefono": null,
  "rol": "operador",
  "microhub": {
    "id": 11,
    "clave": "********",
    "nombre": "Microhub 17BD1"
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
X-Traza-Id: 37ffcf73-35ef-4bcf-ac6f-ddbdabc7437b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "origen_microhub_id": 1,
  "destino_microhub_id": 11,
  "producto_id": 51,
  "cantidad": 12,
  "motivo": "Inventario inicial del microhub nuevo",
  "operacion_uuid": "2d8da327-6446-4f17-b6a7-1c34755c5ccc"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 74 ms · traza `37ffcf73-35ef-4bcf-ac6f-ddbdabc7437b`

```json
{
  "producto_id": 51,
  "cantidad": 12,
  "duplicado": false,
  "origen": {
    "microhub_id": 1,
    "existencia": 293,
    "movimiento_id": 2759
  },
  "destino": {
    "microhub_id": 11,
    "existencia": 12,
    "movimiento_id": 2760
  }
}
```

### F1-08b · Surtir el microhub nuevo · PASA

**Objetivo.** Transferencia atómica desde MH-01.

**Petición.** `POST http://inventario:5111/api/v1/inventario/transferencias`

```http
Accept: application/json
X-Traza-Id: 331cf8db-25aa-4eec-8be4-611083450724
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "origen_microhub_id": 1,
  "destino_microhub_id": 11,
  "producto_id": 36,
  "cantidad": 12,
  "motivo": "Inventario inicial del microhub nuevo",
  "operacion_uuid": "b5590a47-499a-4836-a2ca-3d6377096424"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 62 ms · traza `331cf8db-25aa-4eec-8be4-611083450724`

```json
{
  "producto_id": 36,
  "cantidad": 12,
  "duplicado": false,
  "origen": {
    "microhub_id": 1,
    "existencia": 30,
    "movimiento_id": 2761
  },
  "destino": {
    "microhub_id": 11,
    "existencia": 12,
    "movimiento_id": 2762
  }
}
```

## Servicio pedidos · puerto 5104

### F1-09 · Android (JSON): el cliente hace su pedido · PASA

**Objetivo.** El motor lo asigna al microhub más cercano que tiene todo: el nuevo.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: 8139171c-2a1e-40fd-a679-b8d48d1cd958
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
      "producto_id": 36,
      "cantidad": 3
    }
  ],
  "operacion_uuid": "52be063c-f2c0-4e91-bd87-c22d25619ad8"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 169 ms · traza `8139171c-2a1e-40fd-a679-b8d48d1cd958`

```json
{
  "id": 651,
  "folio": "PED-20261127-000651",
  "estado": "asignado",
  "zona_id": 3,
  "microhub_id": 11,
  "subtotal": 342.0,
  "costo_envio": 0.0,
  "total": 342.0,
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
    "microhub_ganador_id": 11,
    "motivo": null
  }
]
```

**Evidencia en PostgreSQL.** `SELECT tipo, producto_id, cantidad, existencia_resultante FROM movimiento_inventario WHERE referencia_tipo = 'pedido' AND referencia_id = %s`

```json
[
  {
    "tipo": "salida_pedido",
    "producto_id": 36,
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

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/651/estado`

```http
Accept: application/json
X-Traza-Id: 9eaaceb7-7bc7-4f0d-80a5-6e4683eca2d8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NiIs…(296 caracteres)
Content-Type: application/json
```

```json
{
  "estado": "en_preparacion"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 69 ms · traza `9eaaceb7-7bc7-4f0d-80a5-6e4683eca2d8`

```json
{
  "id": 651,
  "folio": "PED-20261127-000651",
  "estado": "en_preparacion",
  "zona": {
    "id": 3,
    "nombre": "Paseo de San Bernabé"
  },
  "microhub_id": 11,
  "total": 342.0,
  "creado_en": "2026-11-27T11:42:36-06:00"
}
```

### F1-11 · El operador lo marca listo · PASA

**Objetivo.** Queda disponible para despacho.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/651/listo`

```http
Accept: application/json
X-Traza-Id: 47c4d506-ddf2-49cd-b94c-7acfa6853976
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NiIs…(296 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 200 (esperado 200) · 42 ms · traza `47c4d506-ddf2-49cd-b94c-7acfa6853976`

```json
{
  "id": 651,
  "estado": "en_preparacion",
  "listo_en": "2026-11-27T11:42:36-06:00"
}
```

## Servicio rutas · puerto 5118

### F1-12 · Proponer la ruta de despacho · PASA

**Objetivo.** Agrupa, asigna repartidor y ordena las paradas (algoritmo de rutas).

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/json
X-Traza-Id: b9fcc437-fe06-449a-a0a6-d269d2f580ef
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NiIs…(296 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 11,
  "pedido_ids": [
    651
  ],
  "repartidor_ids": [
    7
  ],
  "metodo": "automatico",
  "guardar": true
}
```

**Respuesta.** HTTP 201 (esperado 201) · 147 ms · traza `b9fcc437-fe06-449a-a0a6-d269d2f580ef`

```json
{
  "id": 26,
  "estado": "propuesto",
  "version": 1,
  "microhub": {
    "id": 11,
    "nombre": "Microhub 17BD1"
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
            "id": 651,
            "folio": "PED-20261127-000651"
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
X-Traza-Id: 6e78b04a-d09e-4c28-9225-a7c7849715c4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NiIs…(296 caracteres)
Content-Type: application/json
```

```json
{
  "pedido_id": 651,
  "repartidor_id": 7,
  "orden_parada": 1
}
```

**Respuesta.** HTTP 201 (esperado 201) · 49 ms · traza `6e78b04a-d09e-4c28-9225-a7c7849715c4`

```json
{
  "entrega_id": 190,
  "pedido_id": 651,
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
    "referencia_id": "190"
  }
]
```

### F1-14 · Android: el repartidor ve su parada · PASA

**Objetivo.** Sesión validada en Redis.

**Petición.** `GET http://entregas:5105/api/v1/entregas/mias?por_pagina=50`

```http
Accept: application/json
X-Traza-Id: 4d956392-db5f-4307-a496-d098235c2442
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 39 ms · traza `4d956392-db5f-4307-a496-d098235c2442`

```json
{
  "datos": [
    {
      "id": 181,
      "pedido_id": 638,
      "folio": "PED-20261127-000638",
      "estado_pedido": "en_ruta",
      "orden_parada": 1,
      "direccion": "Cerro Prieto 4059, Valles de San Bernabé",
      "zona": "Valles de San Bernabé",
      "distancia_km": 0.63,
      "minutos_estimados": 5.7,
      "total": 184.0
    },
    {
      "id": 185,
      "pedido_id": 641,
      "folio": "PED-20261127-000641",
      "estado_pedido": "en_ruta",
      "orden_parada": 1,
      "direccion": "Rodrigo Gómez 649, Valles de San Bernabé",
      "zona": "Valles de San Bernabé",
      "distancia_km": 0.74,
      "minutos_estimados": 10.0,
      "total": 155.0
    },
    {
      "id": 186,
      "pedido_id": 642,
      "folio": "PED-20261127-000642",
      "estado_pedido": "en_ruta",
      "orden_parada": 1,
      "direccion": "Nogal 2835, San Bernabé X (F-113)",
      "zona": "San Bernabé X (F-113)",
      "distancia_km": 0.68,
      "minutos_estimados": 10.0,
      "total": 127.0
    },
    {
      "id": 190,
      "pedido_id": 651,
      "folio": "PED-20261127-000651",
      "estado_pedido": "en_ruta",
      "orden_parada": 1,
      "direccion": "Nogal 1440, Paseo de San Bernabé",
      "zona": "Paseo de San Bernabé",
      "distancia_km": null,
      "minutos_estimados": null,
      "total": 342.0
    },
    {
      "id": 182,
      "pedido_id": 639,
      "folio": "PED-20261127-000639",
      "estado_pedido": "en_ruta",
      "orden_parada": 2,
      "direccion": "Emiliano Zapata 4397, Valles de San Bernabé",
      "zona": "Valles de San Bernabé",
      "distancia_km": 0.29,
      "minutos_estimados": 10.5,
      "total": 274.5
    },
    {
      "id": 187,
      "pedido_id": 643,
      "folio": "PED-20261127-000643",
      "estado_pedido": "en_ruta",
      "orden_parada": 2,
      "direccion": "Valle Alto 3509, Valles de San Bernabé",
      "zona": "Valles de San Bernabé",
      "distancia_km": 0.26,
      "minutos_estimados": 16.0,
      "total": 187.0
    },
    {
      "id": 183,
      "pedido_id": 640,
      "folio": "PED-20261127-000640",
      "estado_pedido": "en_ruta",
      "orden_parada": 3,
      "direccion": "Emiliano Zapata 231, Valles de San Bernabé",
      "zona": "Valles de San Bernabé",
      "distancia_km": 0.13,
      "minutos_estimados": 14.9,
      "total": 172.5
    },
    {
      "id": 188,
      "pedido_id": 644,
      "folio": "PED-20261127-000644",
      "estado_pedido": "en_ruta",
      "orden_parada": 3,
      "direccion": "Valle Alto 1893, San Bernabé X (F-113)",
      "zona": "San Bernabé X (F-113)",
      "distancia_km": 1.21,
      "minutos_estimados": 22.0,
      "total": 131.0
    },
    {
      "id": 189,
      "pedido_id": 645,
      "folio": "PED-20261127-000645",
      "estado_pedido": "en_ruta",
      "orden_parada": 4,
      "direccion": "Emiliano Zapata 4706, Paseo de San Bernabé",
      "zona": "Paseo de San Bernabé",
      "distancia_km": 0.63,
      "minutos_estimados": 28.0,
      "total": 162.0
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 50,
    "total": 9,
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

**Petición.** `POST http://seguimiento:5110/api/v1/seguimiento/190/ubicaciones`

```http
Accept: application/json
X-Traza-Id: 0e57927b-946c-4a93-b1bd-396175f53a8a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "puntos": [
    {
      "latitud": 25.760195,
      "longitud": -100.370891,
      "capturado_en": "2026-11-27T17:38:36.856747+00:00"
    },
    {
      "latitud": 25.759995,
      "longitud": -100.371091,
      "capturado_en": "2026-11-27T17:41:36.856774+00:00"
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 43 ms · traza `0e57927b-946c-4a93-b1bd-396175f53a8a`

```json
{
  "recibidos": 2
}
```

## Servicio documentos · puerto 5107

### F1-16 · La foto de evidencia queda en el almacén · PASA

**Objetivo.** En la base solo sus datos; se descarga con un enlace firmado.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b09c10cbe459ba76063a609/enlace`

```http
Accept: application/json
X-Traza-Id: 4c8d3d7f-a866-401e-b5c3-81fea3be5346
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 173 ms · traza `4c8d3d7f-a866-401e-b5c3-81fea3be5346`

```json
{
  "id": "6b09c10cbe459ba76063a609",
  "nombre": "evidencia-flujo1-17BD1.jpg",
  "url_firmada": "https://storage.googleapis.com/microhubs-evidencias-637044/d…(1005 caracteres)",
  "metodo": "GET",
  "segundos": 300,
  "expira_en": "2026-11-27T11:47:37-06:00"
}
```

**Evidencia en MongoDB.** `db.documentos.findOne({_id}) sin contenido`

```json
{
  "_id": "6b09c10cbe459ba76063a609",
  "nombre": "evidencia-flujo1-17BD1.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "190"
  },
  "subido_por": 7,
  "creado_en": "2026-11-27 17:42:36.921000+00:00",
  "ruta": "documentos/2026/11/6b09c10cbe459ba76063a609.jpg",
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

**Petición.** `POST http://entregas:5105/api/v1/entregas/190/resultado`

```http
Accept: application/json
X-Traza-Id: a5a9c8ad-f85e-40fc-91cb-0f385aee4a89
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 342.0,
  "cambio_entregado": 0,
  "ubicacion": {
    "latitud": 25.759995,
    "longitud": -100.371091
  },
  "evidencia_ids": [
    "6b09c10cbe459ba76063a609"
  ],
  "capturado_en": "2026-11-27T17:42:37.416421+00:00",
  "id_cliente_local": "d0310593-e278-43cc-b1a9-b6194b2a1358"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 118 ms · traza `a5a9c8ad-f85e-40fc-91cb-0f385aee4a89`

```json
{
  "entrega_id": 190,
  "pedido_id": 651,
  "estado_pedido": "entregado",
  "cerrado_en": "2026-11-27T11:42:37-06:00",
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
    "usuario_id": 56,
    "proceso": null
  },
  {
    "estado_anterior": "en_preparacion",
    "estado_nuevo": "en_ruta",
    "usuario_id": 56,
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
X-Traza-Id: 6813f64c-5b3d-4963-86d0-6d74fd8b9714
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 52 ms · traza `6813f64c-5b3d-4963-86d0-6d74fd8b9714`

```json
{
  "datos": [
    {
      "id": 655,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000651",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "651"
      },
      "creada_en": "2026-11-27T11:42:37-06:00"
    },
    {
      "id": 637,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000635",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "635"
      },
      "creada_en": "2026-11-27T01:31:04-06:00"
    },
    {
      "id": 604,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000623",
      "mensaje": "El pedido cambió a entrega_fallida.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "623"
      },
      "creada_en": "2026-11-27T01:30:06-06:00"
    },
    {
      "id": 602,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000622",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "622"
      },
      "creada_en": "2026-11-27T01:30:04-06:00"
    },
    {
      "id": 597,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000621",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "621"
      },
      "creada_en": "2026-11-27T01:30:01-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 352,
    "paginas": 71
  }
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F1-19 · El auditor reconstruye la historia del pedido · PASA

**Objetivo.** Bitácora, estados, inventario y archivos en una línea de tiempo.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/pedido/651`

```http
Accept: application/json
X-Traza-Id: 8e4e95f4-317f-4f1a-b08c-3beabed1ff94
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 164 ms · traza `8e4e95f4-317f-4f1a-b08c-3beabed1ff94`

```json
{
  "objeto": {
    "tipo": "pedido",
    "id": "651"
  },
  "total": 15,
  "eventos": [
    {
      "fecha": "2026-11-27T11:42:36-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "actualizado_en = 2026-11-27T11:42:36.372291-06:00; asignado_en = None; cerrado_en = None; cliente_id = 1",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "651"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": null,
          "nuevo": "2026-11-27T11:42:36.372291-06:00"
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
          "nuevo": "2026-11-27T11:42:36.372291-06:00"
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
          "nuevo": "PED-20261127-000651"
        },
        {
          "campo": "id",
          "anterior": null,
          "nuevo": "651"
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
      "fecha": "2026-11-27T11:42:36-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "asignado_en = 2026-11-27T11:42:36.372291-06:00; estado: creado → asignado; microhub_id = 11",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "651"
      },
      "cambios": [
        {
          "campo": "asignado_en",
          "anterior": null,
          "nuevo": "2026-11-27T11:42:36.372291-06:00"
        },
        {
          "campo": "estado",
          "anterior": "creado",
          "nuevo": "asignado"
        },
        {
          "campo": "microhub_id",
          "anterior": null,
          "nuevo": "11"
        }
      ]
    },
    {
      "fecha": "2026-11-27T11:42:36-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "nuevo → creado",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "651"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T11:42:36-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "creado → asignado",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "651"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T11:42:36-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -3 de producto 36 en microhub 11 (existencia 9)",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "11-36"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T11:42:36-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -3 de producto 51 en microhub 11 (existencia 9)",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "11-51"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T11:42:36-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-27T11:42:36.372291-06:00 → 2026-11-27T11:42:36.511495-06:00; estado: asignado → en_preparacion",
      "usuario": {
        "id": 56,
        "nombre": "Operador 17BD1"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "651"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-27T11:42:36.372291-06:00",
          "nuevo": "2026-11-27T11:42:36.511495-06:00"
        },
        {
          "campo": "estado",
          "anterior": "asignado",
          "nuevo": "en_preparacion"
        }
      ]
    },
    {
      "fecha": "2026-11-27T11:42:36-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "asignado → en_preparacion",
      "usuario": {
        "id": 56,
        "nombre": "Operador 17BD1"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "651"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T11:42:36-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "listo_en = 2026-11-27T11:42:36.577938-06:00",
      "usuario": {
        "id": 56,
        "nombre": "Operador 17BD1"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "651"
      },
      "cambios": [
        {
          "campo": "listo_en",
          "anterior": null,
          "nuevo": "2026-11-27T11:42:36.577938-06:00"
        }
      ]
    },
    {
      "fecha": "2026-11-27T11:42:36-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "asignada_en = 2026-11-27T11:42:36.768445-06:00; cambio_entregado = None; capturado_en = None; cerrada_por_usuario_id = None",
      "usuario": {
        "id": 56,
        "nombre": "Operador 17BD1"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "190"
      },
      "cambios": [
        {
          "campo": "asignada_en",
          "anterior": null,
          "nuevo": "2026-11-27T11:42:36.768445-06:00"
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
      "fecha": "2026-11-27T11:42:36-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-27T11:42:36.511495-06:00 → 2026-11-27T11:42:36.768445-06:00; estado: en_preparacion → en_ruta",
      "usuario": {
        "id": 56,
        "nombre": "Operador 17BD1"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "651"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-27T11:42:36.511495-06:00",
          "nuevo": "2026-11-27T11:42:36.768445-06:00"
        },
        {
          "campo": "estado",
          "anterior": "en_preparacion",
          "nuevo": "en_ruta"
        }
      ]
    },
    {
      "fecha": "2026-11-27T11:42:36-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "en_preparacion → en_ruta",
      "usuario": {
        "id": 56,
        "nombre": "Operador 17BD1"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "651"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T11:42:37-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "cambio_entregado = 0.0; capturado_en = 2026-11-27T11:42:37.4…(145 caracteres)",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "190"
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
          "nuevo": "2026-11-27T11:42:37.416421-06:00"
        },
        {
          "campo": "cerrada_por_usuario_id",
          "anterior": null,
          "nuevo": "7"
        },
        {
          "campo": "cierre_en",
          "anterior": null,
          "nuevo": "2026-11-27T11:42:37.468811-06:00"
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
          "nuevo": "[\"6b09c10cbe459ba76063a609\"]"
        },
        {
          "campo": "evidencia_url",
          "anterior": null,
          "nuevo": "/api/v1/documentos/6b09c10cbe459ba76063a609"
        },
        {
          "campo": "id_cliente_local",
          "anterior": null,
          "nuevo": "d0310593-e278-43cc-b1a9-b6194b2a1358"
        },
        {
          "campo": "monto_cobrado",
          "anterior": null,
          "nuevo": "342.0"
        },
        {
          "campo": "resultado",
          "anterior": null,
          "nuevo": "entregado"
        }
      ]
    },
    {
      "fecha": "2026-11-27T11:42:37-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-27T11:42:36.768445-06:00 → 2026-11-2…(159 caracteres)",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "651"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-27T11:42:36.768445-06:00",
          "nuevo": "2026-11-27T11:42:37.468811-06:00"
        },
        {
          "campo": "cerrado_en",
          "anterior": null,
          "nuevo": "2026-11-27T11:42:37.468811-06:00"
        },
        {
          "campo": "estado",
          "anterior": "en_ruta",
          "nuevo": "entregado"
        }
      ]
    },
    {
      "fecha": "2026-11-27T11:42:37-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "en_ruta → entregado",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "651"
      },
      "cambios": []
    }
  ]
}
```

## Servicio reportes · puerto 5123

### F1-20 · Visualización: el microhub nuevo ya aparece en la comparación · PASA

**Objetivo.** Datos listos para Highcharts.

**Petición.** `GET http://reportes:5123/api/v1/reportes/comparacion_microhubs/grafica?microhub_id=11`

```http
Accept: application/json
X-Traza-Id: 072bd1e6-cd55-4bb3-827e-90da3ca692ee
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 91 ms · traza `072bd1e6-cd55-4bb3-827e-90da3ca692ee`

```json
{
  "reporte": "comparacion_microhubs",
  "titulo": "Comparación entre microhubs",
  "tipo": "column",
  "unidad": "pedidos / MXN",
  "categorias": [
    "Microhub 17BD1"
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
        342.0
      ]
    }
  ]
}
```

## Servicio microhubs · puerto 5109

### F1-21 · Cierre: dar de baja el microhub de la demostración · PASA

**Objetivo.** Baja lógica; conserva su historia.

**Petición.** `DELETE http://microhubs:5109/api/v1/microhubs/11`

```http
Accept: application/json
X-Traza-Id: db9db829-abbf-46f3-9401-c36b3af47d21
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 33 ms · traza `db9db829-abbf-46f3-9401-c36b3af47d21`

```json
(sin cuerpo)
```

## Servicio pedidos · puerto 5104

### F2-01 · Android: un cliente compra y el inventario baja · PASA

**Objetivo.** El motor descuenta inventario en la misma transacción.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: a3bddf67-1d5c-434c-af4e-287b1ba139e2
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
  "operacion_uuid": "89dc11cd-3d12-4722-8f45-67fa297810b3"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 157 ms · traza `a3bddf67-1d5c-434c-af4e-287b1ba139e2`

```json
{
  "id": 652,
  "folio": "PED-20261127-000652",
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
    "existencia_resultante": 56
  }
]
```

## Servicio inventario · puerto 5111

### F2-02 · El operador fija el mínimo y nace la alerta · PASA

**Objetivo.** El trigger avisa del faltante.

**Petición.** `PATCH http://inventario:5111/api/v1/inventario/1/51/minimo`

```http
Accept: application/json
X-Traza-Id: b4eeeb3a-9555-4e58-98f3-bafe19f68699
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "minimo": 303
}
```

**Respuesta.** HTTP 200 (esperado 200) · 187 ms · traza `b4eeeb3a-9555-4e58-98f3-bafe19f68699`

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
  "existencia": 293,
  "minimo": 303,
  "reservado": 0,
  "disponible": 293,
  "estado": "bajo_minimo",
  "actualizado_en": "2026-11-27T11:42:38-06:00"
}
```

### F2-03 · La alerta de faltante · PASA

**Objetivo.** Qué producto, cuánto falta y qué tan grave es.

**Petición.** `GET http://inventario:5111/api/v1/inventario/alertas?microhub_id=1&por_pagina=100`

```http
Accept: application/json
X-Traza-Id: b17a92ea-de7c-4489-845a-debcafedcd93
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 83 ms · traza `b17a92ea-de7c-4489-845a-debcafedcd93`

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
      "existencia": 293,
      "minimo": 303,
      "disponible": 293,
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
X-Traza-Id: 143c5434-37c5-439b-a149-f9659d70d56f
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

**Respuesta.** HTTP 201 (esperado 201) · 68 ms · traza `143c5434-37c5-439b-a149-f9659d70d56f`

```json
{
  "id": 27,
  "folio": "SC-20261127-000027",
  "microhub_id": 1,
  "estado": "pendiente",
  "motivo": "Faltante detectado por el sistema",
  "solicitada_por": 2,
  "decidida_por": null,
  "decision_motivo": null,
  "decidida_en": null,
  "creada_en": "2026-11-27T11:42:39-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/27/decision`

```http
Accept: application/json
X-Traza-Id: 6ffa9aa8-8c59-4fe9-8582-c53d42c9076f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aprobada",
  "motivo": "Con presupuesto"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 77 ms · traza `6ffa9aa8-8c59-4fe9-8582-c53d42c9076f`

```json
{
  "id": 27,
  "folio": "SC-20261127-000027",
  "microhub_id": 1,
  "estado": "aprobada",
  "motivo": "Faltante detectado por el sistema",
  "solicitada_por": 2,
  "decidida_por": 1,
  "decision_motivo": "Con presupuesto",
  "decidida_en": "2026-11-27T11:42:39-06:00",
  "creada_en": "2026-11-27T11:42:39-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/27/ordenar`

```http
Accept: application/json
X-Traza-Id: 12b18531-0270-4f6a-a68f-a9a7ed8221a6
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 201 (esperado 201) · 234 ms · traza `12b18531-0270-4f6a-a68f-a9a7ed8221a6`

```json
{
  "solicitud_id": 27,
  "ordenes": [
    {
      "id": 23,
      "folio": "OC-20261127-000023",
      "solicitud_id": 27,
      "proveedor": {
        "id": 3,
        "nombre": "Mayorista San Nicolás"
      },
      "microhub_id": 1,
      "estado": "emitida",
      "fecha_esperada": "2026-12-01",
      "total": 4624.0,
      "creada_en": "2026-11-27T11:42:39-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/23/recepcion`

```http
Accept: application/json
X-Traza-Id: 29135d86-fbec-46aa-9d64-5540f13027d0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "operacion_uuid": "f1d38282-8a4a-43e5-9b3d-5b9c857b4978",
  "nota": "Completo",
  "lineas": [
    {
      "producto_id": 51,
      "cantidad": 100
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 221 ms · traza `29135d86-fbec-46aa-9d64-5540f13027d0`

```json
{
  "orden": {
    "id": 23,
    "folio": "OC-20261127-000023",
    "solicitud_id": 27,
    "proveedor": {
      "id": 3,
      "nombre": "Mayorista San Nicolás"
    },
    "microhub_id": 1,
    "estado": "recibida",
    "fecha_esperada": "2026-12-01",
    "total": 4624.0,
    "creada_en": "2026-11-27T11:42:39-06:00",
    "cerrada_en": "2026-11-27T11:42:39-06:00",
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
    "existencia": 393,
    "minimo": 303
  }
]
```

## Servicio documentos · puerto 5107

### F2-08 · La remisión firmada queda en el almacén · PASA

**Objetivo.** Archivo con enlace firmado.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b09c10fbe459ba76063a60e/enlace`

```http
Accept: application/json
X-Traza-Id: e45f4a46-eab9-4dff-be87-cc8655cc0c75
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 138 ms · traza `e45f4a46-eab9-4dff-be87-cc8655cc0c75`

```json
{
  "id": "6b09c10fbe459ba76063a60e",
  "nombre": "remision-23.jpg",
  "url_firmada": "https://storage.googleapis.com/microhubs-evidencias-637044/d…(994 caracteres)",
  "metodo": "GET",
  "segundos": 300,
  "expira_en": "2026-11-27T11:47:39-06:00"
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F2-09 · Trazabilidad del producto en el microhub · PASA

**Objetivo.** Salida por pedido y recepción por orden.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/inventario?microhub_id=1&producto_id=51`

```http
Accept: application/json
X-Traza-Id: 9ef45d62-9bcc-4ff7-9f3d-dfca1499019c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 42 ms · traza `9ef45d62-9bcc-4ff7-9f3d-dfca1499019c`

```json
{
  "objeto": {
    "tipo": "inventario",
    "id": "1-51"
  },
  "total": 15,
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
X-Traza-Id: fffd76b6-1eed-4ac1-b706-62396e31c7c0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 169 ms · traza `fffd76b6-1eed-4ac1-b706-62396e31c7c0`

```json
﻿Microhub,Producto,Existencia,Mínimo,Disponible,Faltante,Severidad

```

## Servicio pedidos · puerto 5104

### F3-01 · El cliente hace un pedido · PASA

**Objetivo.** Punto de partida del recorrido.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: afd81563-8583-47be-8fa5-b01785e8b730
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

**Respuesta.** HTTP 201 (esperado 201) · 141 ms · traza `afd81563-8583-47be-8fa5-b01785e8b730`

```json
{
  "id": 653,
  "folio": "PED-20261127-000653",
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
X-Traza-Id: c79a566a-fb6a-4774-9b8d-74dda0eefcbb
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
Content-Type: application/json
```

```json
{
  "pedido_id": 653,
  "repartidor_id": 7
}
```

**Respuesta.** HTTP 201 (esperado 201) · 39 ms · traza `c79a566a-fb6a-4774-9b8d-74dda0eefcbb`

```json
{
  "entrega_id": 191,
  "pedido_id": 653,
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
X-Traza-Id: bc038c28-2233-4fec-ac23-ef7acb6d344a
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "f371565a-62e3-4e98-986a-fbb0b24372e7",
  "dispositivo": "android-flujo-eeca70",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "47a9b0f8-ac83-4368-8547-6f2d9734b529",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-27T17:22:41.738193+00:00",
      "datos": {
        "entrega_id": 191,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-27T17:22:41.738212+00:00"
          },
          {
            "latitud": 25.7491,
            "longitud": -100.3611,
            "capturado_en": "2026-11-27T17:27:41.738220+00:00"
          }
        ]
      }
    },
    {
      "operacion_uuid": "504fbd75-7659-40ec-ae88-cef7897e5f65",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-27T17:30:41.738238+00:00",
      "datos": {
        "entrega_id": 191,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "El cliente no estaba en su domicilio",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b09c111dfa34c1cb3dadbf5"
        ],
        "capturado_en": "2026-11-27T17:30:41.738242+00:00"
      }
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 270 ms · traza `bc038c28-2233-4fec-ac23-ef7acb6d344a`

```json
{
  "id": 18,
  "lote_uuid": "f371565a-62e3-4e98-986a-fbb0b24372e7",
  "dispositivo": "android-flujo-eeca70",
  "recibido_en": "2026-11-27T11:42:41-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 0,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "47a9b0f8-ac83-4368-8547-6f2d9734b529",
      "tipo": "ubicaciones",
      "estado": "aplicada",
      "duplicada": false,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    },
    {
      "operacion_uuid": "504fbd75-7659-40ec-ae88-cef7897e5f65",
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
    "creada_en": "2026-11-27 11:22:41.738193-06:00"
  },
  {
    "tipo": "entrega_resultado",
    "estado": "aplicada",
    "intentos": 1,
    "creada_en": "2026-11-27 11:30:41.738238-06:00"
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
X-Traza-Id: d74a5f20-6966-45ac-9557-e9e1a2f174ca
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "f371565a-62e3-4e98-986a-fbb0b24372e7",
  "dispositivo": "android-flujo-eeca70",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "47a9b0f8-ac83-4368-8547-6f2d9734b529",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-27T17:22:41.738193+00:00",
      "datos": {
        "entrega_id": 191,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-27T17:22:41.738212+00:00"
          },
          {
            "latitud": 25.7491,
            "longitud": -100.3611,
            "capturado_en": "2026-11-27T17:27:41.738220+00:00"
          }
        ]
      }
    },
    {
      "operacion_uuid": "504fbd75-7659-40ec-ae88-cef7897e5f65",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-27T17:30:41.738238+00:00",
      "datos": {
        "entrega_id": 191,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "El cliente no estaba en su domicilio",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b09c111dfa34c1cb3dadbf5"
        ],
        "capturado_en": "2026-11-27T17:30:41.738242+00:00"
      }
    }
  ]
}
```

**Respuesta.** HTTP 200 (esperado 200) · 110 ms · traza `d74a5f20-6966-45ac-9557-e9e1a2f174ca`

```json
{
  "id": 18,
  "lote_uuid": "f371565a-62e3-4e98-986a-fbb0b24372e7",
  "dispositivo": "android-flujo-eeca70",
  "recibido_en": "2026-11-27T11:42:41-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 2,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "47a9b0f8-ac83-4368-8547-6f2d9734b529",
      "tipo": "ubicaciones",
      "estado": "aplicada",
      "duplicada": true,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    },
    {
      "operacion_uuid": "504fbd75-7659-40ec-ae88-cef7897e5f65",
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
X-Traza-Id: e2912798-4958-46a4-aec2-4ce2b11a648d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 33 ms · traza `e2912798-4958-46a4-aec2-4ce2b11a648d`

```json
{
  "datos": [
    {
      "id": 662,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000653",
      "mensaje": "El pedido cambió a entrega_fallida.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "653"
      },
      "creada_en": "2026-11-27T11:42:41-06:00"
    },
    {
      "id": 660,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000652",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "652"
      },
      "creada_en": "2026-11-27T11:42:40-06:00"
    },
    {
      "id": 655,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000651",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "651"
      },
      "creada_en": "2026-11-27T11:42:37-06:00"
    },
    {
      "id": 637,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000635",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "635"
      },
      "creada_en": "2026-11-27T01:31:04-06:00"
    },
    {
      "id": 604,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261127-000623",
      "mensaje": "El pedido cambió a entrega_fallida.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "623"
      },
      "creada_en": "2026-11-27T01:30:06-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 354,
    "paginas": 71
  }
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F3-06 · El auditor revisa la entrega · PASA

**Objetivo.** Bitácora y archivos de la entrega.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/entrega/191`

```http
Accept: application/json
X-Traza-Id: bb20528c-051c-4174-b206-c04d40fccd8c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 38 ms · traza `bb20528c-051c-4174-b206-c04d40fccd8c`

```json
{
  "objeto": {
    "tipo": "entrega",
    "id": "191"
  },
  "total": 3,
  "eventos": [
    {
      "fecha": "2026-11-27T11:42:41-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "asignada_en = 2026-11-27T11:42:41.613735-06:00; cambio_entregado = None; capturado_en = None; cerrada_por_usuario_id = None",
      "usuario": {
        "id": 3,
        "nombre": "María José Cedillo Mata"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "191"
      },
      "cambios": [
        {
          "campo": "asignada_en",
          "anterior": null,
          "nuevo": "2026-11-27T11:42:41.613735-06:00"
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
      "fecha": "2026-11-27T11:42:41-06:00",
      "origen": "documentos",
      "accion": "documento_subido",
      "descripcion": "evidencia-flujo3-191.jpg (276 bytes, sha256 7f6025cd8a98…)",
      "usuario": {
        "id": 7,
        "nombre": null
      },
      "entidad": {
        "tipo": "documento",
        "id": "6b09c111dfa34c1cb3dadbf5"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T11:42:41-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "cambio_entregado = 0.0; capturado_en = 2026-11-27T11:30:41.7…(145 caracteres)",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "191"
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
          "nuevo": "2026-11-27T11:30:41.738242-06:00"
        },
        {
          "campo": "cerrada_por_usuario_id",
          "anterior": null,
          "nuevo": "7"
        },
        {
          "campo": "cierre_en",
          "anterior": null,
          "nuevo": "2026-11-27T11:42:41.908498-06:00"
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
          "nuevo": "[\"6b09c111dfa34c1cb3dadbf5\"]"
        },
        {
          "campo": "evidencia_url",
          "anterior": null,
          "nuevo": "/api/v1/documentos/6b09c111dfa34c1cb3dadbf5"
        },
        {
          "campo": "id_cliente_local",
          "anterior": null,
          "nuevo": "504fbd75-7659-40ec-ae88-cef7897e5f65"
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
X-Traza-Id: d051ebaa-5ec1-49a8-81e1-8dcbe8e8fcba
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 39 ms · traza `d051ebaa-5ec1-49a8-81e1-8dcbe8e8fcba`

```json
{
  "datos": [
    {
      "id": 2771,
      "microhub_id": 2,
      "producto_id": 51,
      "tipo": "devolucion_cancelacion",
      "cantidad": 3,
      "existencia_resultante": 66,
      "referencia": {
        "tipo": "pedido",
        "id": "653"
      },
      "motivo": "Entrega fallida: la mercancía regresa al microhub.",
      "usuario_id": 7,
      "fecha": "2026-11-27T11:42:41-06:00"
    },
    {
      "id": 2770,
      "microhub_id": 2,
      "producto_id": 31,
      "tipo": "devolucion_cancelacion",
      "cantidad": 3,
      "existencia_resultante": 73,
      "referencia": {
        "tipo": "pedido",
        "id": "653"
      },
      "motivo": "Entrega fallida: la mercancía regresa al microhub.",
      "usuario_id": 7,
      "fecha": "2026-11-27T11:42:41-06:00"
    },
    {
      "id": 2769,
      "microhub_id": 2,
      "producto_id": 51,
      "tipo": "salida_pedido",
      "cantidad": -3,
      "existencia_resultante": 63,
      "referencia": {
        "tipo": "pedido",
        "id": "653"
      },
      "motivo": null,
      "usuario_id": 9,
      "fecha": "2026-11-27T11:42:41-06:00"
    },
    {
      "id": 2768,
      "microhub_id": 2,
      "producto_id": 31,
      "tipo": "salida_pedido",
      "cantidad": -3,
      "existencia_resultante": 70,
      "referencia": {
        "tipo": "pedido",
        "id": "653"
      },
      "motivo": null,
      "usuario_id": 9,
      "fecha": "2026-11-27T11:42:41-06:00"
    },
    {
      "id": 2767,
      "microhub_id": 2,
      "producto_id": 51,
      "tipo": "devolucion_cancelacion",
      "cantidad": 10,
      "existencia_resultante": 66,
      "referencia": {
        "tipo": "pedido",
        "id": "652"
      },
      "motivo": "Cierre del flujo de demostración",
      "usuario_id": 1,
      "fecha": "2026-11-27T11:42:40-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 1847,
    "paginas": 370
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
    "existencia_resultante": 70
  },
  {
    "tipo": "salida_pedido",
    "producto_id": 51,
    "cantidad": -3,
    "existencia_resultante": 63
  },
  {
    "tipo": "devolucion_cancelacion",
    "producto_id": 31,
    "cantidad": 3,
    "existencia_resultante": 73
  },
  {
    "tipo": "devolucion_cancelacion",
    "producto_id": 51,
    "cantidad": 3,
    "existencia_resultante": 66
  }
]
```

## Servicio reportes · puerto 5123

### F3-08 · Reporte del periodo en CSV · PASA

**Objetivo.** La entrega ya cuenta en los reportes.

**Petición.** `GET http://reportes:5123/api/v1/reportes/pedidos_por_dia/exportar?formato=csv`

```http
Accept: application/json
X-Traza-Id: 380628d4-e9b5-4f20-a573-fd906bf2f642
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 172 ms · traza `380628d4-e9b5-4f20-a573-fd906bf2f642`

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
2026-11-27,24,126,5084.50,211.85,1
Total,185,963,36123.60,195.26,36

```

**Evidencia en PostgreSQL.** `SELECT reporte, formato, filas, left(sha256, 16) AS sha256 FROM reporte_exportacion ORDER BY id DESC LIMIT 1`

```json
[
  {
    "reporte": "pedidos_por_dia",
    "formato": "csv",
    "filas": 29,
    "sha256": "92c14af5bb1588d1"
  }
]
```
