# Procesos integrales de principio a fin


Generado el 2026-11-27 07:30 contra los servicios en ejecución. 40 de 40 casos pasan.

## Servicio planeacion · puerto 5106

### F1-01 · Escritorio (XML): el planeador registra una ubicación candidata · PASA

**Objetivo.** Planeación de ubicación.

**Petición.** `POST http://planeacion:5106/api/v1/candidatos`

```http
Accept: application/xml
X-Traza-Id: d8329cb1-dc8d-4079-a15f-3d4cfca1d520
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?><candidato_nuevo xmlns="urn:microhubs:v1"><clave>********</clave><nombre>Ubicación del flujo 9CB6E</nombre><latitud>25.760195</latitud><longitud>-100.370891</longitud><renta_estimada>15000.00</renta_estimada><nomina_estimada>36000.00</nomina_estimada><servicios_estimados>6000.00</servicios_estimados><otros_costos>4000.00</otros_costos><superficie_m2>100</superficie_m2><capacidad_fisica>120</capacidad_fisica><accesibilidad_vial>8</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km></candidato_nuevo>
```

**Respuesta.** HTTP 201 (esperado 201) · 72 ms · traza `d8329cb1-dc8d-4079-a15f-3d4cfca1d520`

```xml
<?xml version='1.0' encoding='utf-8'?>
<candidato xmlns="urn:microhubs:v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1"><id>177</id><clave>FL-9CB6E</clave><nombre>Ubicación del flujo 9CB6E</nombre><latitud>25.760195</latitud><longitud>-100.370891</longitud><renta_estimada>15000.00</renta_estimada><nomina_estimada>36000.00</nomina_estimada><servicios_estimados>6000.00</servicios_estimados><otros_costos>4000.00</otros_costos><costo_fijo>61000.00</costo_fijo><superficie_m2>100</superficie_m2><capacidad_fisica>120</capacidad_fisica><accesibilidad_vial>8</accesibilidad_vial><zona_id>3</zona_id><poblacion_cubierta>5200</poblacion_cubierta><radio_km>1.5</radio_km><decision>pendiente</decision><decision_motivo xsi:nil="true" /></candidato>
```

**Evidencia en PostgreSQL.** `SELECT id, clave, nombre, costo_fijo, decision FROM ubicacion_candidata WHERE clave = %s`

```json
[
  {
    "id": 177,
    "clave": "FL-9CB6E",
    "nombre": "Ubicación del flujo 9CB6E",
    "costo_fijo": "61000.00",
    "decision": "pendiente"
  }
]
```

### F1-02 · El planeador simula la operación de la candidata · PASA

**Objetivo.** Capacidad, utilización y decisión sugerida (MongoDB).

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/177/simular`

```http
Accept: application/json
X-Traza-Id: 32473813-03a4-4112-aaa0-2bd559b3118f
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

