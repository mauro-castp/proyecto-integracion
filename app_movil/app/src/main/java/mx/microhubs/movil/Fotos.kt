package mx.microhubs.movil

import android.content.ContentProvider
import android.content.ContentValues
import android.database.Cursor
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Matrix
import android.media.ExifInterface
import android.net.Uri
import android.os.ParcelFileDescriptor
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.FileNotFoundException
import kotlin.math.max

/**
 * Entrega a la app de cámara un archivo de la caché de la app donde guardar la foto a resolución completa
 * (la miniatura que devuelve la cámara por defecto no sirve como evidencia). Solo sirve archivos .jpg de la carpeta cache/fotos de la app.
 */
class FotoProvider : ContentProvider() {
    override fun onCreate() = true

    private fun archivo(uri: Uri): File {
        val nombre = uri.lastPathSegment ?: throw FileNotFoundException()
        if (!Regex("[A-Za-z0-9_.-]+\\.jpg").matches(nombre)) throw FileNotFoundException()
        return File(File(context!!.cacheDir, "fotos"), nombre)
    }

    override fun openFile(uri: Uri, mode: String): ParcelFileDescriptor =
        ParcelFileDescriptor.open(archivo(uri), ParcelFileDescriptor.parseMode(mode))

    override fun getType(uri: Uri) = "image/jpeg"
    override fun query(uri: Uri, projection: Array<out String>?, selection: String?, selectionArgs: Array<out String>?, sortOrder: String?): Cursor? = null
    override fun insert(uri: Uri, values: ContentValues?): Uri? = null
    override fun delete(uri: Uri, selection: String?, selectionArgs: Array<out String>?) = 0
    override fun update(uri: Uri, values: ContentValues?, selection: String?, selectionArgs: Array<out String>?) = 0
}

object Fotos {
    const val MAXIMO_BYTES = 4_500_000          // el servicio de documentos acepta hasta 5 MB

    /** Lee la foto de la cámara, la endereza según EXIF, limita el lado mayor y devuelve un JPEG que cabe en el límite del servicio. */
    fun preparar(archivo: File, ladoMax: Int = 1600): ByteArray {
        val limites = BitmapFactory.Options().apply { inJustDecodeBounds = true }
        BitmapFactory.decodeFile(archivo.path, limites)
        var muestra = 1
        while (max(limites.outWidth, limites.outHeight) / muestra > ladoMax * 2) muestra *= 2
        val original = BitmapFactory.decodeFile(archivo.path, BitmapFactory.Options().apply { inSampleSize = muestra })
            ?: throw IllegalArgumentException("La cámara no devolvió una imagen legible.")
        val grados = when (ExifInterface(archivo.path).getAttributeInt(ExifInterface.TAG_ORIENTATION, ExifInterface.ORIENTATION_NORMAL)) {
            ExifInterface.ORIENTATION_ROTATE_90 -> 90f
            ExifInterface.ORIENTATION_ROTATE_180 -> 180f
            ExifInterface.ORIENTATION_ROTATE_270 -> 270f
            else -> 0f
        }
        val escala = minOf(1f, ladoMax.toFloat() / max(original.width, original.height))
        val m = Matrix().apply { postRotate(grados); postScale(escala, escala) }
        val imagen = Bitmap.createBitmap(original, 0, 0, original.width, original.height, m, true)
        return comprimir(imagen)
    }

    fun comprimir(imagen: Bitmap): ByteArray {
        var calidad = 80
        while (true) {
            val salida = ByteArrayOutputStream()
            imagen.compress(Bitmap.CompressFormat.JPEG, calidad, salida)
            if (salida.size() <= MAXIMO_BYTES || calidad <= 40) return salida.toByteArray()
            calidad -= 10
        }
    }
}
