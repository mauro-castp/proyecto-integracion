package mx.microhubs.movil

import android.app.Activity
import android.content.Context
import android.content.res.ColorStateList
import android.content.res.Configuration
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.Drawable
import android.graphics.drawable.GradientDrawable
import android.graphics.drawable.RippleDrawable
import android.os.Build
import android.text.InputType
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.view.WindowInsets
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.ScrollView
import android.widget.TextView
import kotlin.math.roundToInt

enum class Tipo { PRIMARIO, SECUNDARIO, PELIGRO, TEXTO }
enum class Mensaje { ERROR, EXITO, INFO }
enum class Red { EN_LINEA, SIN_RED, EJEMPLOS }

/** Colores, formas y componentes de la interfaz. Todo se arma en código (sin AppCompat) y respeta el modo oscuro del sistema. */
class Estilo(val ctx: Context) {
    val noche = (ctx.resources.configuration.uiMode and Configuration.UI_MODE_NIGHT_MASK) == Configuration.UI_MODE_NIGHT_YES
    private fun c(dia: Long, oscuro: Long) = (if (noche) oscuro else dia).toInt()

    val primario = c(0xFF0F766E, 0xFF14B8A6)
    val barra = c(0xFF0F766E, 0xFF0B3B38)
    val fondo = c(0xFFF3F5F7, 0xFF0F1416)
    val superficie = c(0xFFFFFFFF, 0xFF1B2428)
    val borde = c(0xFFE1E6EA, 0xFF2B373D)
    val tinta = c(0xFF1F2937, 0xFFE8EEF1)
    val tintaSec = c(0xFF5B6770, 0xFF9FB0B8)
    val ok = c(0xFF15803D, 0xFF4ADE80)
    val alerta = c(0xFFB45309, 0xFFFBBF24)
    val peligro = c(0xFFB91C1C, 0xFFF87171)
    val info = c(0xFF1D4ED8, 0xFF60A5FA)

    fun dp(v: Int) = (v * ctx.resources.displayMetrics.density).roundToInt()

    fun forma(color: Int, radio: Int = 12, trazo: Int? = null): GradientDrawable = GradientDrawable().apply {
        setColor(color); cornerRadius = dp(radio).toFloat(); if (trazo != null) setStroke(dp(1), trazo)
    }

    private fun conOnda(contenido: Drawable): Drawable =
        RippleDrawable(ColorStateList.valueOf(if (noche) 0x33FFFFFF else 0x1F000000), contenido, null)

    private fun tinte(color: Int, alfa: Int = 0x26) = (color and 0x00FFFFFF) or (alfa shl 24)

