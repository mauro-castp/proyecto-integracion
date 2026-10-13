using System.Net;
using System.Net.Http;
using System.Text;
using System.Xml.Linq;

namespace Microhubs;

/// <summary>
/// Pruebas del cliente de escritorio. Tres bloques:
///   1) contrato: los 46 ejemplos XML oficiales validan contra los XSD y los XML incorrectos se rechazan;
///   2) protocolo: con un transporte simulado (renovación con 401, 429, errores, JSON rechazado, HTTP solo local);
///   3) backend real (opcional): MICROHUBS_BACKEND=http://localhost MICROHUBS_CLAVE=... recorre todas las pantallas contra los servicios.
/// </summary>
static class Pruebas
{
    static int total;
    static void Check(bool value, string name) { if (!value) throw new Exception("FALLA: " + name); Console.WriteLine("PASA: " + name); total++; }
    static void Reject(Action action, string name) { try { action(); } catch { Check(true, name); return; } throw new Exception("FALLA, se aceptó: " + name); }
    static async Task RejectAsync(Func<Task> action, string name) { try { await action(); } catch { Check(true, name); return; } throw new Exception("FALLA, se aceptó: " + name); }
    static string Ex(string name) => File.ReadAllText(Path.Combine(AppContext.BaseDirectory, "contratos", "ejemplos", name));

    static async Task Main()
    {
        Contrato();
        await Protocolo();
        VentanaDeEscritorio();
        var backend = Environment.GetEnvironmentVariable("MICROHUBS_BACKEND");
        if (!string.IsNullOrEmpty(backend)) await BackendReal(backend);
        else Console.WriteLine("(Omitidas las pruebas con backend real: define MICROHUBS_BACKEND=http://localhost y MICROHUBS_CLAVE)");
        Console.WriteLine($"{total} comprobaciones aprobadas");
    }

    // ------------------------------------------------------------------------------------------ 1) contrato
    static void Contrato()
    {
        using var api = new Api();
        var archivos = Directory.GetFiles(Path.Combine(AppContext.BaseDirectory, "contratos", "ejemplos"), "*.xml");
        foreach (var f in archivos) api.Validate(File.ReadAllText(f));
        Check(archivos.Length >= 46, $"Los {archivos.Length} ejemplos XML oficiales validan contra los XSD");
        Reject(() => api.Validate("<sesion xmlns='urn:microhubs:v1'/>"), "XSD rechaza sesión incompleta");
        Reject(() => api.Validate(Ex("Sesion.ok.xml").Replace("urn:microhubs:v1", "urn:otro")), "Rechaza otro espacio de nombres");
        Reject(() => api.Validate(Ex("CandidatoNuevo.ok.xml").Replace("<accesibilidad_vial>7</accesibilidad_vial>", "<accesibilidad_vial>11</accesibilidad_vial>")), "Rechaza accesibilidad fuera de 1 a 10");
        Reject(() => api.Validate(Ex("Decision.ok.xml").Replace("Renegociar la renta antes de firmar.", "ok")), "Rechaza motivo de decisión demasiado corto");
        Reject(() => api.Validate(Ex("Login.ok.xml").Replace("repartidor1@codex.mx", "sin-formato")), "Rechaza correo sin formato");
        Reject(() => api.Validate(Ex("Decision.ok.xml").Replace("condicionado", "quizas")), "Rechaza decisión fuera del catálogo");
        Reject(() => api.Validate("<!DOCTYPE x [<!ENTITY x SYSTEM 'file:///C:/Windows/win.ini'>]><error xmlns='urn:microhubs:v1'><mensaje>&x;</mensaje></error>"), "Rechaza DTD y entidades externas");
        Reject(() => api.Validate("<desconocido xmlns='urn:microhubs:v1'/>"), "Rechaza una raíz que no existe en el contrato");
    }

