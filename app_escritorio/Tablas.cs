using System.Data;
using System.Globalization;
using System.Xml.Linq;

namespace Microhubs;

/// <summary>
/// Convierte las respuestas XML del contrato en las tablas que ve la persona. No depende de Windows Forms (se prueba en cualquier
/// sistema): las ventanas solo asignan el resultado a un DataGridView.
/// </summary>
static class Tablas
{
    static XNamespace Ns => Api.Ns;

    /// <summary>Convierte una lista del contrato (datos + paginacion) en la tabla que ve la persona.</summary>
    internal static DataTable ToTable(XDocument list) => Filas(list.Root!.Element(Ns + "datos")!.Elements());

    /// <summary>Hojas de un elemento como «ruta/hoja» → valor; las que se repiten se unen con «; ».</summary>
    internal static Dictionary<string, string> Flatten(XElement row) => row.Descendants().Where(e => !e.HasElements)
        .GroupBy(e => string.Join("/", e.Ancestors().TakeWhile(a => a != row).Reverse().Select(a => a.Name.LocalName).Append(e.Name.LocalName)))
        .ToDictionary(g => g.Key, g => string.Join("; ", g.Select(e => e.Value)));

    static DataTable Filas(IEnumerable<XElement> elementos)
    {
        var rows = elementos.Select(Flatten).ToList(); var table = new DataTable();
        foreach (var col in rows.SelectMany(r => r.Keys).Distinct()) table.Columns.Add(col);
        foreach (var row in rows) { var item = table.NewRow(); foreach (var cell in row) item[cell.Key] = cell.Value; table.Rows.Add(item); }
        return table;
    }

    /// <summary>
    /// La colección principal de una respuesta: `datos` si es una lista paginada; si no, el hijo directo con más elementos
    /// repetidos (p. ej. las rutas de un plan, los pasos de un cálculo, las filas de una sensibilidad). Los supuestos usados solo son la
    /// colección principal si no hay otra (una comparación de rutas trae 4 métodos y 6 supuestos: la tabla son los métodos). Null si no hay ninguna.
    /// </summary>
    internal static XElement? Coleccion(XDocument doc)
    {
        var root = doc.Root!;
        if (root.Element(Ns + "datos") is { } datos) return datos;
        return root.Elements()
            .Where(e => e.HasElements && e.Elements().All(h => h.Name == e.Elements().First().Name) && e.Elements().First().HasElements)
            .OrderBy(e => e.Name == Ns + "supuestos_usados")           // los supuestos van al resumen salvo que sean lo único que hay
            .ThenByDescending(e => e.Elements().Count())
            .FirstOrDefault();
    }

    /// <summary>La tabla principal de cualquier respuesta: su colección o, si no tiene, campo → valor.</summary>
    internal static DataTable Principal(XDocument doc)
    {
        if (doc.Root!.Name == Ns + "reporte") return Reporte(doc);
        if (doc.Root.Name == Ns + "grafica") return Grafica(doc);
        var c = Coleccion(doc);
        return c != null ? Filas(c.Elements()) : CampoValor(Flatten(doc.Root));
    }

    /// <summary>Todo lo que no está en la colección principal (totales, decisión, supuestos usados…), como campo → valor.</summary>
    internal static DataTable Resumen(XDocument doc)
    {
        var copia = new XElement(doc.Root!);
        if (doc.Root!.Name == Ns + "reporte") { copia.Element(Ns + "columnas")?.Remove(); copia.Element(Ns + "filas")?.Remove(); copia.Element(Ns + "totales")?.Remove(); }
        else if (doc.Root.Name == Ns + "grafica") { copia.Element(Ns + "categorias")?.Remove(); copia.Element(Ns + "series")?.Remove(); }
        else if (Coleccion(doc) is { } c) copia.Element(c.Name)?.Remove();
        else return CampoValor(new Dictionary<string, string>());
        return CampoValor(Flatten(copia));
    }

    internal static DataTable CampoValor(Dictionary<string, string> datos)
    {
        var t = new DataTable(); t.Columns.Add("campo"); t.Columns.Add("valor");
        foreach (var (k, v) in datos) t.Rows.Add(k, v);
        return t;
    }

