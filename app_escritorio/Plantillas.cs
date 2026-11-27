using System.Xml.Linq;

namespace Microhubs;

/// <summary>Un campo editable de una plantilla XML: una hoja, o una lista de hojas iguales (p. ej. pedido_ids/id) como «1, 2, 3».</summary>
sealed record Campo(string Clave, string Valor, bool EsLista);

/// <summary>
/// Edición de los cuerpos XML a partir de los ejemplos oficiales, sin Windows Forms (se prueba en cualquier sistema).
/// Las listas de ids se editan separadas por comas y se rearman (vacía = no se manda); un campo nulo (xsi:nil) que recibe un valor deja de ser nulo y uno
/// que se deja vacío vuelve a serlo.
/// </summary>
static class Plantillas
{
    static readonly XNamespace Xsi = "http://www.w3.org/2001/XMLSchema-instance";

    static bool EsLista(XElement e) => e.HasElements && e.Elements().All(h => !h.HasElements && h.Name == e.Elements().First().Name);

    static IEnumerable<XElement> Nodos(XElement raiz)
    {
        foreach (var e in raiz.Elements())
        {
            if (EsLista(e) || !e.HasElements) yield return e;
            else foreach (var h in Nodos(e)) yield return h;
        }
    }

    static string Clave(XElement raiz, XElement e) => string.Join(".", e.AncestorsAndSelf().TakeWhile(a => a != raiz).Reverse().Select(a => a.Name.LocalName));

    public static List<Campo> Campos(XElement raiz) => Nodos(raiz).Select(e => EsLista(e)
        ? new Campo(Clave(raiz, e), string.Join(", ", e.Elements().Select(h => h.Value)), true)
        : new Campo(Clave(raiz, e), e.Value, false)).ToList();

    /// <summary>
    /// Copia de la plantilla con un `operacion_uuid` nuevo en cada operación: el del ejemplo oficial es fijo y, como los servicios son
    /// idempotentes por ese uuid, mandarlo dos veces devolvería el primer movimiento (duplicado) en vez de registrar uno nuevo.
    /// </summary>
    public static XElement ConOperacionNueva(XElement plantilla)
    {
        var copia = new XElement(plantilla);
        foreach (var e in copia.Descendants().Where(e => e.Name.LocalName == "operacion_uuid").ToList()) { e.Value = Guid.NewGuid().ToString(); e.Attribute(Xsi + "nil")?.Remove(); }
        return copia;
    }

    /// <summary>Copia de la plantilla con los valores escritos. No valida: eso lo hace <see cref="Api.Validate"/> antes de enviar.</summary>
    public static XElement Aplicar(XElement plantilla, IReadOnlyDictionary<string, string> valores)
    {
        var copia = new XElement(plantilla);
        foreach (var e in Nodos(copia).ToList())
        {
            if (!valores.TryGetValue(Clave(copia, e), out var valor)) continue;
            valor = valor.Trim();
            if (EsLista(e))
            {
                var nombre = e.Elements().First().Name;
                var items = valor.Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
                if (items.Length == 0) { e.Remove(); continue; }           // lista vacía = «no la mando» (si era obligatoria, el XSD lo dirá)
                e.RemoveNodes();
                foreach (var v in items) e.Add(new XElement(nombre, v));
                continue;
            }
            // xsi:nil se conserva (en "false" si hay valor) para que la plantilla siga sabiendo que el campo admite quedar vacío
            var nulo = e.Attribute(Xsi + "nil");
            e.Value = valor;
            if (nulo != null) nulo.Value = valor == "" ? "true" : "false";
        }
        return copia;
    }
}
