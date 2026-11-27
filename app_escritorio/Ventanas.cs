using System.Data;
using System.Net.Http;
using System.Xml.Linq;

namespace Microhubs;

/// <summary>Piezas comunes de las ventanas: rejilla de solo lectura, botones que muestran los errores del servicio y el editor de plantillas.</summary>
static class Ui
{
    public static DataGridView Rejilla() => new() { Dock = DockStyle.Fill, ReadOnly = true, AllowUserToAddRows = false, AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.DisplayedCells };

    /// <summary>Botón que corre una tarea y, si falla, muestra el mensaje del servicio con sus campos y la traza.</summary>
    public static Button Boton(Control barra, Label estado, string texto, Func<Task> accion)
    {
        var b = new Button { Text = texto, AutoSize = true }; barra.Controls.Add(b);
        b.Click += async (_, _) =>
        {
            b.Enabled = false;
            try { await accion(); }
            catch (ApiError e) { estado.Text = $"{e.Message} · Traza {e.Trace}"; MessageBox.Show(b.FindForm(), e.Message + "\n" + string.Join("\n", e.Fields.Select(f => $"{f.Key}: {f.Value}")) + "\nTraza: " + e.Trace, "Servicio"); }
            catch (Exception e) { estado.Text = e.Message; MessageBox.Show(b.FindForm(), e.Message, "Microhubs"); }
            finally { b.Enabled = true; }
        };
        return b;
    }

    /// <summary>Edita una plantilla XML campo por campo (las listas, separadas por coma) y solo la devuelve si valida contra el XSD.</summary>
    public static XElement? Editar(IWin32Window owner, Api api, string titulo, XElement plantilla)
    {
        using var dialog = new Form { Text = titulo, Width = 650, Height = 680, StartPosition = FormStartPosition.CenterParent };
        var panel = new TableLayoutPanel { Dock = DockStyle.Fill, AutoScroll = true, ColumnCount = 2 };
        var controles = new Dictionary<string, TextBox>();
        var errores = new ErrorProvider { ContainerControl = dialog };
        foreach (var c in Plantillas.Campos(plantilla))
        {
            var t = new TextBox { Text = c.Valor, Width = 340 }; controles[c.Clave] = t;
            panel.Controls.Add(new Label { Text = c.EsLista ? c.Clave + " (separados por coma)" : c.Clave, AutoSize = true }); panel.Controls.Add(t);
        }
        var guardar = new Button { Text = "Validar y guardar", Dock = DockStyle.Bottom, Height = 40 };
        dialog.Controls.Add(panel); dialog.Controls.Add(guardar);
        XElement? resultado = null;
        guardar.Click += (_, _) =>
        {
            errores.Clear();
            var copia = Plantillas.Aplicar(plantilla, controles.ToDictionary(k => k.Key, k => k.Value.Text));
            try { api.Validate(copia.ToString()); resultado = copia; dialog.DialogResult = DialogResult.OK; }
            catch (Exception e) { foreach (var c in controles.Values) errores.SetError(c, e.Message); MessageBox.Show(dialog, e.Message, "Revisa los campos"); }
        };
        return dialog.ShowDialog(owner) == DialogResult.OK ? resultado : null;
    }

    /// <summary>Pide un texto (p. ej. los parámetros de una consulta). Null si se cancela.</summary>
    public static string? Preguntar(IWin32Window owner, string titulo, string etiqueta, string valor)
    {
        using var dialog = new Form { Text = titulo, Width = 520, Height = 160, StartPosition = FormStartPosition.CenterParent, FormBorderStyle = FormBorderStyle.FixedDialog, MinimizeBox = false, MaximizeBox = false };
        var texto = new TextBox { Text = valor, Dock = DockStyle.Top };
        var ok = new Button { Text = "Consultar", DialogResult = DialogResult.OK, Dock = DockStyle.Bottom, Height = 36 };
        dialog.Controls.Add(texto); dialog.Controls.Add(new Label { Text = etiqueta, Dock = DockStyle.Top, Height = 24 }); dialog.Controls.Add(ok);
        dialog.AcceptButton = ok;
        return dialog.ShowDialog(owner) == DialogResult.OK ? texto.Text.Trim() : null;
    }

    public static bool PuedeEscribir(Api api) => api.Role is "planeador" or "administrador";


