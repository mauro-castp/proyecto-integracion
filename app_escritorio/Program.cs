using System.Data;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Xml;
using System.Xml.Linq;
using System.Xml.Schema;

namespace Microhubs;

static class Program
{
    [STAThread] static void Main() { ApplicationConfiguration.Initialize(); Application.Run(new MainWindow()); }
}

sealed class Api : IDisposable
{
    internal static readonly XNamespace Ns = "urn:microhubs:v1";
    readonly HttpClient http = new() { Timeout = TimeSpan.FromSeconds(20) };
    readonly XmlSchemaSet schemas = new();
    public string Access = "", Refresh = "", Role = "";
    public bool Demo;
    readonly List<(int id, string name)> candidates = new() { (1, "San Bernabé") };
    public string Host = "https://localhost";
    public Api() { schemas.Add(Ns.NamespaceName, Path.Combine(AppContext.BaseDirectory, "contratos", "cliente.xsd")); }
    public static XElement Body(string name, params (string key, string value)[] fields) => new(Ns + name, fields.Select(f => new XElement(Ns + f.key, f.value)));
    public async Task<XDocument> Call(string service, string path, HttpMethod? method = null, XElement? body = null, bool retry = true)
    {
        if (Demo) return Validate(DemoResponse(path, body));
        var ports = new Dictionary<string, int> { ["auth"] = 5101, ["catalogos"] = 5103, ["pedidos"] = 5104, ["planeacion"] = 5106 };
        var parts = path.Split('?', 2);
        var uri = new UriBuilder(Host) { Port = ports[service], Path = "/api/v1/" + parts[0], Query = parts.Length == 2 ? parts[1] : "" };
        using var request = new HttpRequestMessage(method ?? HttpMethod.Get, uri.Uri);
        request.Headers.Accept.Add(new MediaTypeWithQualityHeaderValue("application/xml"));
        if (Access != "") request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", Access);
        if (body != null) request.Content = new StringContent(body.ToString(), Encoding.UTF8, "application/xml");
        using var response = await http.SendAsync(request);
        if (response.StatusCode == System.Net.HttpStatusCode.Unauthorized && retry && Refresh != "" && !path.StartsWith("auth/"))
        {
            try { SetSession(await Call("auth", "auth/renovar", HttpMethod.Post, Body("renovar", ("token_renovacion", Refresh)), false)); }
            catch { Clear(); throw; }
            return await Call(service, path, method, body, false);
        }
        if (response.StatusCode == System.Net.HttpStatusCode.NoContent && response.IsSuccessStatusCode) return new XDocument();
        if (response.Content.Headers.ContentType?.MediaType != "application/xml") throw new Exception("El servicio no devolvió application/xml.");
        var document = Validate(await response.Content.ReadAsStringAsync());
        if (!response.IsSuccessStatusCode) throw new Exception(document.Descendants(Ns + "mensaje").FirstOrDefault()?.Value ?? $"HTTP {(int)response.StatusCode}");
        return document;
    }
    public XDocument Validate(string xml)
    {
        using var reader = XmlReader.Create(new StringReader(xml), new XmlReaderSettings { DtdProcessing = DtdProcessing.Prohibit, XmlResolver = null, MaxCharactersInDocument = 2_000_000 });
        var doc = XDocument.Load(reader);
        doc.Validate(schemas, (_, e) => throw new XmlSchemaValidationException(e.Message));
        return doc;
    }
    public void SetSession(XDocument doc)
    {
        Access = doc.Root!.Element(Ns + "token_acceso")!.Value;
        Refresh = doc.Root.Element(Ns + "token_renovacion")!.Value;
        Role = doc.Descendants(Ns + "rol").Single().Value;
        // La firma y revocación se verifican en el servidor. No se distribuye JWT_SECRET.
        if (!Demo)
        {
            var segments = Access.Split('.');
            if (segments.Length != 3) throw new Exception("JWT inválido.");
            var payload = segments[1].Replace('-', '+').Replace('_', '/');
            payload = payload.PadRight((payload.Length + 3) / 4 * 4, '=');
            using var claims = System.Text.Json.JsonDocument.Parse(Convert.FromBase64String(payload));
            if (claims.RootElement.GetProperty("exp").GetInt64() <= DateTimeOffset.UtcNow.ToUnixTimeSeconds()) throw new Exception("JWT vencido.");
        }
    }
    public void Clear() { Access = Refresh = Role = ""; }
    string DemoResponse(string path, XElement? body)
    {
        if (path is "auth/login" or "auth/renovar") return "<sesion xmlns='urn:microhubs:v1'><token_acceso>demo</token_acceso><token_renovacion>demo</token_renovacion><expira_en>900</expira_en><usuario><id>1</id><nombre>Planeación demo</nombre><rol>planeador</rol><microhub_id>1</microhub_id></usuario></sesion>";
        if (path == "auth/salir") return "<resultado xmlns='urn:microhubs:v1'><mensaje>Sesión cerrada</mensaje></resultado>";
        if (path.Contains("simular")) return new XElement(Ns + "simulacion", new XElement(Ns + "candidato_id", int.Parse(path.Split('/')[1])), new XElement(Ns + "viable", true), new XElement(Ns + "costo", 1250)).ToString();
        if (path.StartsWith("candidatos") && body?.Name.LocalName == "candidato")
        {
            var name = body.Element(Ns + "nombre")!.Value;
            if (path.Contains('/'))
            {
                var id = int.Parse(path.Split('/')[1]);
                var index = candidates.FindIndex(c => c.id == id);
                if (index < 0) throw new Exception("Candidato no encontrado.");
                candidates[index] = (id, name);
            }
            else candidates.Add((candidates.Count == 0 ? 1 : candidates.Max(c => c.id) + 1, name));
            return new XElement(Ns + "resultado", new XElement(Ns + "mensaje", "Candidato guardado en memoria")).ToString();
        }
        if (path == "candidatos") return new XElement(Ns + "lista",
            new XElement(Ns + "datos", candidates.Select(c => Body("candidato", ("id", c.id.ToString()), ("nombre", c.name)))),
            Body("paginacion", ("pagina", "1"), ("por_pagina", "20"), ("total", candidates.Count.ToString()), ("paginas", "1"))).ToString();
        var kind = path.StartsWith("pedidos") ? "pedido" : path.Contains("candidatos") ? "candidato" : "producto";
        return $"<lista xmlns='urn:microhubs:v1'><datos><{kind}><id>1</id><nombre>Ejemplo local</nombre><estado>entregado</estado></{kind}></datos><paginacion><pagina>1</pagina><por_pagina>20</por_pagina><total>1</total><paginas>1</paginas></paginacion></lista>";
    }
    public void Dispose() => http.Dispose();
}

