/* =====================================================================
 * 01_colecciones.js — Diseño de colecciones MongoDB
 * Plataforma de Microhubs · Codex Innovations · Equipo 04
 *
 *   mongosh "mongodb://localhost:27017/microhubs_eventos" 01_colecciones.js
 *
 * CRITERIO DE REPARTO (RNF06)
 * PostgreSQL guarda lo que debe ser consistente y referenciable: pedidos,
 * inventario, entregas, auditoría de negocio. MongoDB guarda lo que es
 * un evento inmutable de forma variable: trazas de algoritmos, corridas
 * analíticas con parámetros heterogéneos, logs técnicos y colas de
 * sincronización móvil.
 *
 * La prueba para decidir dónde va un dato: si perderlo rompe un saldo o
 * una relación, va en PostgreSQL. Si perderlo solo estorba un análisis,
 * puede ir en MongoDB.
 *
 * RNF33 es explícito: la bitácora de auditoría (PostgreSQL) reconstruye
 * operaciones de negocio; los logs técnicos (MongoDB) sirven para
 * diagnóstico. Ninguno sustituye al otro, y por eso no viven juntos.
 * ===================================================================== */

const BD = "microhubs_eventos";
db = db.getSiblingDB(BD);

/* ---------------------------------------------------------------------
 * 1. eventos_demanda — RF22, HU01, HU08
 * Alimenta el análisis de demanda por zona y horario. Incluye demanda
 * ATENDIDA y NO ATENDIDA: HU01 CA2 exige ambas.
 *
 * Sin datos personales: HU01 CA1 pide agrupar por zona y periodo sin
 * exponer teléfono, correo ni domicilio. El esquema ni siquiera tiene
 * campos donde guardarlos, para que no puedan filtrarse por descuido.
 * ------------------------------------------------------------------- */
db.createCollection("eventos_demanda", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["tipo", "ocurrido_en", "zona", "origen"],
      additionalProperties: false,
      properties: {
        _id: { bsonType: "objectId" },
        tipo: {
          enum: ["atendida", "fuera_cobertura", "sin_existencia",
                 "bajo_ticket_minimo", "excede_limite_linea", "sin_microhub_elegible"],
          description: "Corresponde a tipo_demanda de PostgreSQL."
        },
        ocurrido_en: { bsonType: "date" },
        franja_horaria: { bsonType: "int", minimum: 0, maximum: 23 },
        dia_semana: { bsonType: "int", minimum: 1, maximum: 7 },
        zona: {
          bsonType: "object",
          required: ["clave"],
          properties: {
            clave: { bsonType: "string" },
            colonia: { bsonType: "string" },
            codigo_postal: { bsonType: "string", pattern: "^[0-9]{5}$" }
          }
        },
        productos: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              clave_interna: { bsonType: "string" },
              cantidad_solicitada: { bsonType: "int", minimum: 1 }
            }
          }
        },
        importe: { bsonType: "decimal" },
        pedido_id: { bsonType: ["long", "null"], description: "Enlace opcional al pedido de PostgreSQL." },
        origen: { enum: ["web", "android", "escritorio", "api"] }
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
});

db.eventos_demanda.createIndex({ "zona.clave": 1, ocurrido_en: -1 }, { name: "ix_zona_fecha" });
db.eventos_demanda.createIndex({ tipo: 1, ocurrido_en: -1 }, { name: "ix_tipo_fecha" });
db.eventos_demanda.createIndex({ ocurrido_en: -1, franja_horaria: 1 }, { name: "ix_franja" });
db.eventos_demanda.createIndex({ "productos.clave_interna": 1 }, { name: "ix_producto", sparse: true });

/* ---------------------------------------------------------------------
 * 2. decisiones_asignacion — RN15
 * PostgreSQL guarda el resumen auditable (ganador, criterio, cuántos
 * candidatos) porque necesita integridad referencial contra pedido.
 * Aquí va la traza COMPLETA: cada candidato con su distancia, su stock y
 * su capacidad al momento de decidir.
 *
 * RN15 pide poder auditar el algoritmo, no solo su resultado. Sin el
 * detalle de los perdedores es imposible responder "¿por qué este hub y
 * no el otro?" seis semanas después.
 * ------------------------------------------------------------------- */