    /// <summary>Pide dos textos (p. ej. pedidos y repartidor). Null si se cancela.</summary>
    public static (string, string)? PreguntarDos(IWin32Window owner, string titulo, string etiqueta1, string valor1, string etiqueta2, string valor2)
    {
        using var dialog = new Form { Text = titulo, Width = 560, Height = 230, StartPosition = FormStartPosition.CenterParent, FormBorderStyle = FormBorderStyle.FixedDialog, MinimizeBox = false, MaximizeBox = false };
        var panel = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 1, Padding = new Padding(8) };
        var t1 = new TextBox { Text = valor1, Width = 500 }; var t2 = new TextBox { Text = valor2, Width = 500 };
        panel.Controls.Add(new Label { Text = etiqueta1, AutoSize = true }); panel.Controls.Add(t1);
        panel.Controls.Add(new Label { Text = etiqueta2, AutoSize = true }); panel.Controls.Add(t2);
        var ok = new Button { Text = "Aceptar", DialogResult = DialogResult.OK, Dock = DockStyle.Bottom, Height = 36 };
        dialog.Controls.Add(panel); dialog.Controls.Add(ok); dialog.AcceptButton = ok;
        return dialog.ShowDialog(owner) == DialogResult.OK ? (t1.Text.Trim(), t2.Text.Trim()) : null;
    }
}

/// <summary>
/// Pantalla de análisis (cobertura, rutas, costos, capacidad, punto de equilibrio o simulación): un botón por acción del módulo,
/// la colección principal de la respuesta a la izquierda y el resto (totales, decisión, supuestos usados…) a la derecha.
/// </summary>
sealed class VentanaModulo : Form
{
    readonly Api api; readonly Modulo modulo;
    readonly FlowLayoutPanel bar = new() { Dock = DockStyle.Top, AutoSize = true, WrapContents = true };
    readonly DataGridView grid = Ui.Rejilla(), resumen = Ui.Rejilla();
    readonly Label status = new() { Dock = DockStyle.Bottom, Height = 40 };
    XDocument? latest;

    public VentanaModulo(Api api, Modulo modulo)
    {
        this.api = api; this.modulo = modulo;
        Text = $"Microhubs · {modulo.Nombre}"; Width = 1250; Height = 720; StartPosition = FormStartPosition.CenterParent;
        var split = new SplitContainer { Dock = DockStyle.Fill, Orientation = Orientation.Vertical };
        split.Panel1.Controls.Add(grid); split.Panel2.Controls.Add(resumen);
        Controls.Add(split); Controls.Add(bar); Controls.Add(status);
        Load += (_, _) => split.SplitterDistance = (int)(split.Width * 0.66);
        status.Text = modulo.Descripcion;
        foreach (var a in modulo.Acciones)
        {
            var b = Ui.Boton(bar, status, a.Titulo, () => Ejecutar(a));
            if (!a.Habilitada(api)) { b.Enabled = false; b.Text += a.Permiso != null ? " (sin permiso)" : " (solo planeación)"; }
        }
        Ui.Boton(bar, status, "Exportar XML", () =>
        {
            if (latest == null) throw new Exception("Consulta primero.");
            using var d = new SaveFileDialog { Filter = "XML|*.xml", FileName = $"microhubs_{modulo.Nombre.ToLowerInvariant().Replace(' ', '_')}.xml" };
            if (d.ShowDialog(this) == DialogResult.OK) latest.Save(d.FileName);
            return Task.CompletedTask;
        });
    }

    async Task Ejecutar(Accion a)
    {
        string? id = null, consulta = null; XElement? cuerpo = null;
        if (a.Formulario == "manifiesto") { await Manifiesto(a); return; }
        if (a.PorFila)
        {
            // de la fila elegida; si la tabla no tiene esa columna (p. ej. el id de un microhub), se pide
            if (grid.CurrentRow != null && grid.Columns.Contains(a.Columna)) id = grid.CurrentRow.Cells[a.Columna].Value?.ToString();
            else if ((id = Ui.Preguntar(this, $"{modulo.Nombre} · {a.Titulo}", $"Id ({a.Columna}):", "")) == null) return;
        }
        if (a.Parametros != null && (consulta = Ui.Preguntar(this, $"{modulo.Nombre} · {a.Titulo}", "Parámetros (clave=valor separados por &):", a.Parametros)) == null) return;
        if (a.Formulario == "asignacion")
        {
            // si la tabla muestra los pedidos listos, se proponen los renglones elegidos (o el actual)
            IEnumerable<DataGridViewRow> elegidos = grid.SelectedRows.Count > 0 ? grid.SelectedRows.Cast<DataGridViewRow>().Reverse() : grid.CurrentRow is { } fila ? [fila] : [];
            var pedidos = latest?.Root?.Name == Api.Ns + "pedidos_listos" && grid.Columns.Contains("id")
                ? string.Join(", ", elegidos.Select(r => r.Cells["id"].Value?.ToString())) : "";
            var dos = Ui.PreguntarDos(this, $"{modulo.Nombre} · {a.Titulo}", "Pedidos listos, en orden de parada (ids separados por coma):", pedidos,
                                      "Repartidor (id; ver «Repartidores»):", "");
            if (dos == null) return;
            cuerpo = Operacion.Asignacion(dos.Value.Item1, dos.Value.Item2);
        }
        if (a.Plantilla != null && (cuerpo = Ui.Editar(this, api, $"{modulo.Nombre} · {a.Titulo}", Plantillas.ConOperacionNueva(Api.Example(a.Plantilla)))) == null) return;
        if (a.Metodo != "GET" && a.Plantilla == null
            && MessageBox.Show(this, $"{a.Titulo} {id}?", modulo.Nombre, MessageBoxButtons.YesNo, MessageBoxIcon.Question) != DialogResult.Yes) return;
        var doc = await api.Call(a.Servicio, a.Armar(id, consulta), a.Http, cuerpo, root: a.Raiz);
        latest = doc;
        grid.DataSource = Tablas.Principal(doc); resumen.DataSource = Tablas.Resumen(doc);
        status.Text = $"{modulo.Nombre} · {a.Titulo} · {grid.Rows.Count} filas · {api.Role}";
    }

