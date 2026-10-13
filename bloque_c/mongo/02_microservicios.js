/* =====================================================================
 * 02_microservicios.js — Colecciones que agregan los microservicios
 * Plataforma de Microhubs · Codex Innovations · Equipo 04 · Segundo Parcial
 *
 *   mongosh "mongodb://localhost:27017/microhubs_eventos" 02_microservicios.js
 *
 * Docker lo ejecuta en el primer arranque (docker-entrypoint-initdb.d).
 * Con un volumen existente, los servicios crean los índices al iniciar
 * (servicios/comun/datos.py) y las colecciones se crean al primer insert.
 *
 * documentos           — evidencias de entrega y archivos (servicio 5107).
 *                        Binario de hasta 5 MB dentro del documento: muy por
 *                        debajo del límite de 16 MB de BSON, sin GridFS.
 * ubicaciones_entrega  — puntos GPS del recorrido del repartidor (5105).
 *                        Alta frecuencia y esquema simple: no pertenecen a
 *                        PostgreSQL. Índice 2dsphere para consultas espaciales.
 * ===================================================================== */

db = db.getSiblingDB("microhubs_eventos");

db.createCollection("documentos", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["nombre", "tipo_mime", "tamano_bytes", "sha256", "referencia", "subido_por", "creado_en", "contenido"],
      properties: {
        nombre: { bsonType: "string", maxLength: 160 },
        tipo_mime: { enum: ["image/jpeg", "image/png", "application/pdf"] },
        tamano_bytes: { bsonType: ["int", "long"], minimum: 1, maximum: 5242880 },
        sha256: { bsonType: "string", minLength: 64, maxLength: 64 },
        referencia: {
          bsonType: "object", required: ["tipo", "id"],
          properties: { tipo: { enum: ["entrega", "pedido", "usuario", "candidato"] }, id: { bsonType: "string" } }
        },
        subido_por: { bsonType: "int" },
        creado_en: { bsonType: "date" },
        contenido: { bsonType: "binData" }
      }
    }
  }
});
db.documentos.createIndex({ "referencia.tipo": 1, "referencia.id": 1 }, { name: "ix_referencia" });
db.documentos.createIndex({ subido_por: 1, creado_en: -1 }, { name: "ix_autor" });
db.documentos.createIndex({ sha256: 1 }, { name: "ix_sha256" });

db.createCollection("ubicaciones_entrega", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["entrega_id", "usuario_id", "posicion", "capturado_en", "recibido_en"],
      properties: {
        entrega_id: { bsonType: "long" },
        usuario_id: { bsonType: "int" },
        posicion: {
          bsonType: "object", required: ["type", "coordinates"],
          properties: { type: { enum: ["Point"] }, coordinates: { bsonType: "array", minItems: 2, maxItems: 2 } }
        },
        precision_m: { bsonType: ["double", "null"] },
        capturado_en: { bsonType: "date" },
        recibido_en: { bsonType: "date" }
      }
    }
  }
});
db.ubicaciones_entrega.createIndex({ entrega_id: 1, capturado_en: 1 }, { name: "ix_entrega_tiempo" });
db.ubicaciones_entrega.createIndex({ posicion: "2dsphere" }, { name: "ix_posicion" });
// Los recorridos pierden valor operativo con el tiempo: se conservan 180 días.
db.ubicaciones_entrega.createIndex({ recibido_en: 1 }, { name: "ix_ttl", expireAfterSeconds: 15552000 });

print("Colecciones de microservicios listas: documentos, ubicaciones_entrega");