    // ------------------------------------------------------------------ componentes
    fun texto(contenido: CharSequence, tam: Float = 15f, color: Int = tinta, negrita: Boolean = false): TextView = TextView(ctx).apply {
        text = contenido; textSize = tam; setTextColor(color)
        if (negrita) typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
        layoutParams = LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT)
    }

    fun titulo(contenido: CharSequence) = texto(contenido, 13f, tintaSec, true).apply {
        isAllCaps = true; letterSpacing = 0.06f
        (layoutParams as LinearLayout.LayoutParams).apply { topMargin = dp(8); bottomMargin = dp(6) }
    }

    fun etiqueta(contenido: CharSequence) = texto(contenido, 13f, tintaSec, true).apply {
        (layoutParams as LinearLayout.LayoutParams).apply { topMargin = dp(12); bottomMargin = dp(4) }
    }

    fun chip(contenido: CharSequence, color: Int): TextView = TextView(ctx).apply {
        text = contenido; textSize = 12f; setTextColor(color); typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
        setPadding(dp(10), dp(4), dp(10), dp(4)); background = forma(tinte(color), 20)
        layoutParams = LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT)
    }

    fun tarjeta(clic: (() -> Unit)? = null): LinearLayout = LinearLayout(ctx).apply {
        orientation = LinearLayout.VERTICAL
        setPadding(dp(16), dp(14), dp(16), dp(14))
        val base = forma(superficie, 16, borde)
        background = if (clic != null) conOnda(base) else base
        elevation = dp(1).toFloat()
        layoutParams = LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT).apply { bottomMargin = dp(12) }
        if (clic != null) { isClickable = true; isFocusable = true; setOnClickListener { clic() } }
    }

    fun fila(vararg vistas: View, centrada: Boolean = true): LinearLayout = LinearLayout(ctx).apply {
        orientation = LinearLayout.HORIZONTAL
        if (centrada) gravity = Gravity.CENTER_VERTICAL
        layoutParams = LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT)
        vistas.forEach { addView(it) }
    }

    /** Ocupa el espacio sobrante de una fila (peso 1). */
    fun flexible(v: View): View = v.apply { layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f) }

    fun boton(contenido: String, tipo: Tipo = Tipo.SECUNDARIO, accion: () -> Unit): Button = Button(ctx).apply {
        text = contenido; isAllCaps = false; textSize = 15f; typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
        minHeight = dp(48); minimumHeight = dp(48); stateListAnimator = null; elevation = 0f
        setPadding(dp(16), 0, dp(16), 0)
        when (tipo) {
            Tipo.PRIMARIO -> { background = conOnda(forma(primario, 12)); setTextColor(Color.WHITE) }
            Tipo.SECUNDARIO -> { background = conOnda(forma(superficie, 12, primario)); setTextColor(primario) }
            Tipo.PELIGRO -> { background = conOnda(forma(superficie, 12, peligro)); setTextColor(peligro) }
            Tipo.TEXTO -> { background = conOnda(forma(Color.TRANSPARENT, 12)); setTextColor(primario) }
        }
        layoutParams = LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT).apply { topMargin = dp(8) }
        setOnClickListener { accion() }
    }

    /** Botón de ancho ajustado al texto (acciones dentro de una fila). */
    fun botonCompacto(contenido: String, tipo: Tipo = Tipo.SECUNDARIO, accion: () -> Unit): Button = boton(contenido, tipo, accion).apply {
        minHeight = dp(44); minimumHeight = dp(44); setPadding(dp(14), 0, dp(14), 0)
        layoutParams = LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, dp(44))
    }

    /** Selector de una opción entre pocas (entregado / parcial / fallida). `cambio` recibe el valor interno. */
    fun segmentos(opciones: List<Pair<String, String>>, inicial: String, cambio: (String) -> Unit): LinearLayout {
        var actual = inicial
        val botones = mutableListOf<Button>()
        fun pintar() = botones.forEachIndexed { i, b ->
            val sel = opciones[i].first == actual
            b.background = if (sel) forma(primario, 10) else forma(superficie, 10, borde)
            b.setTextColor(if (sel) Color.WHITE else tinta)
            b.isSelected = sel
        }
        val fila = LinearLayout(ctx).apply {
            orientation = LinearLayout.HORIZONTAL
            layoutParams = LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT)
        }
        opciones.forEachIndexed { i, (valor, rotulo) ->
            val b = Button(ctx).apply {
                text = rotulo; isAllCaps = false; textSize = 14f; typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
                minHeight = dp(44); minimumHeight = dp(44); stateListAnimator = null; elevation = 0f; setPadding(dp(4), 0, dp(4), 0)
                layoutParams = LinearLayout.LayoutParams(0, dp(44), 1f).apply { if (i > 0) marginStart = dp(6) }
                setOnClickListener { actual = valor; pintar(); cambio(valor) }
            }
            botones.add(b); fila.addView(b)
        }
        pintar()
        return fila
    }

    fun campo(pista: String, valor: String = "", numerico: Boolean = false, secreto: Boolean = false, entero: Boolean = false): EditText = EditText(ctx).apply {
        hint = pista; setText(valor); textSize = 16f; setTextColor(tinta); setHintTextColor(tintaSec)
        setPadding(dp(14), dp(12), dp(14), dp(12)); minHeight = dp(48)
        background = forma(superficie, 12, borde)
        inputType = when {
            secreto -> InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_PASSWORD
            numerico -> InputType.TYPE_CLASS_NUMBER or InputType.TYPE_NUMBER_FLAG_DECIMAL
            entero -> InputType.TYPE_CLASS_NUMBER
            else -> InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_FLAG_CAP_SENTENCES
        }
        layoutParams = LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT)
    }

    fun circulo(contenido: String, color: Int, tam: Int = 40): TextView = TextView(ctx).apply {
        text = contenido; textSize = 15f; setTextColor(Color.WHITE); gravity = Gravity.CENTER
        typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
        background = GradientDrawable().apply { shape = GradientDrawable.OVAL; setColor(color) }
        layoutParams = LinearLayout.LayoutParams(dp(tam), dp(tam)).apply { marginEnd = dp(12) }
    }

    fun espacio(alto: Int) = View(ctx).apply { layoutParams = LinearLayout.LayoutParams(1, dp(alto)) }

    /** Color y texto legible de cada estado del pedido. */
    fun estado(estado: String): Pair<String, Int> = when (estado) {
        "en_ruta" -> "En ruta" to info
        "entregado" -> "Entregado" to ok
        "entrega_parcial" -> "Entrega parcial" to alerta
        "entrega_fallida" -> "Entrega fallida" to peligro
        "en_preparacion" -> "En preparación" to info
        "asignado" -> "Asignado" to info
        "cancelado" -> "Cancelado" to peligro
        else -> estado.replace('_', ' ').replaceFirstChar { it.uppercase() } to tintaSec
    }
}