    // ------------------------------------------------------------------------------------------ 2) protocolo
    static async Task Protocolo()
    {
        using (var demo = new Api { Demo = true })
        {
            demo.SetSession(await demo.Call("auth", "auth/login", HttpMethod.Post, Api.Example("Login.ok.xml")));
            Check(demo.Role == "planeador", "Login de ejemplo oficial");
            Check((await demo.Call("catalogos", "productos")).Descendants(Api.Ns + "producto").Any(), "Ejemplo de catálogo");
            Check((await demo.Call("pedidos", "pedidos?estado=entregado")).Root!.Name == Api.Ns + "pedidos", "Ejemplo de pedidos");
            Check((await demo.Call("planeacion", "candidatos/1/simular", HttpMethod.Post, Api.Example("Simular.ok.xml"))).Root!.Name == Api.Ns + "resultados", "Ejemplo de simulación");
            await RejectAsync(() => demo.Call("planeacion", "candidatos", HttpMethod.Post, Api.Body("candidato_nuevo", ("nombre", "incompleto"))), "Una petición que incumple el XSD ni se envía");
            demo.Clear(); Check(demo.Access == "" && demo.Refresh == "" && demo.Role == "", "Salir borra credenciales");
        }

        var handler = new FakeHandler(); using var real = new Api(handler);
        real.SetSession(real.Validate(Ex("Sesion.ok.xml")));
        Check(real.Access != "" && real.Role == "repartidor", "Acepta la sesión del servicio");
        await real.Call("pedidos", "pedidos?estado=entregado&pagina=2");
        Check(handler.Last!.Query.Contains("pagina=2") && !handler.Last.AbsolutePath.Contains('?'), "Conserva la consulta y la ruta /api/v1");
        Check(handler.Last.Port == 5104 && handler.Accept == "application/xml", "Pide XML y usa el puerto del servicio correcto");
        Check(handler.Authorization == "Bearer " + real.Access, "Envía el token en Authorization: Bearer");
        await real.Call("catalogos", "productos"); Check(handler.Last!.Port == 5103, "catalogos → 5103");
        await real.Call("planeacion", "candidatos"); Check(handler.Last!.Port == 5106, "planeacion → 5106");

        handler.UnauthorizedOnce = true;
        await real.Call("pedidos", "pedidos");
        Check(handler.Renewals == 1 && real.Access.EndsWith("firma2"), "401 renueva una vez, guarda los tokens nuevos y reintenta");
        Check(real.Role == "repartidor", "La renovación conserva el rol de la sesión");

        handler.SlowUnauthorized = 2; real.Access = "token.viejo.firma";
        var paralelo = await Task.WhenAll(real.Call("pedidos", "pedidos"), real.Call("pedidos", "pedidos"));
        Check(handler.Renewals == 2, "Dos peticiones con 401 simultáneas renuevan una sola vez (el token de renovación rota)");

        handler.WrongContent = true;
        await RejectAsync(() => real.Call("pedidos", "pedidos"), "Rechaza respuestas que no son application/xml");
        handler.WrongContent = false;

        handler.Next = (HttpStatusCode.UnprocessableEntity, Ex("Error.validacion.xml"));
        try { await real.Call("planeacion", "candidatos", HttpMethod.Post, Api.Example("CandidatoNuevo.ok.xml")); throw new Exception("se esperaba un error"); }
        catch (ApiError e) { Check(e.Status == 422 && e.Fields["cantidad"] == "Debe ser mayor a 0." && e.Trace.StartsWith("9f2c"), "Un error XML del servicio llega con estado, campos y traza"); }

        handler.Next = ((HttpStatusCode)429, Ex("Error.validacion.xml")); handler.RetryAfter = 30;
        await RejectAsync(() => real.Call("pedidos", "pedidos"), "429 se informa como error");
        var llamadas = handler.Calls;
        try { await real.Call("pedidos", "pedidos"); } catch (Exception e) { Check(e.Message.Contains("Espera") && handler.Calls == llamadas, "Respeta Retry-After: no vuelve a llamar hasta que pase"); }

        using var otro = new Api(new FakeHandler()) { Host = "http://servidor.ejemplo.com" };
        otro.SetSession(otro.Validate(Ex("Sesion.ok.xml")));
        await RejectAsync(() => otro.Call("pedidos", "pedidos"), "HTTP solo se permite hacia el equipo local");
        using var seguro = new Api(new FakeHandler()) { Host = "https://servidor.ejemplo.com" };
        seguro.SetSession(seguro.Validate(Ex("Sesion.ok.xml"))); await seguro.Call("pedidos", "pedidos");
        Check(true, "HTTPS sí se permite hacia cualquier host");

        var fallida = new FakeHandler { Next = (HttpStatusCode.Unauthorized, Ex("Error.token_invalido.xml")) }; using var sinRenovar = new Api(fallida) { };
        sinRenovar.SetSession(sinRenovar.Validate(Ex("Sesion.ok.xml")));
        fallida.RenewalFails = true;
        await RejectAsync(() => sinRenovar.Call("pedidos", "pedidos"), "Si la renovación falla se rechaza la petición");
        Check(sinRenovar.Access == "" && sinRenovar.Refresh == "", "…y la sesión queda vacía");
    }

