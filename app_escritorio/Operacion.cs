using System.Data;
using System.Globalization;
using System.Net;
using System.Text;
using System.Xml.Linq;

namespace Microhubs;

/// <summary>
/// Lo que el operador arma en el escritorio sin plantilla: la asignación de pedidos listos a un repartidor y el manifiesto de salida de un
/// repartidor (sus paradas en orden, con cliente, dirección, productos y lo que hay que cobrar). Sin Windows Forms: se prueba en cualquier sistema.
/// </summary>
static class Operacion
{
    static XNamespace Ns => Api.Ns;

    /// <summary>Ids positivos separados por coma («121, 122»). Lanza un error legible si alguno no es número o se repite.</summary>
    public static List<long> Ids(string texto, string que)
    {
        var ids = new List<long>();
        foreach (var parte in texto.Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries))
        {
            if (!long.TryParse(parte, NumberStyles.None, CultureInfo.InvariantCulture, out var id) || id < 1) throw new Exception($"{que}: «{parte}» no es un id.");
            if (ids.Contains(id)) throw new Exception($"{que}: el {id} está repetido.");
            ids.Add(id);
        }
        if (ids.Count == 0) throw new Exception($"{que}: escribe al menos un id.");
        return ids;
    }

    /// <summary>Cuerpo &lt;asignacion_nueva&gt;: los pedidos en el orden escrito, todos al mismo repartidor (parada 1, 2, 3…).</summary>
    public static XElement Asignacion(string pedidos, string repartidor)
    {
        var ids = Ids(pedidos, "Pedidos");
        if (ids.Count > 200) throw new Exception("Pedidos: a lo más 200 por asignación.");
        var rep = Ids(repartidor, "Repartidor");
        if (rep.Count != 1) throw new Exception("Repartidor: escribe un solo id.");
        return new XElement(Ns + "asignacion_nueva", new XElement(Ns + "paradas", ids.Select((id, i) =>
            new XElement(Ns + "parada", new XElement(Ns + "pedido_id", id), new XElement(Ns + "repartidor_id", rep[0]), new XElement(Ns + "orden_parada", i + 1)))));
    }

    static string Texto(XElement? e, string hijo) => e?.Element(Ns + hijo) is { } h && h.Attribute(XName.Get("nil", "http://www.w3.org/2001/XMLSchema-instance"))?.Value != "true" ? h.Value : "";

    /// <summary>Manifiesto a partir del detalle de cada entrega (&lt;entrega_detalle&gt;), ordenado por parada.</summary>
    public static DataTable Manifiesto(IEnumerable<XDocument> detalles)
    {
        var t = new DataTable();
        foreach (var c in new[] { "parada", "folio", "cliente", "telefono", "direccion", "productos", "piezas", "total_a_cobrar" }) t.Columns.Add(c);
        var filas = detalles.Select(d => d.Root!).OrderBy(r => int.TryParse(Texto(r, "orden_parada"), out var o) ? o : int.MaxValue);
        foreach (var r in filas)
        {
            var dom = r.Element(Ns + "domicilio");
            var direccion = string.Join(", ", new[] { $"{Texto(dom, "calle")} {Texto(dom, "numero_ext")}".Trim(), Texto(dom, "colonia") }.Where(x => x != ""));
            var lineas = r.Element(Ns + "lineas")?.Elements(Ns + "linea").ToList() ?? new();
            var piezas = lineas.Sum(l => int.TryParse(Texto(l, "cantidad"), out var n) ? n : 0);
            t.Rows.Add(Texto(r, "orden_parada"), Texto(r, "folio"), Texto(r.Element(Ns + "cliente"), "nombre"), Texto(r.Element(Ns + "cliente"), "telefono"),
                       direccion, string.Join("; ", lineas.Select(l => $"{Texto(l, "cantidad")} × {Texto(l, "nombre")}")), piezas,
                       decimal.TryParse(Texto(r, "total"), NumberStyles.Number, CultureInfo.InvariantCulture, out var tot) ? tot.ToString("0.00", CultureInfo.InvariantCulture) : "");
        }
        return t;
    }

    public static decimal TotalACobrar(DataTable manifiesto) =>
        manifiesto.Rows.Cast<DataRow>().Sum(r => decimal.TryParse((string)r["total_a_cobrar"], NumberStyles.Number, CultureInfo.InvariantCulture, out var v) ? v : 0);

    /// <summary>Página HTML imprimible (el navegador la guarda como PDF). Todo el texto va escapado.</summary>
    public static string ManifiestoHtml(DataTable manifiesto, string repartidor, DateTime generado)
    {
        static string E(object? v) => WebUtility.HtmlEncode(v?.ToString() ?? "");
        var sb = new StringBuilder();
        sb.Append("<!DOCTYPE html><html lang=\"es\"><head><meta charset=\"utf-8\"><title>Manifiesto de salida</title><style>")
          .Append("body{font:13px Segoe UI,Arial,sans-serif;margin:24px}h1{font-size:20px;margin:0 0 4px}table{border-collapse:collapse;width:100%;margin-top:12px}")
          .Append("th,td{border:1px solid #999;padding:4px 6px;text-align:left;vertical-align:top}th{background:#eee}td.n{text-align:right}")
          .Append(".firma{margin-top:40px;display:flex;gap:80px}.firma div{border-top:1px solid #000;padding-top:4px;width:240px}</style></head><body>")
          .Append($"<h1>Manifiesto de salida</h1><div>Repartidor: <b>{E(repartidor)}</b> · Generado: {E(generado.ToString("yyyy-MM-dd HH:mm", CultureInfo.InvariantCulture))}")
          .Append($" · Paradas: {manifiesto.Rows.Count} · Total a cobrar: <b>${TotalACobrar(manifiesto).ToString("#,0.00", CultureInfo.InvariantCulture)}</b></div>")
          .Append("<table><tr><th>Parada</th><th>Folio</th><th>Cliente</th><th>Teléfono</th><th>Dirección</th><th>Productos</th><th>Piezas</th><th>A cobrar</th><th>Entregado</th></tr>");
        foreach (DataRow r in manifiesto.Rows)
            sb.Append($"<tr><td class=\"n\">{E(r["parada"])}</td><td>{E(r["folio"])}</td><td>{E(r["cliente"])}</td><td>{E(r["telefono"])}</td><td>{E(r["direccion"])}</td>")
              .Append($"<td>{E(r["productos"])}</td><td class=\"n\">{E(r["piezas"])}</td><td class=\"n\">{E(r["total_a_cobrar"])}</td><td></td></tr>");
        sb.Append("</table><div class=\"firma\"><div>Entregó (operador)</div><div>Recibió (repartidor)</div></div></body></html>");
        return sb.ToString();
    }
}