sealed class MainWindow : Form
{
    readonly Api api = new();
    readonly FlowLayoutPanel bar = new() { Dock = DockStyle.Top, AutoSize = true, WrapContents = true };
    readonly DataGridView grid = new() { Dock = DockStyle.Fill, ReadOnly = true, AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill, AllowUserToAddRows = false };
    readonly TextBox mail = new() { PlaceholderText = "Correo", Width = 180 }, password = new() { PlaceholderText = "Clave", UseSystemPasswordChar = true }, host = new() { Text = "https://localhost", Width = 180 }, search = new() { PlaceholderText = "Buscar", Width = 160 };
    readonly CheckBox demo = new() { Text = "Ejemplos locales", Checked = true, AutoSize = true };
    readonly ComboBox state = new() { DropDownStyle = ComboBoxStyle.DropDownList, Width = 120 };
    readonly Label status = new() { Dock = DockStyle.Bottom, Height = 35, Text = "Sin sesión · ejemplos locales" };
    readonly List<Button> privateButtons = new();
    XDocument? latest;
    DataTable? table;
    public MainWindow()
    {
        Text = "Microhubs · Planeación"; Width = 1100; Height = 700;
        Controls.Add(grid); Controls.Add(bar); Controls.Add(status);
        bar.Controls.AddRange(new Control[] { host, demo, mail, password });
        Add("Entrar", async () => {
            if (!mail.Text.Contains('@') || password.Text.Length == 0) throw new Exception("Ingresa correo y clave.");
            if (!Uri.TryCreate(host.Text, UriKind.Absolute, out var uri) || uri.Scheme != "https") throw new Exception("Configura un host HTTPS.");
            api.Clear(); latest = null; table = null; grid.DataSource = null; api.Demo = demo.Checked; api.Host = host.Text;
            try { api.SetSession(await api.Call("auth", "auth/login", HttpMethod.Post, Api.Body("login", ("correo", mail.Text.Trim()), ("clave", password.Text)))); }
            catch { api.Clear(); throw; }
            password.Clear(); SetMenu(); status.Text = $"{api.Role} · {(api.Demo ? "Ejemplos locales" : "Conectado")}";
        });
        Add("Productos", () => LoadList("catalogos", "productos"), true);
        Add("Pedidos cerrados", () => LoadList("pedidos", "pedidos?estado=entregado"), true);
        Add("Candidatos", () => LoadList("planeacion", "candidatos"), true);
        Add("Guardar candidato", async () => {
            using var dialog = new Form { Text = "Candidato", Width = 350, Height = 210 };
            var id = new TextBox { PlaceholderText = "ID (vacío para crear)", Dock = DockStyle.Top };
            var name = new TextBox { PlaceholderText = "Nombre", Dock = DockStyle.Top };
            var save = new Button { Text = "Guardar", Dock = DockStyle.Bottom, DialogResult = DialogResult.OK };
            dialog.Controls.AddRange(new Control[] { id, name, save });
            if (dialog.ShowDialog(this) != DialogResult.OK) return;
            if (name.Text.Trim().Length < 3 || (id.Text != "" && (!int.TryParse(id.Text, out var n) || n <= 0))) throw new Exception("Nombre e ID inválidos.");
            latest = await api.Call("planeacion", "candidatos" + (id.Text == "" ? "" : "/" + id.Text), id.Text == "" ? HttpMethod.Post : HttpMethod.Put, Api.Body("candidato", ("nombre", name.Text.Trim())));
            await LoadList("planeacion", "candidatos");
        }, true);
        Add("Simular selección", async () => {
            if (grid.CurrentRow == null) throw new Exception("Selecciona un candidato.");
            if (currentResource != "candidatos") throw new Exception("Consulta y selecciona un candidato primero.");
            var id = Convert.ToString(grid.CurrentRow.Cells["id"].Value);
            latest = await api.Call("planeacion", $"candidatos/{Uri.EscapeDataString(id!)}/simular", HttpMethod.Post, Api.Body("simular"));
            MessageBox.Show(latest.ToString(), "Viabilidad");
        }, true);
        Add("Exportar XML", () => {
            if (latest == null) throw new Exception("Consulta primero los datos.");
            using var save = new SaveFileDialog { Filter = "XML|*.xml", FileName = "microhubs.xml" };
            if (save.ShowDialog() == DialogResult.OK) latest.Save(save.FileName);
            return Task.CompletedTask;
        }, true);
        Add("Salir", async () => { try { await api.Call("auth", "auth/salir", HttpMethod.Post, Api.Body("salir", ("token_renovacion", api.Refresh))); } finally { api.Clear(); latest = null; table = null; grid.DataSource = null; SetMenu(); status.Text = "Sin sesión"; } }, true);
        state.Items.AddRange(new object[] { "Todos", "entregado", "parcial", "fallido" }); state.SelectedIndex = 0;
        bar.Controls.AddRange(new Control[] { search, state });
        search.TextChanged += (_, _) => Filter(); state.SelectedIndexChanged += (_, _) => Filter(); SetMenu();
        FormClosed += (_, _) => api.Dispose();
    }
    void SetMenu() { foreach (var b in privateButtons) b.Enabled = api.Access != "" && (b.Text is "Salir" or "Exportar XML" || api.Role is "planeador" or "administrador" or "auditor"); privateButtons.Where(b => b.Text is "Guardar candidato" or "Simular selección").ToList().ForEach(b => b.Enabled = api.Access != "" && api.Role is "planeador" or "administrador"); }
    void Add(string text, Func<Task> action, bool secured = false)
    {
        var button = new Button { Text = text, AutoSize = true };
        button.Click += async (_, _) => { button.Enabled = false; try { await action(); } catch (Exception e) { status.Text = e.Message; MessageBox.Show(e.Message, "Microhubs"); } finally { button.Enabled = true; SetMenu(); } };
        bar.Controls.Add(button); if (secured) privateButtons.Add(button);
    }
    string currentResource = "";
    async Task LoadList(string service, string path)
    {
        // Query parameters must remain a query, not part of UriBuilder.Path.
        latest = await api.Call(service, path);
        currentResource = path.Split('?')[0];
        var rows = latest.Descendants(Api.Ns + "datos").Elements().ToList();
        table = new DataTable();
        foreach (var col in rows.SelectMany(r => r.Elements()).Select(e => e.Name.LocalName).Distinct()) table.Columns.Add(col);
        foreach (var row in rows) { var item = table.NewRow(); foreach (var cell in row.Elements()) item[cell.Name.LocalName] = cell.Value; table.Rows.Add(item); }
        grid.DataSource = table; Filter(); status.Text = $"{rows.Count} registros · {api.Role}";
    }
    void Filter()
    {
        if (table == null) return;
        var rows = table.Clone();
        foreach (DataRow row in table.Rows) if (row.ItemArray.Any(v => (v?.ToString() ?? "").Contains(search.Text, StringComparison.OrdinalIgnoreCase)) && (state.Text == "Todos" || (table.Columns.Contains("estado") && row["estado"].ToString() == state.Text))) rows.ImportRow(row);
        grid.DataSource = rows;
    }
}