db.createCollection("decisiones_asignacion", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["pedido_id", "folio", "decidido_en", "criterio", "candidatos"],
      properties: {
        pedido_id: { bsonType: "long" },
        folio: { bsonType: "string" },
        decidido_en: { bsonType: "date" },
        criterio: { enum: ["menor_distancia", "mayor_capacidad_libre", "manual", "sin_elegible"] },
        manual: { bsonType: "bool" },
        usuario_id: { bsonType: ["int", "null"] },
        motivo: { bsonType: ["string", "null"], description: "RN24: obligatorio si manual = true." },
        ganador: { bsonType: ["object", "null"] },
        domicilio: {
          bsonType: "object",
          description: "Solo coordenadas y zona. RN34: nunca la dirección completa.",
          properties: {
            latitud: { bsonType: "double" },
            longitud: { bsonType: "double" },
            zona_clave: { bsonType: "string" }
          }
        },
        parametros_vigentes: {
          bsonType: "object",
          description: "RN40: los valores usados al decidir, para poder repetir la evaluación aunque la configuración cambie después."
        },
        candidatos: {
          bsonType: "array",
          minItems: 0,
          items: {
            bsonType: "object",
            required: ["microhub_clave", "elegible"],
            properties: {
              microhub_clave: { bsonType: "string" },
              distancia_km: { bsonType: "double" },
              cubre: { bsonType: "bool" },
              stock_completo: { bsonType: "bool" },
              capacidad_libre: { bsonType: "int" },
              elegible: { bsonType: "bool" },
              motivo_descarte: { bsonType: ["string", "null"] }
            }
          }
        },
        duracion_ms: { bsonType: "int" }
      }
    }
  }
});

db.decisiones_asignacion.createIndex({ pedido_id: 1 }, { name: "ix_pedido", unique: true });
db.decisiones_asignacion.createIndex({ decidido_en: -1 }, { name: "ix_fecha" });
db.decisiones_asignacion.createIndex({ criterio: 1, decidido_en: -1 }, { name: "ix_criterio" });
db.decisiones_asignacion.createIndex({ "ganador.microhub_clave": 1 }, { name: "ix_ganador" });

/* ---------------------------------------------------------------------
 * 3. ejecuciones_analiticas — RF28, RNF16
 * Toda simulación del Planeador: demanda, facility location, M/M/1 y
 * M/M/c, punto de equilibrio, surtido, sensibilidad.
 *
 * RNF16 exige reproducibilidad: una corrida debe poder repetirse desde
 * sus parámetros. Por eso se guardan la semilla, la versión del modelo y
 * el rango de datos usado, no solo el resultado. Un resultado sin sus
 * supuestos no es auditable, es una opinión con decimales.
 *
 * HU02 CA3, HU04 CA3, HU07 CA2: la salida es una RECOMENDACIÓN. El
 * campo `aplicado_por` existe para registrar que una persona la tomó,
 * nunca para que el sistema la ejecute solo.
 * ------------------------------------------------------------------- */
db.createCollection("ejecuciones_analiticas", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["escenario_id", "tipo_analisis", "ejecutado_en", "usuario_id", "parametros_entrada"],
      properties: {
        escenario_id: { bsonType: "string", description: "HU06 CA1: identificador que distingue el escenario." },
        nombre_escenario: { bsonType: "string" },
        tipo_analisis: {
          enum: ["demanda", "facility_location", "capacidad_mm1", "capacidad_mmc",
                 "punto_equilibrio", "surtido", "sensibilidad", "rutas"]
        },
        ejecutado_en: { bsonType: "date" },
        usuario_id: { bsonType: "int" },
        version_modelo: { bsonType: "string" },
        semilla_aleatoria: { bsonType: ["long", "null"] },
        rango_datos: {
          bsonType: "object",
          properties: { desde: { bsonType: "date" }, hasta: { bsonType: "date" } }
        },
        parametros_entrada: { bsonType: "object" },
        supuestos: { bsonType: "array", items: { bsonType: "string" } },
        resultados: { bsonType: "object" },
        recomendacion: { bsonType: ["string", "null"] },
        datos_suficientes: {
          bsonType: "bool",
          description: "CU10 A1: si es false, el resultado no se presenta como concluyente."
        },
        duracion_ms: { bsonType: "int" },
        aplicado_por: {
          bsonType: ["object", "null"],
          description: "RN: la apertura o cierre de un microhub es decisión humana. Este campo registra quién la tomó; el sistema nunca la ejecuta por su cuenta."
        }
      }
    }
  }
});

db.ejecuciones_analiticas.createIndex({ escenario_id: 1, ejecutado_en: -1 }, { name: "ix_escenario" });
db.ejecuciones_analiticas.createIndex({ tipo_analisis: 1, ejecutado_en: -1 }, { name: "ix_tipo" });
db.ejecuciones_analiticas.createIndex({ usuario_id: 1, ejecutado_en: -1 }, { name: "ix_usuario" });

/* ---------------------------------------------------------------------
 * 4. logs_tecnicos — RF48, RNF33, RNF34, RNF35
 * Colección CAPPED: se autolimita en tamaño y no puede crecer sin freno
 * ni borrarse selectivamente. Es lo contrario de la bitácora de negocio,
 * que es permanente e inmutable.
 *
 * RNF34 prohíbe registrar contraseñas, tokens completos o datos
 * personales innecesarios. El validador rechaza los campos prohibidos de
 * forma explícita en lugar de confiar en que nadie los escriba.
 * ------------------------------------------------------------------- */