    /// <summary>Manifiesto de salida de un repartidor: sus entregas abiertas, el detalle de cada una y una página imprimible.</summary>
    async Task Manifiesto(Accion a)
    {
        var rep = Ui.Preguntar(this, $"{modulo.Nombre} · {a.Titulo}", "Repartidor (id; ver «Repartidores»):", "");
        if (rep == null) return;
        var rid = Operacion.Ids(rep, "Repartidor").Single();
        var lista = await api.Call(a.Servicio, a.Armar(null, a.Parametros + $"&repartidor_id={rid}"), root: a.Raiz);
        var ids = lista.Root!.Element(Api.Ns + "datos")!.Elements().Select(e => e.Element(Api.Ns + "id")!.Value).ToList();
        if (ids.Count == 0) throw new Exception($"El repartidor {rid} no tiene entregas abiertas.");
        var detalles = new List<XDocument>();
        foreach (var eid in ids) detalles.Add(await api.Call("entregas", $"entregas/{eid}", root: "entrega_detalle"));
        var tabla = Operacion.Manifiesto(detalles);
        latest = lista; grid.DataSource = tabla;
        resumen.DataSource = Tablas.CampoValor(new Dictionary<string, string> { ["repartidor_id"] = rid.ToString(), ["paradas"] = tabla.Rows.Count.ToString(),
                                                                                  ["total_a_cobrar"] = Operacion.TotalACobrar(tabla).ToString("0.00", System.Globalization.CultureInfo.InvariantCulture) });
        status.Text = $"Manifiesto del repartidor {rid} · {tabla.Rows.Count} paradas · {api.Role}";
        using var d = new SaveFileDialog { Filter = "Página para imprimir|*.html", FileName = $"manifiesto_repartidor_{rid}_{DateTime.Now:yyyyMMdd_HHmm}.html" };
        if (d.ShowDialog(this) == DialogResult.OK)
        {
            File.WriteAllText(d.FileName, Operacion.ManifiestoHtml(tabla, $"#{rid}", DateTime.Now), System.Text.Encoding.UTF8);
            System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo(d.FileName) { UseShellExecute = true });
        }
    }
}

/// <summary>
/// Reportes (servicio 5123): catálogo, indicadores, cada reporte como tabla o como datos de gráfica, la bitácora de exportaciones y
/// la descarga en CSV, Excel o PDF. Solo se mandan los filtros que el reporte admite según el catálogo.
/// </summary>
sealed class VentanaReportes : Form
{
    readonly Api api;
    readonly FlowLayoutPanel bar = new() { Dock = DockStyle.Top, AutoSize = true, WrapContents = true };
    readonly DataGridView grid = Ui.Rejilla(), resumen = Ui.Rejilla();
    readonly Label status = new() { Dock = DockStyle.Bottom, Height = 40, Text = "Elige un reporte y su periodo." };
    readonly ComboBox reporte = new() { DropDownStyle = ComboBoxStyle.DropDownList, Width = 260 };
    readonly DateTimePicker desde = new() { Format = DateTimePickerFormat.Short, ShowCheckBox = true, Checked = true, Value = DateTime.Today.AddDays(-30) };
    readonly DateTimePicker hasta = new() { Format = DateTimePickerFormat.Short, ShowCheckBox = true, Checked = true, Value = DateTime.Today };
    readonly TextBox zona = new() { Width = 50 }, microhub = new() { Width = 50 };
    XDocument? catalogo, latest;
    List<(string clave, string titulo)> claves = new();