/** Una pantalla: barra superior con título e indicador de conexión, aviso, progreso, contenido con scroll y pie opcional. */
class Pantalla(val e: Estilo, private val activity: Activity, titulo: String, subtitulo: String? = null, atras: (() -> Unit)? = null) {
    val raiz = LinearLayout(activity).apply { orientation = LinearLayout.VERTICAL; setBackgroundColor(e.fondo) }
    val contenido = LinearLayout(activity).apply { orientation = LinearLayout.VERTICAL; setPadding(e.dp(16), e.dp(16), e.dp(16), e.dp(24)) }
    val scroll = ScrollView(activity).apply { isFillViewport = true; addView(contenido) }
    val pie = LinearLayout(activity).apply {
        orientation = LinearLayout.VERTICAL; visibility = View.GONE; elevation = e.dp(6).toFloat()
        setBackgroundColor(e.superficie); setPadding(e.dp(16), e.dp(8), e.dp(16), e.dp(12))
    }
    private val encabezado = LinearLayout(activity).apply {
        orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL; setBackgroundColor(e.barra)
        setPadding(e.dp(8), e.dp(10), e.dp(12), e.dp(10)); elevation = e.dp(4).toFloat()
    }
    private val chipRed = TextView(activity).apply {
        textSize = 12f; typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD); setTextColor(Color.WHITE)
        setPadding(e.dp(10), e.dp(5), e.dp(10), e.dp(5))
    }
    private val progreso = ProgressBar(activity, null, android.R.attr.progressBarStyleHorizontal).apply {
        isIndeterminate = true; visibility = View.GONE
        indeterminateTintList = ColorStateList.valueOf(e.primario)
        layoutParams = LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, e.dp(4))
    }
    private val banner = TextView(activity).apply {
        textSize = 14f; visibility = View.GONE; setPadding(e.dp(16), e.dp(10), e.dp(16), e.dp(10))
        layoutParams = LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT)
    }

    init {
        if (atras != null) {
            encabezado.addView(TextView(activity).apply {
                text = "←"; textSize = 24f; setTextColor(Color.WHITE); gravity = Gravity.CENTER
                contentDescription = "Volver"; isClickable = true; isFocusable = true
                background = RippleDrawable(ColorStateList.valueOf(0x33FFFFFF), null, null)
                layoutParams = LinearLayout.LayoutParams(e.dp(44), e.dp(44))
                setOnClickListener { atras() }
            })
        } else {
            encabezado.setPadding(e.dp(16), e.dp(10), e.dp(12), e.dp(10))
        }
        val textos = LinearLayout(activity).apply {
            orientation = LinearLayout.VERTICAL; layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
            addView(TextView(activity).apply { text = titulo; textSize = 20f; setTextColor(Color.WHITE); typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD); maxLines = 1; ellipsize = android.text.TextUtils.TruncateAt.END })
            if (subtitulo != null) addView(TextView(activity).apply { text = subtitulo; textSize = 13f; setTextColor(0xCCFFFFFF.toInt()); maxLines = 1; ellipsize = android.text.TextUtils.TruncateAt.END })
        }
        encabezado.addView(textos); encabezado.addView(chipRed)
        raiz.addView(encabezado, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT))
        raiz.addView(progreso); raiz.addView(banner)
        raiz.addView(scroll, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f))
        raiz.addView(pie, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT))
        // Android 15 dibuja bajo las barras del sistema: se compensa con sus márgenes.
        raiz.setOnApplyWindowInsetsListener { _, ins ->
            val (arriba, abajo) = if (Build.VERSION.SDK_INT >= 30) ins.getInsets(WindowInsets.Type.systemBars()).let { it.top to it.bottom }
            else @Suppress("DEPRECATION") (ins.systemWindowInsetTop to ins.systemWindowInsetBottom)
            encabezado.setPadding(encabezado.paddingLeft, arriba + e.dp(10), encabezado.paddingRight, e.dp(10))
            pie.setPadding(e.dp(16), e.dp(8), e.dp(16), e.dp(12) + abajo)
            contenido.setPadding(e.dp(16), e.dp(16), e.dp(16), e.dp(24) + if (pie.visibility == View.GONE) abajo else 0)
            ins
        }
    }

    fun mostrar() { activity.setContentView(raiz); raiz.requestApplyInsets() }

    fun ocupado(si: Boolean) { progreso.visibility = if (si) View.VISIBLE else View.GONE }

    fun aviso(texto: String?, tipo: Mensaje = Mensaje.INFO) {
        if (texto.isNullOrBlank()) { banner.visibility = View.GONE; return }
        val color = when (tipo) { Mensaje.ERROR -> e.peligro; Mensaje.EXITO -> e.ok; Mensaje.INFO -> e.info }
        banner.text = texto; banner.setTextColor(color)
        banner.setBackgroundColor((color and 0x00FFFFFF) or (0x1F shl 24))
        banner.visibility = View.VISIBLE
    }

    fun conexion(red: Red) {
        val (texto, color) = when (red) {
            Red.EN_LINEA -> "● En línea" to 0xFF16A34A.toInt()
            Red.SIN_RED -> "● Sin conexión" to 0xFFDC2626.toInt()
            Red.EJEMPLOS -> "● Ejemplos locales" to 0xFFD97706.toInt()
        }
        chipRed.text = texto
        chipRed.background = GradientDrawable().apply { setColor(color); cornerRadius = e.dp(20).toFloat() }
    }

    fun conPie(vararg vistas: View) { pie.removeAllViews(); vistas.forEach { pie.addView(it) }; pie.visibility = View.VISIBLE }

    fun agregar(vararg vistas: View) { vistas.forEach { contenido.addView(it) } }
}
