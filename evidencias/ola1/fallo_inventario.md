# Qué pasa si inventario se cae durante una recepción

Producto: Galletas María (id 16). Se piden 74 piezas al proveedor PV-01. Los contenedores son los de `docker-compose.integrado.yml`; el de inventario se apaga con `docker compose stop inventario`.

### 1. El operador pide la mercancía

`POST :5114/api/v1/abastecimiento/solicitudes` → **HTTP 201**

```json
{
  "microhub_id": 1,
  "motivo": "Demostración de fallo",
  "lineas": [
    {
      "producto_id": 16,
      "cantidad": 74
    }
  ]
}
```

```json
{
  "id": 10,
  "folio": "SC-20261020-000010",
  "microhub_id": 1,
  "estado": "pendiente",
  "motivo": "Demostración de fallo",
  "solicitada_por": 2,
  "decidida_por": null,
  "decision_motivo": null,
  "decidida_en": null,
  "creada_en": "2026-10-19T19:33:41-06:00",
  "lineas": [
    {
      "producto": {
        "id": 16,
        "nombre": "Galletas María"
      },
      "cantidad": 74
    }
  ]
}
```

### 2. El administrador aprueba

`POST :5114/api/v1/abastecimiento/solicitudes/10/decision` → **HTTP 200**

```json
{
  "decision": "aprobada",
  "motivo": "Hay presupuesto"
}
```

```json
{
  "id": 10,
  "folio": "SC-20261020-000010",
  "microhub_id": 1,
  "estado": "aprobada",
  "motivo": "Demostración de fallo",
  "solicitada_por": 2,
  "decidida_por": 1,
  "decision_motivo": "Hay presupuesto",
  "decidida_en": "2026-10-19T19:33:42-06:00",
  "creada_en": "2026-10-19T19:33:41-06:00",
  "lineas": [
    {
      "producto": {
        "id": 16,
        "nombre": "Galletas María"
      },
      "cantidad": 74
    }
  ]
}
```

### 3. Se emite la orden de compra

`POST :5114/api/v1/abastecimiento/solicitudes/10/ordenar` → **HTTP 201**

```json
{
  "proveedor_id": 1
}
```

```json
{
  "solicitud_id": 10,
  "ordenes": [
    {
      "id": 6,
      "folio": "OC-20261020-000006",
      "solicitud_id": 10,
      "proveedor": {
        "id": 1,
        "nombre": "Abarrotes del Norte"
      },
      "microhub_id": 1,
      "estado": "emitida",
      "fecha_esperada": "2026-10-21",
      "total": 854.7,
      "creada_en": "2026-10-19T19:33:42-06:00",
      "cerrada_en": null,
      "lineas": [
        {
          "producto": {
            "id": 16,
            "nombre": "Galletas María"
          },
          "cantidad": 74,
          "precio_compra": 11.55,
          "cantidad_recibida": 0,
          "pendiente_inventario": 0
        }
      ]
    }
  ]
}
```

Existencia en el microhub 1 antes de recibir: **10**.

## Se apaga inventario

### 4. Llega la mercancía y inventario no responde

`POST :5114/api/v1/abastecimiento/ordenes/6/recepcion` → **HTTP 202**

```json
{
  "nota": "Llegó con inventario caído",
  "lineas": [
    {
      "producto_id": 16,
      "cantidad": 74
    }
  ]
}
```

```json
{
  "orden": {
    "id": 6,
    "folio": "OC-20261020-000006",
    "solicitud_id": 10,
    "proveedor": {
      "id": 1,
      "nombre": "Abarrotes del Norte"
    },
    "microhub_id": 1,
    "estado": "emitida",
    "fecha_esperada": "2026-10-21",
    "total": 854.7,
    "creada_en": "2026-10-19T19:33:42-06:00",
    "cerrada_en": null,
    "lineas": [
      {
        "producto": {
          "id": 16,
          "nombre": "Galletas María"
        },
        "cantidad": 74,
        "precio_compra": 11.55,
        "cantidad_recibida": 0,
        "pendiente_inventario": 74
      }
    ]
  },
  "aplicadas": 0,
  "pendientes": 1,
  "aviso": "Inventario no registró la entrada: El servicio inventario no responde. Intenta más tarde."
}
```

La recepción se guardó, pero la entrada a inventario quedó **pendiente** (`pendiente_inventario` en la línea). La respuesta es 202, no un error: la mercancía llegó y el sistema lo recuerda.

### 5. El tablero cuenta lo pendiente

`GET :5114/api/v1/abastecimiento/seguimiento` → **HTTP 200**

```json
{
  "microhub_id": 1,
  "solicitudes": {
    "pendiente": 0,
    "aprobada": 0,
    "rechazada": 3,
    "ordenada": 6
  },
  "ordenes": {
    "emitida": 1,
    "parcial": 0,
    "recibida": 3,
    "cancelada": 2
  },
  "atrasadas": 0,
  "pendientes_inventario": 1,
  "proxima_entrega": "2026-10-21"
}
```

## Se vuelve a encender inventario

### 6. Se reintenta la recepción (mismo POST, sin líneas)

`POST :5114/api/v1/abastecimiento/ordenes/6/recepcion` → **HTTP 201**

```json
{}
```

```json
{
  "orden": {
    "id": 6,
    "folio": "OC-20261020-000006",
    "solicitud_id": 10,
    "proveedor": {
      "id": 1,
      "nombre": "Abarrotes del Norte"
    },
    "microhub_id": 1,
    "estado": "recibida",
    "fecha_esperada": "2026-10-21",
    "total": 854.7,
    "creada_en": "2026-10-19T19:33:42-06:00",
    "cerrada_en": "2026-10-19T19:33:57-06:00",
    "lineas": [
      {
        "producto": {
          "id": 16,
          "nombre": "Galletas María"
        },
        "cantidad": 74,
        "precio_compra": 11.55,
        "cantidad_recibida": 74,
        "pendiente_inventario": 0
      }
    ]
  },
  "aplicadas": 1,
  "pendientes": 0,
  "aviso": null
}
```

Existencia después: **84** (antes 10 + 74 recibidas = 84).

### 7. Un segundo reintento no vuelve a sumar

`POST :5114/api/v1/abastecimiento/ordenes/6/recepcion` → **HTTP 201**

```json
{}
```

```json
{
  "orden": {
    "id": 6,
    "folio": "OC-20261020-000006",
    "solicitud_id": 10,
    "proveedor": {
      "id": 1,
      "nombre": "Abarrotes del Norte"
    },
    "microhub_id": 1,
    "estado": "recibida",
    "fecha_esperada": "2026-10-21",
    "total": 854.7,
    "creada_en": "2026-10-19T19:33:42-06:00",
    "cerrada_en": "2026-10-19T19:33:58-06:00",
    "lineas": [
      {
        "producto": {
          "id": 16,
          "nombre": "Galletas María"
        },
        "cantidad": 74,
        "precio_compra": 11.55,
        "cantidad_recibida": 74,
        "pendiente_inventario": 0
      }
    ]
  },
  "aplicadas": 0,
  "pendientes": 0,
  "aviso": null
}
```

Existencia al final: **84**. La entrada entró una sola vez gracias a la `operacion_uuid` de la línea.