**Respuesta.** HTTP 200 (esperado 200) · 202 ms · traza `32473813-03a4-4112-aaa0-2bd559b3118f`

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
X-Traza-Id: 7cc428ca-8aa1-4f60-99dc-ea82b325ed81
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "candidato_id": 177,
  "pedidos_dia": 100,
  "ticket": 180,
  "margen_bruto": 0.3,
  "costos_fijos": 61000,
  "costo_variable_pedido": 22
}
```

**Respuesta.** HTTP 200 (esperado 200) · 23 ms · traza `7cc428ca-8aa1-4f60-99dc-ea82b325ed81`

```json
{
  "id": null,
  "nombre": null,
  "objeto": {
    "tipo": "candidato",
    "id": 177,
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

**Petición.** `POST http://planeacion:5106/api/v1/candidatos/177/decision`

```http
Accept: application/json
X-Traza-Id: c27248d9-051e-442c-a6e3-7739fb6468ad
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aceptado",
  "motivo": "Cubre la zona del cliente y la demanda esperada supera el equilibrio."
}
```

**Respuesta.** HTTP 200 (esperado 200) · 42 ms · traza `c27248d9-051e-442c-a6e3-7739fb6468ad`

```json
{
  "id": 177,
  "clave": "********",
  "nombre": "Ubicación del flujo 9CB6E",
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
X-Traza-Id: 97741de0-cec2-4506-883d-67703e196b73
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "clave": "********",
  "nombre": "Microhub 9CB6E",
  "direccion": "Ubicación aprobada en planeación",
  "latitud": 25.760195,
  "longitud": -100.370891,
  "radio_km": 1.5,
  "capacidad_turno": 120
}
```

**Respuesta.** HTTP 201 (esperado 201) · 44 ms · traza `97741de0-cec2-4506-883d-67703e196b73`

```json
{
  "id": 9,
  "clave": "********",
  "nombre": "Microhub 9CB6E",
  "latitud": 25.760195,
  "longitud": -100.370891,
  "radio_km": 1.5,
  "estatus": "activo"
}
```

## Servicio capacidad · puerto 5117

### F1-06 · Asignar personal al microhub · PASA

**Objetivo.** Operadores, repartidores y capacidad física.

**Petición.** `PUT http://capacidad:5117/api/v1/capacidad/recursos/9`

```http
Accept: application/json
X-Traza-Id: 1691d35a-b338-4cb2-9120-e13aaa0d9585
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

**Respuesta.** HTTP 200 (esperado 200) · 127 ms · traza `1691d35a-b338-4cb2-9120-e13aaa0d9585`

```json
{
  "microhub": {
    "id": 9,
    "nombre": "Microhub 9CB6E"
  },
  "operadores": 2,
  "repartidores": 2,
  "capacidad_fisica": 120,
  "actualizado_en": "2026-11-27T01:30:00-06:00"
}
```

## Servicio usuarios · puerto 5102

### F1-07 · Crear la cuenta del operador · PASA

**Objetivo.** Cuenta nueva con su perfil y su microhub.

**Petición.** `POST http://usuarios:5102/api/v1/usuarios`

```http
Accept: application/json
X-Traza-Id: d4ce3e68-81a6-43ea-b7e0-24f10e6a6269
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "nombre": "Operador",
  "apellidos": "9CB6E",
  "correo": "operador.9cb6e@ejemplo.mx",
  "clave": "********",
  "rol": "operador",
  "microhub_id": 9
}
```

**Respuesta.** HTTP 201 (esperado 201) · 123 ms · traza `d4ce3e68-81a6-43ea-b7e0-24f10e6a6269`

```json
{
  "id": 53,
  "nombre": "Operador",
  "apellidos": "9CB6E",
  "correo": "operador.9cb6e@ejemplo.mx",
  "telefono": null,
  "rol": "operador",
  "microhub": {
    "id": 9,
    "clave": "********",
    "nombre": "Microhub 9CB6E"
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
X-Traza-Id: 351ea605-792c-45d8-8841-0d39439d8297
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "origen_microhub_id": 1,
  "destino_microhub_id": 9,
  "producto_id": 51,
  "cantidad": 12,
  "motivo": "Inventario inicial del microhub nuevo",
  "operacion_uuid": "939efab6-bdd7-44c2-a848-01b3ce87ea0b"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 77 ms · traza `351ea605-792c-45d8-8841-0d39439d8297`

```json
{
  "producto_id": 51,
  "cantidad": 12,
  "duplicado": false,
  "origen": {
    "microhub_id": 1,
    "existencia": 205,
    "movimiento_id": 2658
  },
  "destino": {
    "microhub_id": 9,
    "existencia": 12,
    "movimiento_id": 2659
  }
}
```

### F1-08b · Surtir el microhub nuevo · PASA

**Objetivo.** Transferencia atómica desde MH-01.

**Petición.** `POST http://inventario:5111/api/v1/inventario/transferencias`

```http
Accept: application/json
X-Traza-Id: 5391c3b8-67fb-41fe-83db-b2896d650e6d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "origen_microhub_id": 1,
  "destino_microhub_id": 9,
  "producto_id": 47,
  "cantidad": 12,
  "motivo": "Inventario inicial del microhub nuevo",
  "operacion_uuid": "ec222731-2029-4ef2-9b82-36ed1d8f7517"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 57 ms · traza `5391c3b8-67fb-41fe-83db-b2896d650e6d`

```json
{
  "producto_id": 47,
  "cantidad": 12,
  "duplicado": false,
  "origen": {
    "microhub_id": 1,
    "existencia": 38,
    "movimiento_id": 2660
  },
  "destino": {
    "microhub_id": 9,
    "existencia": 12,
    "movimiento_id": 2661
  }
}
```

## Servicio pedidos · puerto 5104

### F1-09 · Android (JSON): el cliente hace su pedido · PASA

**Objetivo.** El motor lo asigna al microhub más cercano que tiene todo: el nuevo.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: 360af542-cbdc-4cdc-a4b8-cc53cd637943
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
      "producto_id": 47,
      "cantidad": 3
    }
  ],
  "operacion_uuid": "e888d2b4-785c-49c1-b98c-916a723dfc15"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 182 ms · traza `360af542-cbdc-4cdc-a4b8-cc53cd637943`

```json
{
  "id": 621,
  "folio": "PED-20261127-000621",
  "estado": "asignado",
  "zona_id": 3,
  "microhub_id": 9,
  "subtotal": 366.0,
  "costo_envio": 0.0,
  "total": 366.0,
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
    "microhub_ganador_id": 9,
    "motivo": null
  }
]
```

**Evidencia en PostgreSQL.** `SELECT tipo, producto_id, cantidad, existencia_resultante FROM movimiento_inventario WHERE referencia_tipo = 'pedido' AND referencia_id = %s`

```json
[
  {
    "tipo": "salida_pedido",
    "producto_id": 47,
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

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/621/estado`

```http
Accept: application/json
X-Traza-Id: 2682712c-4d9f-45bd-bb99-f30fb5223b58
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1MyIs…(295 caracteres)
Content-Type: application/json
```

```json
{
  "estado": "en_preparacion"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 61 ms · traza `2682712c-4d9f-45bd-bb99-f30fb5223b58`

```json
{
  "id": 621,
  "folio": "PED-20261127-000621",
  "estado": "en_preparacion",
  "zona": {
    "id": 3,
    "nombre": "Paseo de San Bernabé"
  },
  "microhub_id": 9,
  "total": 366.0,
  "creado_en": "2026-11-27T01:30:00-06:00"
}
```

### F1-11 · El operador lo marca listo · PASA

**Objetivo.** Queda disponible para despacho.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos/621/listo`

```http
Accept: application/json
X-Traza-Id: 8042bcd2-1e23-4df1-865c-fd6c5e5da2e1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1MyIs…(295 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 200 (esperado 200) · 40 ms · traza `8042bcd2-1e23-4df1-865c-fd6c5e5da2e1`

```json
{
  "id": 621,
  "estado": "en_preparacion",
  "listo_en": "2026-11-27T01:30:01-06:00"
}
```

## Servicio rutas · puerto 5118

### F1-12 · Proponer la ruta de despacho · PASA

**Objetivo.** Agrupa, asigna repartidor y ordena las paradas (algoritmo de rutas).

**Petición.** `POST http://rutas:5118/api/v1/rutas/planes`

```http
Accept: application/json
X-Traza-Id: 775fcdee-5841-4480-9bb5-d57a4f586b55
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1MyIs…(295 caracteres)
Content-Type: application/json
```

```json
{
  "microhub_id": 9,
  "pedido_ids": [
    621
  ],
  "repartidor_ids": [
    7
  ],
  "metodo": "automatico",
  "guardar": true
}
```

**Respuesta.** HTTP 201 (esperado 201) · 137 ms · traza `775fcdee-5841-4480-9bb5-d57a4f586b55`

```json
{
  "id": 22,
  "estado": "propuesto",
  "version": 1,
  "microhub": {
    "id": 9,
    "nombre": "Microhub 9CB6E"
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
            "id": 621,
            "folio": "PED-20261127-000621"
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
X-Traza-Id: ea6d609f-9695-4fc3-8902-a137d650ba6e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1MyIs…(295 caracteres)
Content-Type: application/json
```

```json
{
  "pedido_id": 621,
  "repartidor_id": 7,
  "orden_parada": 1
}
```

**Respuesta.** HTTP 201 (esperado 201) · 44 ms · traza `ea6d609f-9695-4fc3-8902-a137d650ba6e`

```json
{
  "entrega_id": 170,
  "pedido_id": 621,
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
    "referencia_id": "170"
  }
]
```

### F1-14 · Android: el repartidor ve su parada · PASA

**Objetivo.** Sesión validada en Redis.

**Petición.** `GET http://entregas:5105/api/v1/entregas/mias?por_pagina=50`

```http
Accept: application/json
X-Traza-Id: 520988dc-9dba-4995-b61e-5c8e23e4e6e5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 38 ms · traza `520988dc-9dba-4995-b61e-5c8e23e4e6e5`

```json
{
  "datos": [
    {
      "id": 170,
      "pedido_id": 621,
      "folio": "PED-20261127-000621",
      "estado_pedido": "en_ruta",
      "orden_parada": 1,
      "direccion": "Nogal 1440, Paseo de San Bernabé",
      "zona": "Paseo de San Bernabé",
      "distancia_km": null,
      "minutos_estimados": null,
      "total": 366.0
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
    "valor": 1
  }
]
```

## Servicio seguimiento · puerto 5110

### F1-15 · El repartidor envía su recorrido · PASA

**Objetivo.** Puntos GPS en MongoDB (2dsphere).

**Petición.** `POST http://seguimiento:5110/api/v1/seguimiento/170/ubicaciones`

```http
Accept: application/json
X-Traza-Id: decbcd5c-ed21-41fc-b800-16d20e707987
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "puntos": [
    {
      "latitud": 25.760195,
      "longitud": -100.370891,
      "capturado_en": "2026-11-27T07:26:01.410206+00:00"
    },
    {
      "latitud": 25.759995,
      "longitud": -100.371091,
      "capturado_en": "2026-11-27T07:29:01.410227+00:00"
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 39 ms · traza `decbcd5c-ed21-41fc-b800-16d20e707987`

```json
{
  "recibidos": 2
}
```

## Servicio documentos · puerto 5107

### F1-16 · La foto de evidencia queda en el almacén · PASA

**Objetivo.** En la base solo sus datos; se descarga con un enlace firmado.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b093179d92909927b4fc98d/enlace`

```http
Accept: application/json
X-Traza-Id: eb02a636-61b3-47e3-808b-d929f7d20238
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 119 ms · traza `eb02a636-61b3-47e3-808b-d929f7d20238`

```json
{
  "id": "6b093179d92909927b4fc98d",
  "nombre": "evidencia-flujo1-9CB6E.jpg",
  "url_firmada": "https://storage.googleapis.com/microhubs-evidencias-637044/d…(1005 caracteres)",
  "metodo": "GET",
  "segundos": 300,
  "expira_en": "2026-11-27T01:35:01-06:00"
}
```

**Evidencia en MongoDB.** `db.documentos.findOne({_id}) sin contenido`

```json
{
  "_id": "6b093179d92909927b4fc98d",
  "nombre": "evidencia-flujo1-9CB6E.jpg",
  "tipo_mime": "image/jpeg",
  "tamano_bytes": 276,
  "sha256": "7f6025cd8a98db24ba552ff186d6bc3a48fde11ea90962d085b2426c327299dc",
  "referencia": {
    "tipo": "entrega",
    "id": "170"
  },
  "subido_por": 7,
  "creado_en": "2026-11-27 07:30:01.467000+00:00",
  "ruta": "documentos/2026/11/6b093179d92909927b4fc98d.jpg",
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

**Petición.** `POST http://entregas:5105/api/v1/entregas/170/resultado`

```http
Accept: application/json
X-Traza-Id: 0e3c58eb-cb9a-48b9-96b0-b5fe3d9ffa0f
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "resultado": "entregado",
  "monto_cobrado": 366.0,
  "cambio_entregado": 0,
  "ubicacion": {
    "latitud": 25.759995,
    "longitud": -100.371091
  },
  "evidencia_ids": [
    "6b093179d92909927b4fc98d"
  ],
  "capturado_en": "2026-11-27T07:30:01.748411+00:00",
  "id_cliente_local": "5279926e-d880-4f93-a405-540da2cb5085"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 76 ms · traza `0e3c58eb-cb9a-48b9-96b0-b5fe3d9ffa0f`

```json
{
  "entrega_id": 170,
  "pedido_id": 621,
  "estado_pedido": "entregado",
  "cerrado_en": "2026-11-27T01:30:01-06:00",
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
    "usuario_id": 53,
    "proceso": null
  },
  {
    "estado_anterior": "en_preparacion",
    "estado_nuevo": "en_ruta",
    "usuario_id": 53,
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
X-Traza-Id: 86eddf12-cced-4d60-8b54-8be0210ecbc2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 30 ms · traza `86eddf12-cced-4d60-8b54-8be0210ecbc2`

```json
{
  "datos": [
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
    },
    {
      "id": 595,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000620",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "620"
      },
      "creada_en": "2026-11-26T23:45:05-06:00"
    },
    {
      "id": 539,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000597",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "597"
      },
      "creada_en": "2026-11-26T23:38:27-06:00"
    },
    {
      "id": 538,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000596",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "596"
      },
      "creada_en": "2026-11-26T23:38:17-06:00"
    },
    {
      "id": 537,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000595",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "595"
      },
      "creada_en": "2026-11-26T23:38:13-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 348,
    "paginas": 70
  }
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F1-19 · El auditor reconstruye la historia del pedido · PASA

**Objetivo.** Bitácora, estados, inventario y archivos en una línea de tiempo.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/pedido/621`

```http
Accept: application/json
X-Traza-Id: 4f048025-8027-47df-ae13-cce2f7b1f235
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 113 ms · traza `4f048025-8027-47df-ae13-cce2f7b1f235`

```json
{
  "objeto": {
    "tipo": "pedido",
    "id": "621"
  },
  "total": 15,
  "eventos": [
    {
      "fecha": "2026-11-27T01:30:00-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "actualizado_en = 2026-11-27T01:30:00.930817-06:00; asignado_en = None; cerrado_en = None; cliente_id = 1",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "621"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": null,
          "nuevo": "2026-11-27T01:30:00.930817-06:00"
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
          "nuevo": "2026-11-27T01:30:00.930817-06:00"
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
          "nuevo": "PED-20261127-000621"
        },
        {
          "campo": "id",
          "anterior": null,
          "nuevo": "621"
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
      "fecha": "2026-11-27T01:30:00-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "asignado_en = 2026-11-27T01:30:00.930817-06:00; estado: creado → asignado; microhub_id = 9",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "621"
      },
      "cambios": [
        {
          "campo": "asignado_en",
          "anterior": null,
          "nuevo": "2026-11-27T01:30:00.930817-06:00"
        },
        {
          "campo": "estado",
          "anterior": "creado",
          "nuevo": "asignado"
        },
        {
          "campo": "microhub_id",
          "anterior": null,
          "nuevo": "9"
        }
      ]
    },
    {
      "fecha": "2026-11-27T01:30:00-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "nuevo → creado",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "621"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T01:30:00-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "creado → asignado",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "621"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T01:30:00-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -3 de producto 47 en microhub 9 (existencia 9)",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "9-47"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T01:30:00-06:00",
      "origen": "inventario",
      "accion": "movimiento_inventario",
      "descripcion": "salida_pedido: -3 de producto 51 en microhub 9 (existencia 9)",
      "usuario": {
        "id": 9,
        "nombre": "Juan Chapa Sepúlveda"
      },
      "entidad": {
        "tipo": "inventario",
        "id": "9-51"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T01:30:01-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-27T01:30:00.930817-06:00 → 2026-11-27T01:30:01.085737-06:00; estado: asignado → en_preparacion",
      "usuario": {
        "id": 53,
        "nombre": "Operador 9CB6E"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "621"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-27T01:30:00.930817-06:00",
          "nuevo": "2026-11-27T01:30:01.085737-06:00"
        },
        {
          "campo": "estado",
          "anterior": "asignado",
          "nuevo": "en_preparacion"
        }
      ]
    },
    {
      "fecha": "2026-11-27T01:30:01-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "asignado → en_preparacion",
      "usuario": {
        "id": 53,
        "nombre": "Operador 9CB6E"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "621"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T01:30:01-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "listo_en = 2026-11-27T01:30:01.14679-06:00",
      "usuario": {
        "id": 53,
        "nombre": "Operador 9CB6E"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "621"
      },
      "cambios": [
        {
          "campo": "listo_en",
          "anterior": null,
          "nuevo": "2026-11-27T01:30:01.14679-06:00"
        }
      ]
    },
    {
      "fecha": "2026-11-27T01:30:01-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "asignada_en = 2026-11-27T01:30:01.323081-06:00; cambio_entregado = None; capturado_en = None; cerrada_por_usuario_id = None",
      "usuario": {
        "id": 53,
        "nombre": "Operador 9CB6E"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "170"
      },
      "cambios": [
        {
          "campo": "asignada_en",
          "anterior": null,
          "nuevo": "2026-11-27T01:30:01.323081-06:00"
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
      "fecha": "2026-11-27T01:30:01-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-27T01:30:01.085737-06:00 → 2026-11-27T01:30:01.323081-06:00; estado: en_preparacion → en_ruta",
      "usuario": {
        "id": 53,
        "nombre": "Operador 9CB6E"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "621"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-27T01:30:01.085737-06:00",
          "nuevo": "2026-11-27T01:30:01.323081-06:00"
        },
        {
          "campo": "estado",
          "anterior": "en_preparacion",
          "nuevo": "en_ruta"
        }
      ]
    },
    {
      "fecha": "2026-11-27T01:30:01-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "en_preparacion → en_ruta",
      "usuario": {
        "id": 53,
        "nombre": "Operador 9CB6E"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "621"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T01:30:01-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "cambio_entregado = 0.0; capturado_en = 2026-11-27T01:30:01.7…(145 caracteres)",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "170"
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
          "nuevo": "2026-11-27T01:30:01.748411-06:00"
        },
        {
          "campo": "cerrada_por_usuario_id",
          "anterior": null,
          "nuevo": "7"
        },
        {
          "campo": "cierre_en",
          "anterior": null,
          "nuevo": "2026-11-27T01:30:01.778993-06:00"
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
          "nuevo": "[\"6b093179d92909927b4fc98d\"]"
        },
        {
          "campo": "evidencia_url",
          "anterior": null,
          "nuevo": "/api/v1/documentos/6b093179d92909927b4fc98d"
        },
        {
          "campo": "id_cliente_local",
          "anterior": null,
          "nuevo": "5279926e-d880-4f93-a405-540da2cb5085"
        },
        {
          "campo": "monto_cobrado",
          "anterior": null,
          "nuevo": "366.0"
        },
        {
          "campo": "resultado",
          "anterior": null,
          "nuevo": "entregado"
        }
      ]
    },
    {
      "fecha": "2026-11-27T01:30:01-06:00",
      "origen": "auditoria",
      "accion": "cambio_estado",
      "descripcion": "actualizado_en: 2026-11-27T01:30:01.323081-06:00 → 2026-11-2…(159 caracteres)",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "621"
      },
      "cambios": [
        {
          "campo": "actualizado_en",
          "anterior": "2026-11-27T01:30:01.323081-06:00",
          "nuevo": "2026-11-27T01:30:01.778993-06:00"
        },
        {
          "campo": "cerrado_en",
          "anterior": null,
          "nuevo": "2026-11-27T01:30:01.778993-06:00"
        },
        {
          "campo": "estado",
          "anterior": "en_ruta",
          "nuevo": "entregado"
        }
      ]
    },
    {
      "fecha": "2026-11-27T01:30:01-06:00",
      "origen": "estados",
      "accion": "cambio_estado",
      "descripcion": "en_ruta → entregado",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "pedido",
        "id": "621"
      },
      "cambios": []
    }
  ]
}
```

## Servicio reportes · puerto 5123

### F1-20 · Visualización: el microhub nuevo ya aparece en la comparación · PASA

**Objetivo.** Datos listos para Highcharts.

**Petición.** `GET http://reportes:5123/api/v1/reportes/comparacion_microhubs/grafica?microhub_id=9`

```http
Accept: application/json
X-Traza-Id: 5cfd6dfa-ddd2-416b-bb66-4cba998470e1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwi…(298 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 81 ms · traza `5cfd6dfa-ddd2-416b-bb66-4cba998470e1`

```json
{
  "reporte": "comparacion_microhubs",
  "titulo": "Comparación entre microhubs",
  "tipo": "column",
  "unidad": "pedidos / MXN",
  "categorias": [
    "Microhub 9CB6E"
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
        366.0
      ]
    }
  ]
}
```

## Servicio microhubs · puerto 5109

### F1-21 · Cierre: dar de baja el microhub de la demostración · PASA

**Objetivo.** Baja lógica; conserva su historia.

**Petición.** `DELETE http://microhubs:5109/api/v1/microhubs/9`

```http
Accept: application/json
X-Traza-Id: 899929f3-6c65-41a2-8b85-c4e9a10f7566
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 204 (esperado 204) · 35 ms · traza `899929f3-6c65-41a2-8b85-c4e9a10f7566`

```json
(sin cuerpo)
```

## Servicio pedidos · puerto 5104

### F2-01 · Android: un cliente compra y el inventario baja · PASA

**Objetivo.** El motor descuenta inventario en la misma transacción.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: 93dc62bd-eab7-4560-92c3-e35398dbb47d
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
  "operacion_uuid": "f9b64f9f-e4d7-4c30-b0aa-8375c646944c"
}
```

**Respuesta.** HTTP 201 (esperado 201) · 142 ms · traza `93dc62bd-eab7-4560-92c3-e35398dbb47d`

```json
{
  "id": 622,
  "folio": "PED-20261127-000622",
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
    "existencia_resultante": 59
  }
]
```

## Servicio inventario · puerto 5111

### F2-02 · El operador fija el mínimo y nace la alerta · PASA

**Objetivo.** El trigger avisa del faltante.

**Petición.** `PATCH http://inventario:5111/api/v1/inventario/1/51/minimo`

```http
Accept: application/json
X-Traza-Id: 9ea1c354-2cf6-41c2-8f7a-1621ee8c2f55
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "minimo": 215
}
```

**Respuesta.** HTTP 200 (esperado 200) · 200 ms · traza `9ea1c354-2cf6-41c2-8f7a-1621ee8c2f55`

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
  "existencia": 205,
  "minimo": 215,
  "reservado": 0,
  "disponible": 205,
  "estado": "bajo_minimo",
  "actualizado_en": "2026-11-27T01:30:03-06:00"
}
```

### F2-03 · La alerta de faltante · PASA

**Objetivo.** Qué producto, cuánto falta y qué tan grave es.

**Petición.** `GET http://inventario:5111/api/v1/inventario/alertas?microhub_id=1&por_pagina=100`

```http
Accept: application/json
X-Traza-Id: 00d6ab04-0b8a-4c5f-bf4f-3368bb6cf973
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 72 ms · traza `00d6ab04-0b8a-4c5f-bf4f-3368bb6cf973`

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
      "existencia": 205,
      "minimo": 215,
      "disponible": 205,
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
X-Traza-Id: 82f87f87-1921-4088-a590-1f8e09694520
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

**Respuesta.** HTTP 201 (esperado 201) · 62 ms · traza `82f87f87-1921-4088-a590-1f8e09694520`

```json
{
  "id": 23,
  "folio": "SC-20261127-000023",
  "microhub_id": 1,
  "estado": "pendiente",
  "motivo": "Faltante detectado por el sistema",
  "solicitada_por": 2,
  "decidida_por": null,
  "decision_motivo": null,
  "decidida_en": null,
  "creada_en": "2026-11-27T01:30:03-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/23/decision`

```http
Accept: application/json
X-Traza-Id: 0b7bd333-87a7-4659-8720-14a2c4e95e5b
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{
  "decision": "aprobada",
  "motivo": "Con presupuesto"
}
```

**Respuesta.** HTTP 200 (esperado 200) · 71 ms · traza `0b7bd333-87a7-4659-8720-14a2c4e95e5b`

```json
{
  "id": 23,
  "folio": "SC-20261127-000023",
  "microhub_id": 1,
  "estado": "aprobada",
  "motivo": "Faltante detectado por el sistema",
  "solicitada_por": 2,
  "decidida_por": 1,
  "decision_motivo": "Con presupuesto",
  "decidida_en": "2026-11-27T01:30:03-06:00",
  "creada_en": "2026-11-27T01:30:03-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/solicitudes/23/ordenar`

```http
Accept: application/json
X-Traza-Id: 0c63e823-ba95-4564-ac33-8583c3a8df1e
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
Content-Type: application/json
```

```json
{}
```

**Respuesta.** HTTP 201 (esperado 201) · 212 ms · traza `0c63e823-ba95-4564-ac33-8583c3a8df1e`

```json
{
  "solicitud_id": 23,
  "ordenes": [
    {
      "id": 19,
      "folio": "OC-20261127-000019",
      "solicitud_id": 23,
      "proveedor": {
        "id": 3,
        "nombre": "Mayorista San Nicolás"
      },
      "microhub_id": 1,
      "estado": "emitida",
      "fecha_esperada": "2026-12-01",
      "total": 4624.0,
      "creada_en": "2026-11-27T01:30:03-06:00",
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

**Petición.** `POST http://abastecimiento:5114/api/v1/abastecimiento/ordenes/19/recepcion`

```http
Accept: application/json
X-Traza-Id: ab4bcdf6-2849-4f94-9c05-bac47a1592fa
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwi…(302 caracteres)
Content-Type: application/json
```

```json
{
  "operacion_uuid": "bca20eb4-45b7-4d0e-9a8f-4ed55d5b5981",
  "nota": "Completo",
  "lineas": [
    {
      "producto_id": 51,
      "cantidad": 100
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 231 ms · traza `ab4bcdf6-2849-4f94-9c05-bac47a1592fa`

```json
{
  "orden": {
    "id": 19,
    "folio": "OC-20261127-000019",
    "solicitud_id": 23,
    "proveedor": {
      "id": 3,
      "nombre": "Mayorista San Nicolás"
    },
    "microhub_id": 1,
    "estado": "recibida",
    "fecha_esperada": "2026-12-01",
    "total": 4624.0,
    "creada_en": "2026-11-27T01:30:03-06:00",
    "cerrada_en": "2026-11-27T01:30:03-06:00",
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
    "existencia": 305,
    "minimo": 215
  }
]
```

## Servicio documentos · puerto 5107

### F2-08 · La remisión firmada queda en el almacén · PASA

**Objetivo.** Archivo con enlace firmado.

**Petición.** `GET http://documentos:5107/api/v1/documentos/6b09317bd92909927b4fc992/enlace`

```http
Accept: application/json
X-Traza-Id: 289cfbf5-7a12-40e6-a223-3934dd988e59
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 123 ms · traza `289cfbf5-7a12-40e6-a223-3934dd988e59`

```json
{
  "id": "6b09317bd92909927b4fc992",
  "nombre": "remision-19.jpg",
  "url_firmada": "https://storage.googleapis.com/microhubs-evidencias-637044/d…(994 caracteres)",
  "metodo": "GET",
  "segundos": 300,
  "expira_en": "2026-11-27T01:35:04-06:00"
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F2-09 · Trazabilidad del producto en el microhub · PASA

**Objetivo.** Salida por pedido y recepción por orden.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/inventario?microhub_id=1&producto_id=51`

```http
Accept: application/json
X-Traza-Id: 7fc2b8e0-674e-4ec0-955c-8d1ece81df89
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 39 ms · traza `7fc2b8e0-674e-4ec0-955c-8d1ece81df89`

```json
{
  "objeto": {
    "tipo": "inventario",
    "id": "1-51"
  },
  "total": 13,
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
X-Traza-Id: fb17a073-6a56-4c31-ad09-7f9b93c3ee87
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 160 ms · traza `fb17a073-6a56-4c31-ad09-7f9b93c3ee87`

```json
﻿Microhub,Producto,Existencia,Mínimo,Disponible,Faltante,Severidad
Microhub San Bernabé Centro,Galletas María,7,8,7,1,baja
Total,,,,,1,

```

## Servicio pedidos · puerto 5104

### F3-01 · El cliente hace un pedido · PASA

**Objetivo.** Punto de partida del recorrido.

**Petición.** `POST http://pedidos:5104/api/v1/pedidos`

```http
Accept: application/json
X-Traza-Id: 2d211447-1b1c-405b-901a-a9082b2fb441
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

**Respuesta.** HTTP 201 (esperado 201) · 205 ms · traza `2d211447-1b1c-405b-901a-a9082b2fb441`

```json
{
  "id": 623,
  "folio": "PED-20261127-000623",
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
X-Traza-Id: 7b43d1d8-b24a-4c0b-8141-301dcd839d39
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwi…(310 caracteres)
Content-Type: application/json
```

```json
{
  "pedido_id": 623,
  "repartidor_id": 7
}
```

**Respuesta.** HTTP 201 (esperado 201) · 38 ms · traza `7b43d1d8-b24a-4c0b-8141-301dcd839d39`

```json
{
  "entrega_id": 171,
  "pedido_id": 623,
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
X-Traza-Id: 73cbd866-ea8a-4e14-a4c8-e0377bc18a1c
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "38e40b06-effd-4f12-9658-5392eb296dd1",
  "dispositivo": "android-flujo-4862a7",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "7c071c42-24c8-45a3-b76b-021265b5d56a",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-27T07:10:06.040562+00:00",
      "datos": {
        "entrega_id": 171,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-27T07:10:06.040581+00:00"
          },
          {
            "latitud": 25.7491,
            "longitud": -100.3611,
            "capturado_en": "2026-11-27T07:15:06.040586+00:00"
          }
        ]
      }
    },
    {
      "operacion_uuid": "f3faa6ac-e0b0-4bd8-909a-f4db8aab0522",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-27T07:18:06.040596+00:00",
      "datos": {
        "entrega_id": 171,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "El cliente no estaba en su domicilio",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b09317dd92909927b4fc997"
        ],
        "capturado_en": "2026-11-27T07:18:06.040600+00:00"
      }
    }
  ]
}
```

**Respuesta.** HTTP 201 (esperado 201) · 274 ms · traza `73cbd866-ea8a-4e14-a4c8-e0377bc18a1c`

```json
{
  "id": 15,
  "lote_uuid": "38e40b06-effd-4f12-9658-5392eb296dd1",
  "dispositivo": "android-flujo-4862a7",
  "recibido_en": "2026-11-27T01:30:06-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 0,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "7c071c42-24c8-45a3-b76b-021265b5d56a",
      "tipo": "ubicaciones",
      "estado": "aplicada",
      "duplicada": false,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    },
    {
      "operacion_uuid": "f3faa6ac-e0b0-4bd8-909a-f4db8aab0522",
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
    "creada_en": "2026-11-27 01:10:06.040562-06:00"
  },
  {
    "tipo": "entrega_resultado",
    "estado": "aplicada",
    "intentos": 1,
    "creada_en": "2026-11-27 01:18:06.040596-06:00"
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
X-Traza-Id: 4a4d51c0-f67f-4043-89e6-e0c60a3fdbfc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3Iiwi…(298 caracteres)
Content-Type: application/json
```

```json
{
  "lote_uuid": "38e40b06-effd-4f12-9658-5392eb296dd1",
  "dispositivo": "android-flujo-4862a7",
  "cliente": "android",
  "operaciones": [
    {
      "operacion_uuid": "7c071c42-24c8-45a3-b76b-021265b5d56a",
      "tipo": "ubicaciones",
      "creada_en": "2026-11-27T07:10:06.040562+00:00",
      "datos": {
        "entrega_id": 171,
        "puntos": [
          {
            "latitud": 25.7488,
            "longitud": -100.3608,
            "capturado_en": "2026-11-27T07:10:06.040581+00:00"
          },
          {
            "latitud": 25.7491,
            "longitud": -100.3611,
            "capturado_en": "2026-11-27T07:15:06.040586+00:00"
          }
        ]
      }
    },
    {
      "operacion_uuid": "f3faa6ac-e0b0-4bd8-909a-f4db8aab0522",
      "tipo": "entrega_resultado",
      "creada_en": "2026-11-27T07:18:06.040596+00:00",
      "datos": {
        "entrega_id": 171,
        "resultado": "fallida",
        "monto_cobrado": 0,
        "cambio_entregado": 0,
        "incidencia": "El cliente no estaba en su domicilio",
        "ubicacion": {
          "latitud": 25.7491,
          "longitud": -100.3611
        },
        "evidencia_ids": [
          "6b09317dd92909927b4fc997"
        ],
        "capturado_en": "2026-11-27T07:18:06.040600+00:00"
      }
    }
  ]
}
```

**Respuesta.** HTTP 200 (esperado 200) · 122 ms · traza `4a4d51c0-f67f-4043-89e6-e0c60a3fdbfc`

```json
{
  "id": 15,
  "lote_uuid": "38e40b06-effd-4f12-9658-5392eb296dd1",
  "dispositivo": "android-flujo-4862a7",
  "recibido_en": "2026-11-27T01:30:06-06:00",
  "total": 2,
  "aplicadas": 2,
  "duplicadas": 2,
  "conflictos": 0,
  "rechazadas": 0,
  "pendientes": 0,
  "operaciones": [
    {
      "operacion_uuid": "7c071c42-24c8-45a3-b76b-021265b5d56a",
      "tipo": "ubicaciones",
      "estado": "aplicada",
      "duplicada": true,
      "http_status": 201,
      "codigo": null,
      "mensaje": null,
      "reintentar": false
    },
    {
      "operacion_uuid": "f3faa6ac-e0b0-4bd8-909a-f4db8aab0522",
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
X-Traza-Id: 5e85f665-e5e5-442a-80bf-4e234f7598aa
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwi…(291 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 32 ms · traza `5e85f665-e5e5-442a-80bf-4e234f7598aa`

```json
{
  "datos": [
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
    },
    {
      "id": 595,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000620",
      "mensaje": "El pedido cambió a entregado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "620"
      },
      "creada_en": "2026-11-26T23:45:05-06:00"
    },
    {
      "id": 539,
      "tipo": "pedido",
      "titulo": "Pedido PED-20261126-000597",
      "mensaje": "El pedido cambió a cancelado.",
      "leida": false,
      "referencia": {
        "tipo": "pedido",
        "id": "597"
      },
      "creada_en": "2026-11-26T23:38:27-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 350,
    "paginas": 70
  }
}
```

## Servicio auditoria-monitoreo · puerto 5126

### F3-06 · El auditor revisa la entrega · PASA

**Objetivo.** Bitácora y archivos de la entrega.

**Petición.** `GET http://auditoria-monitoreo:5126/api/v1/auditoria/trazabilidad/entrega/171`

```http
Accept: application/json
X-Traza-Id: f411591c-0411-4491-9e31-4249e19f4770
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2Iiwi…(294 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 39 ms · traza `f411591c-0411-4491-9e31-4249e19f4770`

```json
{
  "objeto": {
    "tipo": "entrega",
    "id": "171"
  },
  "total": 3,
  "eventos": [
    {
      "fecha": "2026-11-27T01:30:05-06:00",
      "origen": "auditoria",
      "accion": "alta",
      "descripcion": "asignada_en = 2026-11-27T01:30:05.929257-06:00; cambio_entregado = None; capturado_en = None; cerrada_por_usuario_id = None",
      "usuario": {
        "id": 3,
        "nombre": "María José Cedillo Mata"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "171"
      },
      "cambios": [
        {
          "campo": "asignada_en",
          "anterior": null,
          "nuevo": "2026-11-27T01:30:05.929257-06:00"
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
      "fecha": "2026-11-27T01:30:05-06:00",
      "origen": "documentos",
      "accion": "documento_subido",
      "descripcion": "evidencia-flujo3-171.jpg (276 bytes, sha256 7f6025cd8a98…)",
      "usuario": {
        "id": 7,
        "nombre": null
      },
      "entidad": {
        "tipo": "documento",
        "id": "6b09317dd92909927b4fc997"
      },
      "cambios": []
    },
    {
      "fecha": "2026-11-27T01:30:06-06:00",
      "origen": "auditoria",
      "accion": "modificacion",
      "descripcion": "cambio_entregado = 0.0; capturado_en = 2026-11-27T01:18:06.0…(143 caracteres)",
      "usuario": {
        "id": 7,
        "nombre": "Ramiro Alanís Lozano"
      },
      "entidad": {
        "tipo": "entrega",
        "id": "171"
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
          "nuevo": "2026-11-27T01:18:06.0406-06:00"
        },
        {
          "campo": "cerrada_por_usuario_id",
          "anterior": null,
          "nuevo": "7"
        },
        {
          "campo": "cierre_en",
          "anterior": null,
          "nuevo": "2026-11-27T01:30:06.201953-06:00"
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
          "nuevo": "[\"6b09317dd92909927b4fc997\"]"
        },
        {
          "campo": "evidencia_url",
          "anterior": null,
          "nuevo": "/api/v1/documentos/6b09317dd92909927b4fc997"
        },
        {
          "campo": "id_cliente_local",
          "anterior": null,
          "nuevo": "f3faa6ac-e0b0-4bd8-909a-f4db8aab0522"
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
X-Traza-Id: 1b4fd662-44ea-4572-bf00-ace501889fd3
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 53 ms · traza `1b4fd662-44ea-4572-bf00-ace501889fd3`

```json
{
  "datos": [
    {
      "id": 2670,
      "microhub_id": 2,
      "producto_id": 51,
      "tipo": "devolucion_cancelacion",
      "cantidad": 3,
      "existencia_resultante": 69,
      "referencia": {
        "tipo": "pedido",
        "id": "623"
      },
      "motivo": "Entrega fallida: la mercancía regresa al microhub.",
      "usuario_id": 7,
      "fecha": "2026-11-27T01:30:06-06:00"
    },
    {
      "id": 2669,
      "microhub_id": 2,
      "producto_id": 32,
      "tipo": "devolucion_cancelacion",
      "cantidad": 3,
      "existencia_resultante": 19,
      "referencia": {
        "tipo": "pedido",
        "id": "623"
      },
      "motivo": "Entrega fallida: la mercancía regresa al microhub.",
      "usuario_id": 7,
      "fecha": "2026-11-27T01:30:06-06:00"
    },
    {
      "id": 2668,
      "microhub_id": 2,
      "producto_id": 51,
      "tipo": "salida_pedido",
      "cantidad": -3,
      "existencia_resultante": 66,
      "referencia": {
        "tipo": "pedido",
        "id": "623"
      },
      "motivo": null,
      "usuario_id": 9,
      "fecha": "2026-11-27T01:30:05-06:00"
    },
    {
      "id": 2667,
      "microhub_id": 2,
      "producto_id": 32,
      "tipo": "salida_pedido",
      "cantidad": -3,
      "existencia_resultante": 16,
      "referencia": {
        "tipo": "pedido",
        "id": "623"
      },
      "motivo": null,
      "usuario_id": 9,
      "fecha": "2026-11-27T01:30:05-06:00"
    },
    {
      "id": 2666,
      "microhub_id": 2,
      "producto_id": 51,
      "tipo": "devolucion_cancelacion",
      "cantidad": 10,
      "existencia_resultante": 69,
      "referencia": {
        "tipo": "pedido",
        "id": "622"
      },
      "motivo": "Cierre del flujo de demostración",
      "usuario_id": 1,
      "fecha": "2026-11-27T01:30:04-06:00"
    }
  ],
  "paginacion": {
    "pagina": 1,
    "por_pagina": 5,
    "total": 1829,
    "paginas": 366
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
    "existencia_resultante": 16
  },
  {
    "tipo": "salida_pedido",
    "producto_id": 51,
    "cantidad": -3,
    "existencia_resultante": 66
  },
  {
    "tipo": "devolucion_cancelacion",
    "producto_id": 32,
    "cantidad": 3,
    "existencia_resultante": 19
  },
  {
    "tipo": "devolucion_cancelacion",
    "producto_id": 51,
    "cantidad": 3,
    "existencia_resultante": 69
  }
]
```

## Servicio reportes · puerto 5123

### F3-08 · Reporte del periodo en CSV · PASA

**Objetivo.** La entrega ya cuenta en los reportes.

**Petición.** `GET http://reportes:5123/api/v1/reportes/pedidos_por_dia/exportar?formato=csv`

```http
Accept: application/json
X-Traza-Id: f4f7ac72-f59e-49b9-ab18-18b24bafa60d
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwi…(300 caracteres)
```

**Respuesta.** HTTP 200 (esperado 200) · 213 ms · traza `f4f7ac72-f59e-49b9-ab18-18b24bafa60d`

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
2026-11-27,2,12,786.00,393.00,0
Total,163,849,31825.10,195.25,35

```

**Evidencia en PostgreSQL.** `SELECT reporte, formato, filas, left(sha256, 16) AS sha256 FROM reporte_exportacion ORDER BY id DESC LIMIT 1`

```json
[
  {
    "reporte": "pedidos_por_dia",
    "formato": "csv",
    "filas": 29,
    "sha256": "b2e882e92a0b936e"
  }
]
```