    // ------------------------------------------------------------------------------------------ ventana
    static void VentanaDeEscritorio()
    {
        Exception? startupError = null;
        var thread = new Thread(() => { try { using var window = new MainWindow(); Check(window.Text.Contains("Planeación") && window.Controls.Count == 3, "Inicializa la ventana de escritorio"); } catch (Exception e) { startupError = e; } });
        thread.SetApartmentState(ApartmentState.STA); thread.Start(); thread.Join();
        if (startupError != null) throw startupError;
    }

    // ------------------------------------------------------------------------------------------ 3) backend real
    static async Task BackendReal(string host)
    {
        var clave = Environment.GetEnvironmentVariable("MICROHUBS_CLAVE") ?? throw new Exception("Define MICROHUBS_CLAVE con la clave de las cuentas de demostración.");
        Console.WriteLine($"-- Backend real en {host}");
        async Task<Api> Entrar(string correo)
        {
            var a = new Api { Host = host };
            a.SetSession(await a.Call("auth", "auth/login", HttpMethod.Post, Api.Body("login", ("correo", correo), ("clave", clave))));
            return a;
        }
        using var plan = await Entrar("planeador@codex.mx");
        Check(plan.Role == "planeador", "Login real: planeador (la sesión se validó contra el XSD oficial)");
        var tokenViejo = plan.Access;
        try { using var mala = new Api { Host = host }; await mala.Call("auth", "auth/login", HttpMethod.Post, Api.Body("login", ("correo", "planeador@codex.mx"), ("clave", "incorrecta"))); throw new Exception("entró"); }
        catch (ApiError e) { Check(e.Status == 401 && e.Message.Contains("Intento"), "Clave incorrecta: 401 con mensaje de intentos"); }

        Check((await plan.Call("catalogos", "productos?pagina=1&por_pagina=5&q=arroz")).Descendants(Api.Ns + "producto").Any(), "Catálogo: productos filtrados (XML válido)");
        var prod = (await plan.Call("catalogos", "productos?pagina=1&por_pagina=1")).Descendants(Api.Ns + "producto").First().Element(Api.Ns + "id")!.Value;
        Check((await plan.Call("catalogos", $"productos/{prod}")).Root!.Name == Api.Ns + "producto", "Catálogo: detalle de producto");
        Check((await plan.Call("catalogos", "zonas")).Root!.Name == Api.Ns + "zonas" && (await plan.Call("catalogos", "microhubs")).Root!.Name == Api.Ns + "microhubs", "Catálogo: zonas y microhubs");
        var pedidos = await plan.Call("pedidos", "pedidos?pagina=1&por_pagina=5&estado=entregado");
        var pid = pedidos.Descendants(Api.Ns + "pedido").First().Element(Api.Ns + "id")!.Value;
        Check((await plan.Call("pedidos", $"pedidos/{pid}")).Descendants(Api.Ns + "linea").Any(), "Pedidos: detalle con líneas");
        Check((await plan.Call("pedidos", $"pedidos/{pid}/historial")).Root!.Name == Api.Ns + "historial", "Pedidos: historial");
        await RejectAsync(() => plan.Call("pedidos", "pedidos?estado=inventado"), "Pedidos: un filtro inválido da error 400");

        foreach (var (srv, recurso) in new[] { ("catalogos", "productos"), ("catalogos", "zonas"), ("catalogos", "microhubs"), ("pedidos", "pedidos"), ("planeacion", "candidatos"), ("planeacion", "escenarios") })
        {
            var tabla = MainWindow.ToTable(await plan.Call(srv, $"{recurso}?pagina=1&por_pagina=20&q="));
            var vacioValido = recurso == "escenarios" && tabla.Rows.Count == 0;       // en una base nueva aún no hay escenarios guardados
            Check(vacioValido || tabla.Columns.Contains("id") && tabla.Rows.Count > 0, $"Pantalla {recurso}: la tabla tiene columna id y {tabla.Rows.Count} filas (columnas: {tabla.Columns.Count})");
        }

        // candidatos: crear, editar, simular, decidir
        var clavec = "D-" + DateTimeOffset.UtcNow.ToUnixTimeSeconds();
        var nuevo = Api.Example("CandidatoNuevo.ok.xml"); nuevo.Element(Api.Ns + "clave")!.Value = clavec;
        var creado = (await plan.Call("planeacion", "candidatos", HttpMethod.Post, nuevo)).Root!;
        var cid = creado.Element(Api.Ns + "id")!.Value;
        Check(creado.Element(Api.Ns + "clave")!.Value == clavec && creado.Element(Api.Ns + "costo_fijo")!.Value == "67000.00", "Planeación: crear candidato (costo fijo calculado)");
        try { await plan.Call("planeacion", "candidatos", HttpMethod.Post, nuevo); throw new Exception("duplicado aceptado"); }
        catch (ApiError e) { Check(e.Status == 409, "Planeación: clave duplicada → 409"); }
        nuevo.Element(Api.Ns + "nombre")!.Value = "Alianza Norte (editado)"; nuevo.Element(Api.Ns + "renta_estimada")!.Value = "18000.00";
        var editado = (await plan.Call("planeacion", $"candidatos/{cid}", HttpMethod.Put, nuevo)).Root!;
        Check(editado.Element(Api.Ns + "nombre")!.Value.EndsWith("(editado)") && editado.Element(Api.Ns + "costo_fijo")!.Value == "69000.00", "Planeación: modificar candidato recalcula el costo fijo");
        var sim = (await plan.Call("planeacion", $"candidatos/{cid}/simular", HttpMethod.Post, Api.Body("simular"))).Root!;
        var eq = sim.Element(Api.Ns + "equilibrio")!; var margen = double.Parse(eq.Element(Api.Ns + "margen_pedido")!.Value, System.Globalization.CultureInfo.InvariantCulture);
        var mensual = double.Parse(eq.Element(Api.Ns + "mensual")!.Value, System.Globalization.CultureInfo.InvariantCulture);
        Check(Math.Abs(margen * mensual - 69000) <= margen && sim.Element(Api.Ns + "explicacion")!.HasElements, "Planeación: la simulación usa los costos fijos del candidato seleccionado (69,000) y explica su decisión");
        try { await plan.Call("planeacion", $"candidatos/{cid}/decision", HttpMethod.Post, Api.Body("decision", ("decision", "aceptado"), ("motivo", "ok"))); throw new Exception("motivo corto aceptado"); }
        catch (Exception e) when (e is ApiError or System.Xml.Schema.XmlSchemaValidationException) { Check(true, "Planeación: la decisión sin motivo suficiente no pasa"); }
        var decidido = (await plan.Call("planeacion", $"candidatos/{cid}/decision", HttpMethod.Post, Api.Body("decision", ("decision", "condicionado"), ("motivo", "Renegociar la renta antes de firmar.")))).Root!;
        Check(decidido.Element(Api.Ns + "decision")!.Value == "condicionado", "Planeación: decisión humana con motivo");
        Check((await plan.Call("planeacion", "candidatos?decision=condicionado&q=editado")).Descendants(Api.Ns + "candidato").Any(), "Planeación: filtros por decisión y texto");

        var libre = Api.Example("Simulacion.ok.xml");
        var libreR = (await plan.Call("planeacion", "simulaciones", HttpMethod.Post, libre)).Root!;
        Check(libreR.Element(Api.Ns + "equilibrio") != null, "Planeación: simulación libre con supuestos");
        var esc = Api.Example("EscenarioNuevo.ok.xml"); esc.Element(Api.Ns + "candidato_id")!.Value = cid; esc.Element(Api.Ns + "nombre")!.Value = "Escenario de prueba " + clavec;
        var escR = (await plan.Call("planeacion", "escenarios", HttpMethod.Post, esc)).Root!;
        Check((await plan.Call("planeacion", $"escenarios/{escR.Element(Api.Ns + "id")!.Value}")).Root!.Name == Api.Ns + "escenario", "Planeación: guardar y abrir un escenario");
        var listaEsc = await plan.Call("planeacion", "escenarios?pagina=1&por_pagina=5");
        var tablaEsc = MainWindow.ToTable(listaEsc);
        Check(listaEsc.Root!.Name == Api.Ns + "escenarios" && tablaEsc.Rows.Count >= 1 && tablaEsc.Columns.Contains("id"), "Planeación: lista de escenarios y su tabla (con el que se acaba de guardar)");
        var resumen = (await plan.Call("planeacion", "simulaciones/resumen")).Root!;
        Check(int.Parse(resumen.Element(Api.Ns + "total")!.Value) >= 2, "Planeación: resumen por agregación de MongoDB");

        // permisos
        using var aud = await Entrar("auditor@codex.mx");
        Check((await aud.Call("planeacion", "candidatos")).Descendants(Api.Ns + "candidato").Any(), "Auditor: puede consultar candidatos");
        try { await aud.Call("planeacion", "candidatos", HttpMethod.Post, Api.Example("CandidatoNuevo.ok.xml")); throw new Exception("auditor creó"); }
        catch (ApiError e) { Check(e.Status == 403, "Auditor: no puede crear (403)"); }

        // renovación y cierre de sesión
        var antes = plan.Refresh;
        using var otraSesion = await Entrar("planeador@codex.mx");
        otraSesion.Access = "token.invalido.firma";
        await otraSesion.Call("pedidos", "pedidos?por_pagina=1");
        Check(otraSesion.Refresh != "" && otraSesion.Access != "token.invalido.firma", "Token de acceso inválido: renueva con el real y reintenta");
        await plan.Call("auth", "auth/salir", HttpMethod.Post, Api.Body("salir", ("token_renovacion", plan.Refresh)));
        plan.Access = tokenViejo; plan.Refresh = antes;
        try { await plan.Call("pedidos", "pedidos"); throw new Exception("sesión cerrada aún válida"); }
        catch (ApiError e) { Check(e.Status == 401, "Cerrar sesión revoca el token (401) y la renovación vieja ya no sirve"); }
    }