    /// <summary>Un reporte (GET /reportes/{clave}): una columna por cada &lt;columna&gt; con su título, una fila por &lt;fila&gt; y al final los totales.</summary>
    internal static DataTable Reporte(XDocument doc)
    {
        var r = doc.Root!; var t = new DataTable();
        var titulos = r.Element(Ns + "columnas")!.Elements(Ns + "columna").Select(c => c.Element(Ns + "titulo")!.Value).ToList();
        foreach (var titulo in titulos) t.Columns.Add(Unico(t, titulo));
        void Agregar(XElement celdas)
        {
            var valores = celdas.Elements(Ns + "celda").Select(c => (object)c.Value).ToArray();
            if (valores.Length != titulos.Count) throw new Exception($"El reporte trae {valores.Length} celdas en una fila y {titulos.Count} columnas.");
            t.Rows.Add(valores);
        }
        foreach (var fila in r.Element(Ns + "filas")?.Elements(Ns + "fila") ?? []) Agregar(fila.Element(Ns + "celdas")!);
        if (r.Element(Ns + "totales")?.Element(Ns + "celdas") is { } tot) Agregar(tot);
        return t;
    }

    /// <summary>Datos de una gráfica (GET /reportes/{clave}/grafica): una fila por categoría y una columna por serie.</summary>
    internal static DataTable Grafica(XDocument doc)
    {
        var r = doc.Root!; var t = new DataTable(); t.Columns.Add("categoría");
        var categorias = r.Element(Ns + "categorias")!.Elements().Select(c => c.Value).ToList();
        var series = r.Element(Ns + "series")!.Elements(Ns + "serie").ToList();
        foreach (var s in series) t.Columns.Add(Unico(t, s.Element(Ns + "nombre")!.Value));
        for (var i = 0; i < categorias.Count; i++)
            t.Rows.Add(new object[] { categorias[i] }.Concat(series.Select(s => (object)(s.Element(Ns + "datos")!.Elements().ElementAtOrDefault(i)?.Value ?? ""))).ToArray());
        return t;
    }

    static string Unico(DataTable t, string nombre) { var n = nombre; for (var i = 2; t.Columns.Contains(n); i++) n = $"{nombre} ({i})"; return n; }

    /// <summary>Los filtros que admite un reporte, según el catálogo (GET /reportes). Un reporte rechaza (400) los que no admite.</summary>
    internal static HashSet<string> FiltrosDe(XDocument catalogo, string clave) =>
        catalogo.Descendants(Ns + "reporte").FirstOrDefault(r => r.Element(Ns + "clave")?.Value == clave)?.Element(Ns + "filtros")?.Elements().Select(f => f.Value).ToHashSet()
        ?? throw new Exception($"El reporte {clave} no está en el catálogo.");

    /// <summary>
    /// Consulta de un reporte: desde y hasta (AAAA-MM-DD), zona y microhub solo si se indicaron y, si se pasa `admitidos`, solo los que
    /// ese reporte admite (los demás se omiten en lugar de provocar un 400).
    /// </summary>
    internal static string ConsultaReporte(string clave, string sufijo, DateTime? desde, DateTime? hasta, int? zona, int? microhub, string? formato = null,
                                           ISet<string>? admitidos = null)
    {
        if (!System.Text.RegularExpressions.Regex.IsMatch(clave, "^[a-z_]{3,60}$")) throw new Exception("Clave de reporte no válida.");
        if (desde > hasta) throw new Exception("«Desde» no puede ser posterior a «hasta».");
        bool Admite(string f) => admitidos == null || admitidos.Contains(f);
        var q = new List<string>();
        if (desde is { } d && Admite("desde")) q.Add("desde=" + d.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture));
        if (hasta is { } h && Admite("hasta")) q.Add("hasta=" + h.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture));
        if (zona is { } z && Admite("zona_id")) q.Add("zona_id=" + z);
        if (microhub is { } m && Admite("microhub_id")) q.Add("microhub_id=" + m);
        if (formato != null) q.Add("formato=" + formato);
        return $"reportes/{clave}{sufijo}" + (q.Count > 0 ? "?" + string.Join("&", q) : "");
    }
}