    public VentanaReportes(Api api)
    {
        this.api = api;
        Text = "Microhubs · Reportes"; Width = 1250; Height = 720; StartPosition = FormStartPosition.CenterParent;
        var split = new SplitContainer { Dock = DockStyle.Fill, Orientation = Orientation.Vertical };
        split.Panel1.Controls.Add(grid); split.Panel2.Controls.Add(resumen);
        Controls.Add(split); Controls.Add(bar); Controls.Add(status);
        Load += (_, _) => split.SplitterDistance = (int)(split.Width * 0.72);
        bar.Controls.AddRange(new Control[] { new Label { Text = "Reporte", AutoSize = true }, reporte, new Label { Text = "Desde", AutoSize = true }, desde,
            new Label { Text = "Hasta", AutoSize = true }, hasta, new Label { Text = "Zona", AutoSize = true }, zona, new Label { Text = "Microhub", AutoSize = true }, microhub });
        Ui.Boton(bar, status, "Catálogo", Catalogo);
        Ui.Boton(bar, status, "Ver reporte", async () => Mostrar(await api.Call("reportes", Consulta(""), root: "reporte"), "reporte"));
        Ui.Boton(bar, status, "Gráfica", async () => Mostrar(await api.Call("reportes", Consulta("/grafica"), root: "grafica"), "gráfica"));
        Ui.Boton(bar, status, "Descargar CSV", () => Descargar("csv", "CSV|*.csv"));
        Ui.Boton(bar, status, "Descargar Excel", () => Descargar("xlsx", "Excel|*.xlsx"));
        Ui.Boton(bar, status, "Descargar PDF", () => Descargar("pdf", "PDF|*.pdf"));
        Ui.Boton(bar, status, "Indicadores", async () => Mostrar(await api.Call("reportes", Modulos.Indicadores.Armar(), root: Modulos.Indicadores.Raiz), "indicadores"));
        Ui.Boton(bar, status, "Exportaciones", async () => Mostrar(await api.Call("reportes", Modulos.Exportaciones.Armar(), root: Modulos.Exportaciones.Raiz), "exportaciones"));
        Ui.Boton(bar, status, "Exportar XML", () =>
        {
            if (latest == null) throw new Exception("Consulta primero.");
            using var d = new SaveFileDialog { Filter = "XML|*.xml", FileName = "microhubs_reporte.xml" };
            if (d.ShowDialog(this) == DialogResult.OK) latest.Save(d.FileName);
            return Task.CompletedTask;
        });
        Shown += async (_, _) => { try { await Catalogo(); } catch (Exception e) { status.Text = e.Message; } };
    }

    async Task Catalogo()
    {
        catalogo = await api.Call("reportes", Modulos.Catalogo.Armar(), root: Modulos.Catalogo.Raiz);
        claves = catalogo.Descendants(Api.Ns + "reporte").Select(r => (r.Element(Api.Ns + "clave")!.Value, r.Element(Api.Ns + "titulo")!.Value)).ToList();
        var actual = reporte.SelectedIndex;
        reporte.Items.Clear(); reporte.Items.AddRange(claves.Select(c => (object)$"{c.titulo} ({c.clave})").ToArray());
        if (reporte.Items.Count > 0) reporte.SelectedIndex = Math.Clamp(actual, 0, reporte.Items.Count - 1);
        Mostrar(catalogo, "catálogo");
    }

    static int? Entero(TextBox t, string nombre)
    {
        var s = t.Text.Trim();
        if (s == "") return null;
        return int.TryParse(s, out var n) && n > 0 ? n : throw new Exception($"{nombre}: escribe un id (número) o déjalo vacío.");
    }

    string Consulta(string sufijo, string? formato = null)
    {
        if (catalogo == null || reporte.SelectedIndex < 0) throw new Exception("Carga el catálogo y elige un reporte.");
        var clave = claves[reporte.SelectedIndex].clave;
        return Tablas.ConsultaReporte(clave, sufijo, desde.Checked ? desde.Value.Date : null, hasta.Checked ? hasta.Value.Date : null,
                                      Entero(zona, "Zona"), Entero(microhub, "Microhub"), formato, Tablas.FiltrosDe(catalogo, clave));
    }

    void Mostrar(XDocument doc, string que)
    {
        latest = doc;
        grid.DataSource = Tablas.Principal(doc); resumen.DataSource = Tablas.Resumen(doc);
        status.Text = $"{que} · {grid.Rows.Count} filas · {api.Role}";
    }

    async Task Descargar(string formato, string filtro)
    {
        var archivo = await api.Download("reportes", Consulta("/exportar", formato), formato);
        using var d = new SaveFileDialog { Filter = filtro, FileName = archivo.Nombre };
        if (d.ShowDialog(this) != DialogResult.OK) return;
        await File.WriteAllBytesAsync(d.FileName, archivo.Contenido);
        status.Text = $"Guardado {Path.GetFileName(d.FileName)} · {archivo.Contenido.Length:N0} bytes · {archivo.Filas} filas · SHA-256 {archivo.Sha256[..16]}… verificado";
    }
}