    sealed class FakeHandler : HttpMessageHandler
    {
        public Uri? Last; public string? Accept, Authorization; public bool UnauthorizedOnce, WrongContent, RenewalFails; public int Renewals, Calls, SlowUnauthorized, RetryAfter;
        public (HttpStatusCode code, string body)? Next;
        protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
        {
            Calls++; Last = request.RequestUri; Accept = request.Headers.Accept.ToString(); Authorization = request.Headers.Authorization?.ToString();
            if (Last!.AbsolutePath.EndsWith("renovar"))
            {
                if (RenewalFails) return Xml(HttpStatusCode.Unauthorized, Ex("Error.token_invalido.xml"));
                await Task.Delay(50, cancellationToken); Renewals++;
                return Xml(HttpStatusCode.OK, Ex("Tokens.ok.xml"));
            }
            if (SlowUnauthorized > 0 && request.Headers.Authorization?.Parameter == "token.viejo.firma") { SlowUnauthorized--; await Task.Delay(100, cancellationToken); return Xml(HttpStatusCode.Unauthorized, Ex("Error.token_invalido.xml")); }
            if (UnauthorizedOnce) { UnauthorizedOnce = false; return Xml(HttpStatusCode.Unauthorized, Ex("Error.token_invalido.xml")); }
            if (Next is { } n) { Next = null; var r = Xml(n.code, n.body); if (RetryAfter > 0) r.Headers.RetryAfter = new System.Net.Http.Headers.RetryConditionHeaderValue(TimeSpan.FromSeconds(RetryAfter)); return r; }
            if (WrongContent) return new HttpResponseMessage(HttpStatusCode.OK) { Content = new StringContent("{}", Encoding.UTF8, "application/json") };
            var ruta = Last.AbsolutePath;
            return Xml(HttpStatusCode.OK, Ex(ruta.EndsWith("/productos") ? "ProductoLista.ok.xml" : ruta.EndsWith("/candidatos") ? "CandidatoLista.ok.xml" : "PedidoLista.ok.xml"));
        }
        static HttpResponseMessage Xml(HttpStatusCode code, string body) => new(code) { Content = new StringContent(body, Encoding.UTF8, "application/xml") };
    }
}
