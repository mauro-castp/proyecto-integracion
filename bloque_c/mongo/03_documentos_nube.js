/* =====================================================================
 * 03_documentos_nube.js — Esquema de `documentos` para los archivos en Google Cloud Storage.
 *
 * Para un volumen de MongoDB que ya existía (creado con el esquema anterior, que exigía el campo `contenido`): actualiza el validador
 * de la colección con collMod. En una base nueva 02_microservicios.js ya crea el esquema final y esto no cambia nada.
 * Es repetible. Para correrlo a mano:
 *
 *   docker compose exec -T mongo mongosh --quiet < bloque_c/mongo/03_documentos_nube.js
 * ===================================================================== */

db = db.getSiblingDB("microhubs_eventos");

const existe = db.getCollectionNames().includes("documentos");
if (existe) {
  db.runCommand({
    collMod: "documentos",
    validator: {
      $jsonSchema: {
        bsonType: "object",
        required: ["nombre", "tipo_mime", "tamano_bytes", "sha256", "referencia", "subido_por", "creado_en"],
        properties: {
          nombre: { bsonType: "string", maxLength: 160 },
          tipo_mime: { enum: ["image/jpeg", "image/png", "application/pdf"] },
          tamano_bytes: { bsonType: ["int", "long"], minimum: 1, maximum: 5242880 },
          sha256: { bsonType: "string", minLength: 64, maxLength: 64 },
          referencia: {
            bsonType: "object", required: ["tipo", "id"],
            properties: { tipo: { enum: ["entrega", "pedido", "usuario", "candidato", "orden_compra"] }, id: { bsonType: "string" } }
          },
          subido_por: { bsonType: "int" },
          creado_en: { bsonType: "date" },
          contenido: { bsonType: "binData" },
          ruta: { bsonType: "string", maxLength: 300 },
          privacidad: { enum: ["privado", "interno"] },
          estado: { enum: ["activo", "eliminado"] },
          eliminado_en: { bsonType: "date" },
          metadatos: {
            bsonType: "object",
            properties: { almacen: { enum: ["gcs", "local", "mongodb"] }, origen: { enum: ["api", "web", "movil", "escritorio"] } }
          }
        }
      }
    }
  });
  print("documentos: validador actualizado (archivos en el bucket, el contenido ya no es obligatorio).");
} else {
  print("documentos: la colección aún no existe; la creará 02_microservicios.js con el esquema final.");
}
db.documentos.createIndex({ estado: 1, creado_en: -1 }, { name: "ix_estado" });
db.documentos.createIndex({ ruta: 1 }, { name: "ix_ruta", sparse: true });