db.createCollection("logs_tecnicos", {
  capped: true,
  size: 536870912,        // 512 MB
  max: 2000000,           // 2 millones de documentos
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["nivel", "componente", "mensaje", "registrado_en"],
      properties: {
        nivel: { enum: ["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"] },
        componente: { bsonType: "string", description: "RNF35: componente de origen para correlacionar fallas." },
        registrado_en: { bsonType: "date" },
        correlacion_id: { bsonType: "string", description: "Mismo id a lo largo de una petición entre servicios." },
        mensaje: { bsonType: "string" },
        excepcion: { bsonType: ["object", "null"] },
        contexto: { bsonType: ["object", "null"] },
        usuario_id: { bsonType: ["int", "null"] },
        ruta: { bsonType: ["string", "null"] },
        duracion_ms: { bsonType: ["int", "null"] },
        // RNF34: campos prohibidos. Declararlos con bsonType "null" hace
        // que cualquier intento de escribir un valor sea rechazado.
        contrasena: { bsonType: "null" },
        token: { bsonType: "null" },
        hash_contrasena: { bsonType: "null" }
      }
    }
  },
  validationAction: "error"
});

db.logs_tecnicos.createIndex({ registrado_en: -1 }, { name: "ix_fecha" });
db.logs_tecnicos.createIndex({ nivel: 1, componente: 1, registrado_en: -1 }, { name: "ix_nivel_comp" });
db.logs_tecnicos.createIndex({ correlacion_id: 1 }, { name: "ix_correlacion", sparse: true });

/* ---------------------------------------------------------------------
 * 5. sincronizaciones_moviles — RNF17, CU05 A4, HU32 CA2
 * Cola de operaciones que el Repartidor registró sin conexión y los
 * conflictos detectados al sincronizar.
 *
 * CU05 A4 es tajante: la sincronización NO sobrescribe en silencio. Un
 * conflicto se conserva para resolución y trazabilidad, y por eso existe
 * el estado "conflicto" en lugar de simplemente aplicar el último cambio.
 *
 * `operacion_uuid` es único: es lo que impide que un reintento del móvil
 * duplique un cierre de entrega (HU32 CA2).
 * ------------------------------------------------------------------- */
db.createCollection("sincronizaciones_moviles", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["operacion_uuid", "dispositivo_id", "usuario_id", "tipo_operacion",
                 "capturado_en", "estado"],
      properties: {
        operacion_uuid: { bsonType: "string", description: "Idempotencia: generado en el dispositivo." },
        dispositivo_id: { bsonType: "string" },
        usuario_id: { bsonType: "int" },
        tipo_operacion: { enum: ["cierre_entrega", "entrega_parcial", "entrega_fallida",
                                 "incidencia", "escaneo_pedido"] },
        pedido_id: { bsonType: ["long", "null"] },
        capturado_en: { bsonType: "date", description: "Hora del dispositivo." },
        sincronizado_en: { bsonType: ["date", "null"], description: "Hora del servidor." },
        estado: { enum: ["pendiente", "aplicada", "conflicto", "rechazada"] },
        carga: { bsonType: "object" },
        conflicto: {
          bsonType: ["object", "null"],
          description: "CU05 A4: se conserva el evento en lugar de sobrescribir.",
          properties: {
            motivo: { bsonType: "string" },
            estado_servidor: { bsonType: "string" },
            estado_dispositivo: { bsonType: "string" },
            resuelto_por: { bsonType: ["int", "null"] },
            resuelto_en: { bsonType: ["date", "null"] }
          }
        }
      }
    }
  }
});

db.sincronizaciones_moviles.createIndex({ operacion_uuid: 1 }, { name: "ix_uuid", unique: true });
db.sincronizaciones_moviles.createIndex({ estado: 1, capturado_en: 1 }, { name: "ix_pendientes" });
db.sincronizaciones_moviles.createIndex({ usuario_id: 1, capturado_en: -1 }, { name: "ix_usuario" });
db.sincronizaciones_moviles.createIndex({ pedido_id: 1 }, { name: "ix_pedido", sparse: true });

/* ---------------------------------------------------------------------
 * 6. metricas_servicio — RF49, RNF36
 * Serie temporal con expiración automática: las métricas operativas
 * pierden valor rápido y no deben crecer para siempre.
 * ------------------------------------------------------------------- */
db.createCollection("metricas_servicio", {
  timeseries: { timeField: "momento", metaField: "etiquetas", granularity: "minutes" },
  expireAfterSeconds: 7776000   // 90 días
});

db.metricas_servicio.createIndex({ "etiquetas.servicio": 1, momento: -1 }, { name: "ix_servicio" });

/* ---------------------------------------------------------------------
 * Resumen
 * ------------------------------------------------------------------- */
print("Base: " + BD);
db.getCollectionNames().sort().forEach(function (c) {
  const n = db.getCollection(c).getIndexes().length;
  print("  " + c.padEnd(28) + " índices: " + n);
});
