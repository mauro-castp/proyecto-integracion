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
        await Analisis();
#if !SIN_VENTANA
        VentanaDeEscritorio();
#endif
        var backend = Environment.GetEnvironmentVariable("MICROHUBS_BACKEND");
        if (!string.IsNullOrEmpty(backend)) { await BackendReal(backend); await AnalisisReal(backend); await OperacionReal(backend); }
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
            Check((await demo.Call("productos", "productos")).Descendants(Api.Ns + "producto").Any(), "Ejemplo de catálogo");
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
        await real.Call("productos", "productos"); Check(handler.Last!.Port == 5103, "productos → 5103");
        await real.Call("zonas", "zonas"); Check(handler.Last!.Port == 5108, "zonas → 5108");
        await real.Call("microhubs", "microhubs"); Check(handler.Last!.Port == 5109, "microhubs → 5109");
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

        var repetido = XDocument.Parse(Ex("Error.validacion.xml")); var detalle = repetido.Descendants(Api.Ns + "detalle").Single();
        detalle.Element(Api.Ns + "campo")!.Value = "pedido_ids"; detalle.Element(Api.Ns + "mensaje")!.Value = "El pedido 163 no está listo o no es de ese microhub.";
        var segundo = new XElement(detalle); segundo.Element(Api.Ns + "mensaje")!.Value = "El pedido 176 no está listo o no es de ese microhub."; detalle.AddAfterSelf(segundo);
        handler.Next = (HttpStatusCode.UnprocessableEntity, repetido.ToString());
        try { await real.Call("rutas", "rutas/comparaciones", HttpMethod.Post, Api.Example("RutaComparacionNueva.ok.xml")); throw new Exception("se esperaba un error"); }
        catch (ApiError e) { Check(e.Status == 422 && e.Fields.Count == 1 && e.Fields["pedido_ids"].Contains("163") && e.Fields["pedido_ids"].Contains("176"), "Varios detalles del mismo campo (un pedido no listo por renglón) se juntan en uno sin tronar"); }

        handler.Next = ((HttpStatusCode)429, Ex("Error.validacion.xml")); handler.RetryAfter = 30;
        await RejectAsync(() => real.Call("pedidos", "pedidos"), "429 se informa como error");
        var llamadas = handler.Calls;
        try { await real.Call("pedidos", "pedidos"); } catch (Exception e) { Check(e.Message.Contains("Espera") && handler.Calls == llamadas, "Respeta Retry-After: no vuelve a llamar hasta que pase"); }

        using var otro = new Api(new FakeHandler()) { Host = "http://servidor.ejemplo.com" };
        otro.SetSession(otro.Validate(Ex("Sesion.ok.xml")));
        await RejectAsync(() => otro.Call("pedidos", "pedidos"), "HTTP solo se permite hacia el equipo local");
        var porPuerto = new FakeHandler();
        using var seguro = new Api(porPuerto) { Host = "https://servidor.ejemplo.com" };
        seguro.SetSession(seguro.Validate(Ex("Sesion.ok.xml"))); await seguro.Call("pedidos", "pedidos");
        Check(true, "HTTPS sí se permite hacia cualquier host");
        Check(porPuerto.Last!.AbsoluteUri == "https://servidor.ejemplo.com:5104/api/v1/pedidos", "Sin ruta en el servidor: cada servicio va a su puerto");
        var porRuta = new FakeHandler();
        using var nube = new Api(porRuta) { Host = "https://servidor.ejemplo.com/servicios/" };
        nube.SetSession(nube.Validate(Ex("Sesion.ok.xml"))); await nube.Call("pedidos", "pedidos?por_pagina=1");
        Check(porRuta.Last!.AbsoluteUri == "https://servidor.ejemplo.com/servicios/pedidos/api/v1/pedidos?por_pagina=1", "Con ruta en el servidor (nube): un solo puerto y el nombre del servicio");

        var fallida = new FakeHandler { Next = (HttpStatusCode.Unauthorized, Ex("Error.token_invalido.xml")) }; using var sinRenovar = new Api(fallida) { };
        sinRenovar.SetSession(sinRenovar.Validate(Ex("Sesion.ok.xml")));
        fallida.RenewalFails = true;
        await RejectAsync(() => sinRenovar.Call("pedidos", "pedidos"), "Si la renovación falla se rechaza la petición");
        Check(sinRenovar.Access == "" && sinRenovar.Refresh == "", "…y la sesión queda vacía");
    }

    // ------------------------------------------------------------------------------------------ 2b) análisis, reportes y descargas (sin red)
    static async Task Analisis()
    {
        using var demo = new Api { Demo = true };
        demo.SetSession(await demo.Call("auth", "auth/login", HttpMethod.Post, Api.Example("Login.ok.xml")));
        foreach (var m in Modulos.Todos)
            foreach (var a in m.Acciones)
            {
                if (a.Plantilla != null) { demo.Validate(Api.Example(a.Plantilla).ToString()); }
                var doc = await demo.Call(a.Servicio, a.Armar(a.PorFila ? "1" : null), a.Http, a.Plantilla != null ? Api.Example(a.Plantilla) : null, root: a.Raiz);
                if (doc.Root!.Name != Api.Ns + a.Raiz) throw new Exception($"FALLA: {m.Nombre} · {a.Titulo} devolvió {doc.Root.Name.LocalName}");
                Tablas.Principal(doc); Tablas.Resumen(doc);
            }
        Check(true, $"Las {Modulos.Todos.Sum(m => m.Acciones.Length)} acciones de inventario, preparación, despacho, surtido, cobertura, rutas, costos, capacidad, equilibrio y simulación tienen ejemplo oficial con su raíz, sus plantillas validan y su tabla se arma");
        Check(Modulos.Todos.SelectMany(m => m.Acciones).All(a => Api.Puertos.ContainsKey(a.Servicio)), "Cada acción va a un servicio con puerto conocido");
        Check(Tablas.Principal(await demo.Call("capacidad", "capacidad/microhubs", root: "capacidad_microhubs")).Columns.Contains("microhub/id"), "Capacidad: la tabla trae la columna microhub/id que usa «Detalle»");
        var plan = Tablas.Principal(Api.Example("RutaPlan.ok.xml").Document!);
        Check(plan.Rows.Count > 0 && Tablas.Resumen(Api.Example("RutaPlan.ok.xml").Document!).Rows.Count > 0, "Un plan de rutas se ve como tabla (sus rutas) más un resumen campo → valor");
        var comparacion = new XDocument(Api.Example("RutaComparacion.ok.xml")); var sup = comparacion.Root!.Element(Api.Ns + "supuestos_usados")!;
        for (var i = 0; i < 4; i++) sup.Add(new XElement(sup.Elements().First()));                     // como en el servidor: 6 supuestos y menos métodos
        Check(Tablas.Principal(comparacion).Columns.Contains("metodo") && Tablas.Principal(comparacion).Rows.Count == 2 && Tablas.Resumen(comparacion).Rows.Cast<System.Data.DataRow>().Any(r => (string)r["campo"] == "supuestos_usados/supuesto/clave"),
              "Comparar métodos: la tabla son los métodos aunque haya más supuestos; los supuestos van al resumen");
        Check(Tablas.Coleccion(Api.Example("EquilibrioCalculo.ok.xml").Document!)!.Name.LocalName == "supuestos_usados", "Si los supuestos son la única colección, siguen siendo la tabla");

        // Plantillas: listas de ids como «1, 2» y campos nulos
        var ruta = Api.Example("RutaPlanNuevo.ok.xml");
        var campos = Plantillas.Campos(ruta);
        Check(campos.Single(c => c.Clave == "pedido_ids").EsLista && campos.Single(c => c.Clave == "pedido_ids").Valor == "163, 168, 169", "Plantilla: la lista de pedidos se edita como «163, 168, 169»");
        var editada = Plantillas.Aplicar(ruta, new Dictionary<string, string> { ["pedido_ids"] = "5, 6", ["metodo"] = "exacto" });
        Check(editada.Element(Api.Ns + "pedido_ids")!.Elements().Select(e => e.Value).SequenceEqual(["5", "6"]) && editada.Element(Api.Ns + "metodo")!.Value == "exacto", "Plantilla: la lista se rearma con los ids escritos");
        demo.Validate(editada.ToString());
        var sinLista = Plantillas.Aplicar(ruta, new Dictionary<string, string> { ["pedido_ids"] = " ", ["repartidor_ids"] = "" });
        demo.Validate(sinLista.ToString());
        Check(sinLista.Element(Api.Ns + "pedido_ids") == null && sinLista.Element(Api.Ns + "repartidor_ids") == null, "Plantilla: una lista vacía no se manda (el plan usa todos los pedidos listos) y valida");
        Reject(() => demo.Validate(Plantillas.Aplicar(ruta, new Dictionary<string, string> { ["pedido_ids"] = "1, dos" }).ToString()), "Plantilla: un id que no es número no pasa el XSD");
        var cap = Api.Example("CapacidadSimulacionNueva.ok.xml");
        var conValor = Plantillas.Aplicar(cap, new Dictionary<string, string> { ["capacidad_fisica"] = "120" });
        demo.Validate(conValor.ToString());
        Check(conValor.Element(Api.Ns + "capacidad_fisica")!.Value == "120" && conValor.Element(Api.Ns + "capacidad_fisica")!.Attributes().Single(x => x.Name.LocalName == "nil").Value == "false", "Plantilla: un campo nulo que recibe valor deja de ser nulo y valida");
        demo.Validate(Plantillas.Aplicar(conValor, new Dictionary<string, string> { ["capacidad_fisica"] = "" }).ToString());
        Check(true, "Plantilla: dejarlo vacío lo vuelve nulo y valida");

        // Operación (operador): asignación, manifiesto, uuid nuevo por operación y permisos de la sesión
        var asig = Operacion.Asignacion("121, 155,7", "8");
        demo.Validate(asig.ToString());
        Check(asig.Descendants(Api.Ns + "parada").Select(x => x.Element(Api.Ns + "orden_parada")!.Value + ":" + x.Element(Api.Ns + "pedido_id")!.Value).SequenceEqual(["1:121", "2:155", "3:7"])
              && asig.Descendants(Api.Ns + "repartidor_id").All(x => x.Value == "8"), "Asignación: los pedidos en el orden escrito, paradas 1, 2, 3, y valida contra el XSD");
        Reject(() => Operacion.Asignacion("121, dos", "8"), "Asignación: un id que no es número se rechaza antes de enviar");
        Reject(() => Operacion.Asignacion("121, 121", "8"), "Asignación: un pedido repetido se rechaza");
        Reject(() => Operacion.Asignacion("121", "7, 8"), "Asignación: un solo repartidor");
        Reject(() => Operacion.Asignacion("", "8"), "Asignación: sin pedidos no se manda");
        var d1 = XDocument.Parse(Ex("EntregaDetalle.ok.xml")); var d2 = XDocument.Parse(Ex("EntregaDetalle.ok.xml"));
        d2.Root!.Element(Api.Ns + "orden_parada")!.Value = "1"; d2.Root.Element(Api.Ns + "folio")!.Value = "PED-PRIMERA"; d2.Root.Element(Api.Ns + "total")!.Value = "41.50";
        d2.Root.Element(Api.Ns + "cliente")!.Element(Api.Ns + "nombre")!.Value = "<script>alert(1)</script>";
        var man = Operacion.Manifiesto([d1, d2]);
        Check(man.Rows.Count == 2 && (string)man.Rows[0]["folio"] == "PED-PRIMERA" && (string)man.Rows[1]["productos"] == "2 × Arroz; 4 × Agua purificada"
              && (string)man.Rows[1]["piezas"] == "6" && (string)man.Rows[1]["direccion"] == "Av. Rodrigo Gómez 1420, San Bernabé", "Manifiesto: paradas en orden, productos, piezas y dirección");
        Check(Operacion.TotalACobrar(man) == 199.50m, "Manifiesto: total a cobrar del repartidor (158.00 + 41.50)");
        var html = Operacion.ManifiestoHtml(man, "#7", new DateTime(2026, 11, 27, 9, 0, 0));
        Check(!html.Contains("<script>") && html.Contains("&lt;script&gt;") && html.Contains("199.50") && html.Contains("Recibió (repartidor)"), "Manifiesto: página imprimible con el texto escapado y espacio para firmas");
        var mov = Api.Example("MovimientoNuevo.ok.xml"); var mov1 = Plantillas.ConOperacionNueva(mov); var mov2 = Plantillas.ConOperacionNueva(mov);
        demo.Validate(mov1.ToString());
        Check(mov1.Element(Api.Ns + "operacion_uuid")!.Value != mov.Element(Api.Ns + "operacion_uuid")!.Value && mov1.Element(Api.Ns + "operacion_uuid")!.Value != mov2.Element(Api.Ns + "operacion_uuid")!.Value,
              "Plantilla: cada movimiento lleva un operacion_uuid nuevo (el del ejemplo haría que el servicio lo tomara como duplicado)");
        using (var conPermisos = new Api()) {
            conPermisos.SetSession(XDocument.Parse(Ex("Sesion.ok.xml")));
            Check(conPermisos.Puede("entregas.cerrar") && !conPermisos.Puede("entregas.asignar") && conPermisos.Puede("inventario.ajuste|entregas.ver"), "Sesión: los permisos del perfil habilitan las acciones que escriben");
            var asignar = Modulos.Despacho.Acciones.Single(a => a.Titulo == "Asignar repartidor");
            Check(!asignar.Habilitada(conPermisos) && Modulos.Despacho.Acciones[0].Habilitada(conPermisos), "Sesión: un repartidor no puede asignar; consultar sí");
            conPermisos.Clear();
            Check(!conPermisos.Puede("entregas.cerrar"), "Sesión: al salir se borran los permisos");
        }
        var colas = XDocument.Parse(Ex("ColaCalculo.ok.xml"));
        Check(Tablas.Principal(colas).Columns.Contains("wq_min") && Tablas.Principal(colas).Rows.Count == 2, "Colas M/M/c: la tabla son los operadores posibles con su espera");

        // Rutas armadas a partir de la fila elegida
        var detalle = Modulos.Capacidad.Acciones.Single(a => a.Titulo == "Detalle");
        Check(detalle.Armar("3") == "capacidad/microhubs/3" && detalle.Columna == "microhub/id", "Acción por fila: sustituye el id de la fila");
        Reject(() => detalle.Armar(null), "Acción por fila: sin fila elegida no se llama");
        Reject(() => detalle.Armar("../1"), "Acción por fila: rechaza un id que no es número ni UUID");
        Check(Modulos.Simulacion.Acciones.Single(a => a.Titulo == "Ver ejecución").Armar("2726FCBC-96FF-4EF0-9707-8A8EA2455558") == "simulacion/ejecuciones/2726fcbc-96ff-4ef0-9707-8a8ea2455558", "Acción por fila: las simulaciones usan UUID");
        Check(Modulos.Costos.Acciones.Single(a => a.Titulo == "Resumen").Armar(null, "candidato_id=2") == "costos/resumen?candidato_id=2", "Consulta editable: la persona cambia los parámetros");
        Reject(() => Modulos.Costos.Acciones[0].Armar(null, "x=1/../../auth"), "Consulta editable: rechaza rutas dentro de la consulta");

        // Reportes
        var rep = Tablas.Reporte(Api.Example("Reporte.ok.xml").Document!);
        Check(rep.Columns.Cast<System.Data.DataColumn>().Select(c => c.ColumnName).SequenceEqual(["Día", "Pedidos", "Venta"]) && rep.Rows.Count == 2 && (string)rep.Rows[1][0] == "Total",
            "Reporte: columnas con su título, filas y renglón de totales");
        var graf = Tablas.Grafica(Api.Example("ReporteGrafica.ok.xml").Document!);
        Check(graf.Columns.Count >= 2 && graf.Rows.Count >= 1, "Gráfica: una fila por categoría y una columna por serie");
        Check(Tablas.ConsultaReporte("pedidos_por_dia", "/exportar", new DateTime(2026, 11, 1), new DateTime(2026, 11, 25), null, 2, "xlsx")
              == "reportes/pedidos_por_dia/exportar?desde=2026-11-01&hasta=2026-11-25&microhub_id=2&formato=xlsx", "Reporte: consulta con periodo, microhub y formato (sin zona si no se indicó)");
        Reject(() => Tablas.ConsultaReporte("../auth", "", null, null, null, null), "Reporte: rechaza una clave rara");
        var catEj = Api.Example("ReportesCatalogo.ok.xml").Document!;
        var claveEj = catEj.Descendants(Api.Ns + "reporte").First().Element(Api.Ns + "clave")!.Value;
        var admite = Tablas.FiltrosDe(catEj, claveEj);
        Check(Tablas.ConsultaReporte(claveEj, "", new DateTime(2026, 11, 1), new DateTime(2026, 11, 2), 3, 4, null, new HashSet<string>()) == $"reportes/{claveEj}"
              && Tablas.ConsultaReporte(claveEj, "", null, null, 3, null, null, new HashSet<string> { "zona_id" }) == $"reportes/{claveEj}?zona_id=3",
              $"Reporte: solo se mandan los filtros que el catálogo dice que admite ({claveEj}: {string.Join(", ", admite)})");
        Reject(() => Tablas.ConsultaReporte("pedidos_por_dia", "", new DateTime(2026, 11, 25), new DateTime(2026, 11, 1), null, null), "Reporte: «desde» posterior a «hasta» no se envía");
        Check((await demo.Call("reportes", "reportes", root: "reportes_catalogo")).Descendants(Api.Ns + "reporte").Any(), "Reportes: catálogo de ejemplo");
        var csvDemo = await demo.Download("reportes", "reportes/pedidos_por_dia/exportar?formato=csv", "csv");
        Check(csvDemo.Nombre == "pedidos_por_dia.csv" && System.Text.Encoding.UTF8.GetString(csvDemo.Contenido).StartsWith("Día,Pedidos,Venta"), "Ejemplos: la descarga CSV se arma con el reporte oficial");
        await RejectAsync(() => demo.Download("reportes", "reportes/pedidos_por_dia/exportar?formato=pdf", "pdf"), "Ejemplos: Excel y PDF solo los genera el servicio");

        // Descarga binaria contra un transporte simulado
        var h = new FakeHandler(); using var api = new Api(h);
        api.SetSession(api.Validate(Ex("Sesion.ok.xml")));
        var csv = System.Text.Encoding.UTF8.GetBytes("﻿Día,Pedidos\n2026-11-24,12\n");
        var sha = Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(csv)).ToLowerInvariant();
        h.Custom = _ => Archivo(csv, "text/csv; charset=utf-8", sha, "pedidos_por_dia_2026-10-26_2026-11-25.csv");
        var a1 = await api.Download("reportes", "reportes/pedidos_por_dia/exportar?formato=csv", "csv");
        Check(h.Last!.Port == 5123 && h.Last.PathAndQuery == "/api/v1/reportes/pedidos_por_dia/exportar?formato=csv", "Descarga: puerto 5123 y ruta /api/v1 con su consulta");
        Check(h.Accept!.Contains("text/csv") && h.Accept.Contains("application/xml") && h.Authorization == "Bearer " + api.Access, "Descarga: pide el tipo del archivo (y XML para los errores) con el token");
        Check(a1.Contenido.SequenceEqual(csv) && a1.Sha256 == sha && a1.Nombre == "pedidos_por_dia_2026-10-26_2026-11-25.csv" && a1.Filas == 1, "Descarga: bytes, SHA-256, nombre y filas que manda el servicio");
        h.Custom = _ => Archivo(csv, "text/csv", new string('0', 64), "x.csv");
        await RejectAsync(() => api.Download("reportes", "reportes/x/exportar?formato=csv", "csv"), "Descarga: un SHA-256 distinto al del servicio se rechaza");
        h.Custom = _ => Archivo(csv, "application/pdf", sha, "x.pdf");
        await RejectAsync(() => api.Download("reportes", "reportes/x/exportar?formato=pdf", "pdf"), "Descarga: un PDF que no empieza con %PDF- se rechaza");
        h.Custom = _ => Archivo(csv, "application/json", sha, "x.csv");
        await RejectAsync(() => api.Download("reportes", "reportes/x/exportar?formato=csv", "csv"), "Descarga: un tipo distinto al pedido se rechaza");
        var pdf = System.Text.Encoding.ASCII.GetBytes("%PDF-1.4\n%fin");
        h.Custom = _ => Archivo(pdf, "application/pdf", null, "../../Windows/evil.pdf");
        Check((await api.Download("reportes", "reportes/x/exportar?formato=pdf", "pdf")).Nombre == "evil.pdf", "Descarga: el nombre sugerido no puede llevar carpetas");
        h.Custom = _ => new HttpResponseMessage(HttpStatusCode.BadRequest) { Content = new StringContent(Ex("Error.validacion.xml"), System.Text.Encoding.UTF8, "application/xml") };
        try { await api.Download("reportes", "reportes/x/exportar?formato=csv&zona_id=1", "csv"); throw new Exception("se esperaba error"); }
        catch (ApiError e) { Check(e.Status == 400 && e.Trace.StartsWith("9f2c"), "Descarga: el error XML del servicio llega con estado y traza"); }
        h.Custom = null; h.UnauthorizedOnce = true; var antes = h.Renewals;
        h.Custom = r => h.UnauthorizedOnce ? null : Archivo(pdf, "application/pdf", null, "r.pdf");
        Check((await api.Download("reportes", "reportes/x/exportar?formato=pdf", "pdf")).Nombre == "r.pdf" && h.Renewals == antes + 1, "Descarga: un 401 renueva una vez y repite");
        h.Custom = null;
        await RejectAsync(() => api.Download("reportes", "reportes/x/exportar?formato=doc", "doc"), "Descarga: un formato fuera de csv, xlsx y pdf ni se pide");
        foreach (var (srv, puerto) in new[] { ("cobertura", 5116), ("capacidad", 5117), ("rutas", 5118), ("costos", 5119), ("punto-equilibrio", 5120), ("simulacion", 5121), ("reportes", 5123) })
        {
            h.Custom = _ => new HttpResponseMessage(HttpStatusCode.OK) { Content = new StringContent(Ex("SupuestosCobertura.ok.xml"), System.Text.Encoding.UTF8, "application/xml") };
            await api.Call(srv, srv + "/supuestos", root: "supuestos_cobertura");
            if (h.Last!.Port != puerto) throw new Exception($"FALLA: {srv} → {h.Last.Port}");
        }
        h.Custom = null;
        Check(true, "Puertos: cobertura 5116, capacidad 5117, rutas 5118, costos 5119, equilibrio 5120, simulación 5121, reportes 5123");
        await RejectAsync(() => api.Call("cobertura", "cobertura/resumen", root: "otra_raiz"), "Una respuesta con otra raíz que la esperada se rechaza");
    }

    static HttpResponseMessage Archivo(byte[] cuerpo, string tipo, string? sha, string nombre)
    {
        var r = new HttpResponseMessage(HttpStatusCode.OK) { Content = new ByteArrayContent(cuerpo) };
        r.Content.Headers.ContentType = System.Net.Http.Headers.MediaTypeHeaderValue.Parse(tipo);
        r.Content.Headers.ContentDisposition = new System.Net.Http.Headers.ContentDispositionHeaderValue("attachment") { FileName = "\"" + nombre + "\"" };
        if (sha != null) r.Headers.Add("X-Reporte-SHA256", sha);
        r.Headers.Add("X-Reporte-Filas", "1");
        return r;
    }

    // ------------------------------------------------------------------------------------------ ventana
#if !SIN_VENTANA
    static void VentanaDeEscritorio()
    {
        Exception? startupError = null;
        var thread = new Thread(() =>
        {
            try
            {
                using var window = new MainWindow(); Check(window.Text.Contains("Planeación") && window.Controls.Count == 3, "Inicializa la ventana de escritorio");
                using var api = new Api { Demo = true };
                foreach (var m in Modulos.Todos)
                {
                    using var v = new VentanaModulo(api, m);
                    var botones = v.Controls.OfType<FlowLayoutPanel>().Single().Controls.OfType<Button>().ToList();
                    if (botones.Count != m.Acciones.Length + 1) throw new Exception($"FALLA: {m.Nombre} tiene {botones.Count} botones");
                }
                Check(true, "Inicializa las ventanas de cobertura, rutas, costos, capacidad, equilibrio y simulación con un botón por acción");
                using var r = new VentanaReportes(api);
                Check(r.Controls.OfType<FlowLayoutPanel>().Single().Controls.OfType<Button>().Count(b => b.Text.StartsWith("Descargar")) == 3, "Inicializa la ventana de reportes con las tres descargas");
            }
            catch (Exception e) { startupError = e; }
        });
        thread.SetApartmentState(ApartmentState.STA); thread.Start(); thread.Join();
        if (startupError != null) throw startupError;
    }
#endif

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

        Check((await plan.Call("productos", "productos?pagina=1&por_pagina=5&q=arroz")).Descendants(Api.Ns + "producto").Any(), "Catálogo: productos filtrados (XML válido)");
        var prod = (await plan.Call("productos", "productos?pagina=1&por_pagina=1")).Descendants(Api.Ns + "producto").First().Element(Api.Ns + "id")!.Value;
        Check((await plan.Call("productos", $"productos/{prod}")).Root!.Name == Api.Ns + "producto", "Catálogo: detalle de producto");
        Check((await plan.Call("zonas", "zonas")).Root!.Name == Api.Ns + "zonas" && (await plan.Call("microhubs", "microhubs")).Root!.Name == Api.Ns + "microhubs", "Catálogo: zonas y microhubs");
        var pedidos = await plan.Call("pedidos", "pedidos?pagina=1&por_pagina=5&estado=entregado");
        var pid = pedidos.Descendants(Api.Ns + "pedido").First().Element(Api.Ns + "id")!.Value;
        Check((await plan.Call("pedidos", $"pedidos/{pid}")).Descendants(Api.Ns + "linea").Any(), "Pedidos: detalle con líneas");
        Check((await plan.Call("pedidos", $"pedidos/{pid}/historial")).Root!.Name == Api.Ns + "historial", "Pedidos: historial");
        await RejectAsync(() => plan.Call("pedidos", "pedidos?estado=inventado"), "Pedidos: un filtro inválido da error 400");

        foreach (var (srv, recurso) in new[] { ("productos", "productos"), ("zonas", "zonas"), ("microhubs", "microhubs"), ("pedidos", "pedidos"), ("planeacion", "candidatos"), ("planeacion", "escenarios") })
        {
            var tabla = Tablas.ToTable(await plan.Call(srv, $"{recurso}?pagina=1&por_pagina=20&q="));
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
        var tablaEsc = Tablas.ToTable(listaEsc);
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

    // ------------------------------------------------------------------------------------------ 3c) operación del microhub contra el backend real
    static async Task OperacionReal(string host)
    {
        var clave = Environment.GetEnvironmentVariable("MICROHUBS_CLAVE")!;
        async Task<Api> Entrar(string correo)
        {
            var a = new Api { Host = host };
            a.SetSession(await a.Call("auth", "auth/login", HttpMethod.Post, Api.Body("login", ("correo", correo), ("clave", clave))));
            return a;
        }
        Console.WriteLine("-- Operación del microhub (operador) contra el backend real");
        using var op = await Entrar("operador.mh01@codex.mx");
        using var plan = await Entrar("planeador@codex.mx");
        Check(op.Puede("pedidos.cambiar_estado") && op.Puede("entregas.asignar") && !op.Puede("surtido.editar"), "Operador: la sesión trae sus permisos");

        // Consultas de las pantallas de operación, como operador
        foreach (var m in new[] { Modulos.Inventario, Modulos.Preparacion, Modulos.Despacho, Modulos.Surtido })
            foreach (var a in m.Acciones.Where(a => a.Metodo == "GET" && !a.PorFila && a.Formulario == null))
            {
                var t = Tablas.Principal(await op.Call(a.Servicio, a.Armar(), a.Http, root: a.Raiz));
                Check(true, $"{m.Nombre} · {a.Titulo}: <{a.Raiz}> válido, {t.Rows.Count} filas");
            }

        // Inventario: un ajuste con la plantilla oficial y un uuid nuevo (dos envíos = dos movimientos)
        var reg = Modulos.Inventario.Acciones.Single(a => a.Titulo == "Registrar movimiento");
        async Task<XElement> Ajuste(int cantidad) => (await op.Call(reg.Servicio, reg.Armar(), reg.Http, Plantillas.Aplicar(Plantillas.ConOperacionNueva(Api.Example(reg.Plantilla!)),
            new Dictionary<string, string> { ["tipo"] = "ajuste", ["cantidad"] = cantidad.ToString(), ["motivo"] = "Prueba del escritorio", ["referencia.tipo"] = "ajuste", ["referencia.id"] = "1" }),
            root: reg.Raiz)).Root!;
        var m1 = await Ajuste(1); var m2 = await Ajuste(-1);
        Check(m1.Descendants(Api.Ns + "duplicado").First().Value == "false" && m2.Descendants(Api.Ns + "duplicado").First().Value == "false", "Inventario · Registrar movimiento dos veces: dos movimientos (+1 y −1), ninguno duplicado");

        // Preparación → listo → asignación → manifiesto, todo en XML
        var prep = Modulos.Preparacion.Acciones;
        var porPreparar = Tablas.Principal(await op.Call("pedidos", prep[0].Armar(), root: prep[0].Raiz));
        var listos = Tablas.Principal(await op.Call("pedidos", "pedidos/listos?microhub_id=1", root: "pedidos_listos"));
        string? pid = null;
        if (porPreparar.Rows.Count > 0)
        {
            pid = porPreparar.Rows[0]["id"]!.ToString()!;
            var pasar = prep.Single(a => a.Titulo == "Pasar a preparación");
            var p1 = (await op.Call("pedidos", pasar.Armar(pid), pasar.Http, Plantillas.ConOperacionNueva(Api.Example(pasar.Plantilla!)), root: pasar.Raiz)).Root!;
            Check(p1.Element(Api.Ns + "estado")!.Value == "en_preparacion", $"Preparación · Pasar a preparación el pedido {pid} (XML pedido_estado_cambio)");
            var listo = prep.Single(a => a.Titulo == "Marcar listo");
            Check((await op.Call("pedidos", listo.Armar(pid), listo.Http, root: listo.Raiz)).Root!.Element(Api.Ns + "listo_en") != null, $"Preparación · Marcar listo el pedido {pid}");
        }
        else if (listos.Rows.Count > 0)
        {
            pid = listos.Rows[0]["id"]!.ToString()!;
            Console.WriteLine($"(Preparación: no hay pedidos asignados en el microhub 1; se despacha el pedido listo {pid})");
        }
        if (pid == null) Console.WriteLine("(Operación: no hay pedidos asignados ni listos en el microhub 1; corre preparar_listos)");
        else
        {
            var reps = Tablas.Principal(await op.Call("entregas", "entregas/repartidores", root: "repartidores"));
            var rid = reps.Rows[0]["id"]!.ToString()!;
            var asignar = Modulos.Despacho.Acciones.Single(a => a.Titulo == "Asignar repartidor");
            var asignada = (await op.Call("entregas", asignar.Armar(), asignar.Http, Operacion.Asignacion(pid, rid), root: asignar.Raiz)).Root!;
            Check(asignada.Element(Api.Ns + "asignadas")!.Value == "1", $"Despacho · Asignar el pedido {pid} al repartidor {rid} (XML asignacion_nueva)");
            await RejectAsync(() => op.Call("entregas", asignar.Armar(), asignar.Http, Operacion.Asignacion(pid, rid), root: asignar.Raiz), "Despacho · Un pedido que ya salió no se vuelve a despachar (409)");
            var man = Modulos.Despacho.Acciones.Single(a => a.Formulario == "manifiesto");
            var lista = await op.Call("entregas", man.Armar(null, man.Parametros + "&repartidor_id=" + rid), root: man.Raiz);
            var detalles = new List<XDocument>();
            foreach (var e in lista.Root!.Element(Api.Ns + "datos")!.Elements()) detalles.Add(await op.Call("entregas", "entregas/" + e.Element(Api.Ns + "id")!.Value, root: "entrega_detalle"));
            var tabla = Operacion.Manifiesto(detalles);
            Check(tabla.Rows.Cast<System.Data.DataRow>().Any(r => ((string)r["folio"]).EndsWith(pid.PadLeft(6, '0'))) && Operacion.TotalACobrar(tabla) > 0,
                  $"Despacho · Manifiesto del repartidor {rid}: {tabla.Rows.Count} paradas, incluye el pedido {pid}, total {Operacion.TotalACobrar(tabla):0.00}");
        }

        // Surtido y capacidad desde el escritorio
        var restr = Modulos.Surtido.Acciones.Single(a => a.Titulo == "Restricciones");
        Check((await op.Call("surtido", restr.Armar("1"), root: restr.Raiz)).Root!.Element(Api.Ns + "microhub") != null, "Surtido · Restricciones del microhub 1 (id pedido al no haber columna)");
        var colas = Modulos.Capacidad.Acciones.Single(a => a.Titulo == "Colas M/M/c");
        var c = (await op.Call("capacidad", colas.Armar(), colas.Http, Api.Example(colas.Plantilla!), root: colas.Raiz)).Root!;
        Check(c.Element(Api.Ns + "servidores_requeridos")!.Value == "4" && Tablas.Principal(c.Document!).Rows.Count >= 2, "Capacidad · Colas M/M/c con la plantilla oficial: 4 operadores para esperar ≤ 5 min");
        var cambiar = Modulos.Capacidad.Acciones.Single(a => a.Titulo == "Cambiar personal");
        await RejectAsync(() => op.Call("capacidad", cambiar.Armar("1"), cambiar.Http, Api.Example(cambiar.Plantilla!), root: cambiar.Raiz), "Capacidad · Cambiar personal: el operador no puede (403)");
        var antes = (await plan.Call("capacidad", "capacidad/recursos/1", root: "recurso_capacidad")).Root!;
        var cuerpo = Plantillas.Aplicar(Api.Example(cambiar.Plantilla!), new Dictionary<string, string> { ["operadores"] = antes.Element(Api.Ns + "operadores")!.Value,
            ["repartidores"] = antes.Element(Api.Ns + "repartidores")!.Value, ["capacidad_fisica"] = antes.Element(Api.Ns + "capacidad_fisica")!.Value });
        var despues = (await plan.Call("capacidad", cambiar.Armar("1"), cambiar.Http, cuerpo, root: cambiar.Raiz)).Root!;
        Check(despues.Element(Api.Ns + "operadores")!.Value == antes.Element(Api.Ns + "operadores")!.Value, "Capacidad · Cambiar personal como planeador (se deja igual que estaba)");
    }

    // ------------------------------------------------------------------------------------------ 3b) análisis y reportes contra el backend real
    static async Task AnalisisReal(string host)
    {
        var clave = Environment.GetEnvironmentVariable("MICROHUBS_CLAVE")!;
        async Task<Api> Entrar(string correo)
        {
            var a = new Api { Host = host };
            a.SetSession(await a.Call("auth", "auth/login", HttpMethod.Post, Api.Body("login", ("correo", correo), ("clave", clave))));
            return a;
        }
        Console.WriteLine("-- Pantallas de análisis y reportes contra el backend real");
        using var plan = await Entrar("planeador@codex.mx");

        // Cada consulta de cada pantalla (las que no dependen de una fila): XML válido con la raíz esperada y su tabla
        var operacion = new[] { Modulos.Inventario, Modulos.Preparacion, Modulos.Despacho };     // las de operación se prueban como operador (3c)
        foreach (var m in Modulos.Todos.Except(operacion))
            foreach (var a in m.Acciones.Where(a => a.Metodo == "GET" && !a.PorFila && a.Titulo != "Comparar" && a.Formulario == null))
            {
                var doc = await plan.Call(a.Servicio, a.Armar(), a.Http, root: a.Raiz);
                var t = Tablas.Principal(doc);
                Check(t.Columns.Count > 0 || t.Rows.Count == 0, $"{m.Nombre} · {a.Titulo}: <{a.Raiz}> válido, tabla de {t.Rows.Count} filas × {t.Columns.Count} columnas");
            }

        // Las que van sobre una fila, con la primera fila de su lista
        async Task<string?> PrimerId(Accion lista, string columna)
        {
            var t = Tablas.Principal(await plan.Call(lista.Servicio, lista.Armar(), root: lista.Raiz));
            return t.Rows.Count > 0 && t.Columns.Contains(columna) ? t.Rows[0][columna]?.ToString() : null;
        }
        var cap = Modulos.Capacidad.Acciones; var mid = await PrimerId(cap[0], "microhub/id");
        var det = await plan.Call("capacidad", cap[1].Armar(mid), root: cap[1].Raiz);
        Check(Tablas.Principal(det).Rows.Count > 0, $"Capacidad · Detalle del microhub {mid} (columna microhub/id de la lista)");

        // Envíos con las plantillas oficiales (los que no cambian datos de nadie)
        foreach (var (m, titulo) in new[] { (Modulos.Cobertura, "Evaluar ubicación"), (Modulos.Capacidad, "Simular"), (Modulos.Equilibrio, "Sensibilidad") })
        {
            var a = m.Acciones.Single(x => x.Titulo == titulo);
            var r = await plan.Call(a.Servicio, a.Armar(), a.Http, Api.Example(a.Plantilla!), root: a.Raiz);
            Check(Tablas.Principal(r).Rows.Count > 0, $"{m.Nombre} · {titulo}: la plantilla oficial se acepta y responde <{a.Raiz}>");
        }

        // Punto de equilibrio: calcular y guardar dos escenarios, abrir uno y compararlos
        var eq = Modulos.Equilibrio.Acciones; var calc = eq.Single(a => a.Titulo == "Calcular");
        var ids = new List<string>();
        foreach (var n in new[] { "A", "B" })
        {
            var cuerpo = Plantillas.Aplicar(Api.Example(calc.Plantilla!), new Dictionary<string, string> { ["nombre"] = "Prueba escritorio " + n + " " + DateTimeOffset.UtcNow.ToUnixTimeSeconds(), ["pedidos_dia"] = n == "A" ? "45" : "60" });
            var r = (await plan.Call(calc.Servicio, calc.Armar(), calc.Http, cuerpo, root: calc.Raiz)).Root!;
            ids.Add(r.Descendants(Api.Ns + "escenario_id").FirstOrDefault()?.Value ?? r.Element(Api.Ns + "id")?.Value ?? throw new Exception("FALLA: el cálculo guardado no trae id: " + r));
        }
        Check(ids.Count == 2, $"Equilibrio · Calcular y guardar dos escenarios ({string.Join(", ", ids)})");
        var abrir = eq.Single(a => a.Titulo == "Abrir escenario");
        Check((await plan.Call(abrir.Servicio, abrir.Armar(ids[0]), root: abrir.Raiz)).Root!.Name == Api.Ns + "equilibrio_calculo", "Equilibrio · Abrir escenario");
        var comp = eq.Single(a => a.Titulo == "Comparar");
        Check(Tablas.Principal(await plan.Call(comp.Servicio, comp.Armar(null, "ids=" + string.Join(",", ids)), root: comp.Raiz)).Rows.Count >= 2, "Equilibrio · Comparar los dos escenarios");

        // Simulación: crear, ver hasta que termine, repetir (misma huella) y comparar
        var sim = Modulos.Simulacion.Acciones; var nueva = sim.Single(a => a.Titulo == "Nueva simulación");
        var cuerpoSim = Plantillas.Aplicar(Api.Example(nueva.Plantilla!), new Dictionary<string, string> { ["nombre"] = "Prueba escritorio " + DateTimeOffset.UtcNow.ToUnixTimeSeconds(), ["replicas"] = "50", ["dias"] = "14" });
        var creada = (await plan.Call(nueva.Servicio, nueva.Armar(), nueva.Http, cuerpoSim, root: nueva.Raiz)).Root!;
        var sid = creada.Element(Api.Ns + "id")!.Value;
        var ver = sim.Single(a => a.Titulo == "Ver ejecución");
        async Task<XElement> Esperar(string id)
        {
            for (var i = 0; i < 60; i++)
            {
                var e = (await plan.Call(ver.Servicio, ver.Armar(id), root: ver.Raiz)).Root!;
                if (e.Element(Api.Ns + "estado")!.Value is "terminada" or "fallida" or "cancelada") return e;
                await Task.Delay(500);
            }
            throw new Exception("FALLA: la simulación no terminó en 30 s");
        }
        var terminada = await Esperar(sid);
        Check(terminada.Element(Api.Ns + "estado")!.Value == "terminada", $"Simulación · Nueva y Ver ejecución {sid}: terminó");
        var repetir = sim.Single(a => a.Titulo == "Repetir");
        var rid = (await plan.Call(repetir.Servicio, repetir.Armar(sid), repetir.Http, root: repetir.Raiz)).Root!.Element(Api.Ns + "id")!.Value;
        var repetida = await Esperar(rid);
        Check(repetida.Element(Api.Ns + "huella")?.Value == terminada.Element(Api.Ns + "huella")?.Value && terminada.Element(Api.Ns + "huella")?.Value is { Length: > 0 },
            "Simulación · Repetir con la misma semilla da la misma huella");
        var compS = sim.Single(a => a.Titulo == "Comparar");
        Check(Tablas.Principal(await plan.Call(compS.Servicio, compS.Armar(null, $"ids={sid},{rid}"), root: compS.Raiz)).Rows.Count >= 2, "Simulación · Comparar las dos ejecuciones");

        // Rutas: con los pedidos listos del microhub 1 (sin lista = todos): comparar métodos, proponer y guardar, abrir y cancelar
        var rutas = Modulos.Rutas.Acciones;
        var proponer = rutas.Single(a => a.Titulo == "Proponer plan"); var compR = rutas.Single(a => a.Titulo == "Comparar métodos");
        try
        {
            var cmp = await plan.Call("rutas", compR.Armar(), compR.Http, Plantillas.Aplicar(Api.Example(compR.Plantilla!), new Dictionary<string, string> { ["pedido_ids"] = "" }), root: compR.Raiz);
            Check(Tablas.Principal(cmp).Columns.Contains("metodo") && Tablas.Principal(cmp).Rows.Count == cmp.Root!.Element(Api.Ns + "filas")!.Elements().Count(),
                  $"Rutas · Comparar métodos con los pedidos listos: {Tablas.Principal(cmp).Rows.Count} métodos en la tabla principal");
            var cuerpo = Plantillas.Aplicar(Api.Example(proponer.Plantilla!), new Dictionary<string, string> { ["pedido_ids"] = "", ["repartidor_ids"] = "", ["guardar"] = "true" });
            var pr = (await plan.Call("rutas", proponer.Armar(), proponer.Http, cuerpo, root: proponer.Raiz)).Root!;
            var pid2 = pr.Element(Api.Ns + "id")!.Value;
            Check(Tablas.Principal(pr.Document!).Rows.Count > 0, $"Rutas · Proponer y guardar el plan {pid2} ({pr.Element(Api.Ns + "estado")?.Value})");
            var abrirP = rutas.Single(a => a.Titulo == "Abrir plan"); var cancelar = rutas.Single(a => a.Titulo == "Cancelar plan");
            Check((await plan.Call("rutas", abrirP.Armar(pid2), root: abrirP.Raiz)).Root!.Element(Api.Ns + "id")!.Value == pid2, "Rutas · Abrir plan");
            var cancelado = (await plan.Call("rutas", cancelar.Armar(pid2), cancelar.Http, root: cancelar.Raiz)).Root!;
            Check(cancelado.Element(Api.Ns + "estado")!.Value == "cancelado", "Rutas · Cancelar plan (POST sin cuerpo)");
            Check(Tablas.Principal(await plan.Call("rutas", rutas[0].Armar(), root: rutas[0].Raiz)).Rows.Count >= 1, "Rutas · Planes: aparece el plan guardado");
        }
        catch (ApiError e) when (e.Status is 409 or 422) { Console.WriteLine($"(Rutas: sin pedidos listos en el microhub 1 para proponer un plan: {e.Message})"); }

        // Costos: alta de un concepto con la plantilla oficial y baja lógica
        var nuevoC = Modulos.Costos.Acciones.Single(a => a.Titulo == "Nuevo concepto");
        var concepto = (await plan.Call("costos", nuevoC.Armar(), nuevoC.Http, Plantillas.Aplicar(Api.Example(nuevoC.Plantilla!),
            new Dictionary<string, string> { ["nombre"] = "Prueba escritorio " + DateTimeOffset.UtcNow.ToUnixTimeSeconds(), ["categoria"] = "otros", ["monto"] = "10" }), root: nuevoC.Raiz)).Root!;
        Check(concepto.Element(Api.Ns + "id") != null, "Costos · Nuevo concepto con la plantilla oficial");
        await plan.Call("costos", "costos/conceptos/" + concepto.Element(Api.Ns + "id")!.Value, HttpMethod.Delete);
        Check(true, "Costos · baja lógica del concepto de prueba");

        // Reportes: catálogo, cada reporte con su tabla y su gráfica, y las tres descargas
        var catalogo = await plan.Call("reportes", Modulos.Catalogo.Armar(), root: Modulos.Catalogo.Raiz);
        var claves = catalogo.Descendants(Api.Ns + "reporte").Select(r => r.Element(Api.Ns + "clave")!.Value).ToList();
        Check(claves.Count >= 8, $"Reportes · Catálogo con {claves.Count} reportes");
        var hasta = DateTime.Today; var desde = hasta.AddDays(-60);
        foreach (var k in claves)
        {
            var admite = Tablas.FiltrosDe(catalogo, k);
            var rep = await plan.Call("reportes", Tablas.ConsultaReporte(k, "", desde, hasta, null, null, null, admite), root: "reporte");
            var t = Tablas.Reporte(rep);
            Check(t.Columns.Count == rep.Descendants(Api.Ns + "columna").Count(), $"Reporte {k}: {t.Rows.Count} filas (con totales) × {t.Columns.Count} columnas");
            var g = Tablas.Grafica(await plan.Call("reportes", Tablas.ConsultaReporte(k, "/grafica", desde, hasta, null, null, null, admite), root: "grafica"));
            Check(g.Columns.Count >= 2, $"Gráfica {k}: {g.Rows.Count} categorías × {g.Columns.Count - 1} series");
        }
        Check(Tablas.Principal(await plan.Call("reportes", Modulos.Indicadores.Armar(), root: Modulos.Indicadores.Raiz)).Rows.Count > 0, "Reportes · Indicadores");
        var tamanos = new List<string>();
        foreach (var f in new[] { "csv", "xlsx", "pdf" })
        {
            var arch = await plan.Download("reportes", Tablas.ConsultaReporte("pedidos_por_dia", "/exportar", desde, hasta, null, null, f), f);
            var sha = Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(arch.Contenido)).ToLowerInvariant();
            Check(arch.Nombre.StartsWith("pedidos_por_dia_") && arch.Nombre.EndsWith("." + f) && sha == arch.Sha256 && Api.Signature(f, arch.Contenido),
                $"Descarga {f.ToUpperInvariant()}: {arch.Nombre}, {arch.Contenido.Length} bytes, {arch.Filas} filas, SHA-256 verificado");
            var destino = Environment.GetEnvironmentVariable("MICROHUBS_DESCARGAS");
            if (!string.IsNullOrEmpty(destino)) { Directory.CreateDirectory(destino); File.WriteAllBytes(Path.Combine(destino, arch.Nombre), arch.Contenido); }
            tamanos.Add(arch.Sha256);
        }
        var bitacora = await plan.Call("reportes", Modulos.Exportaciones.Armar(), root: Modulos.Exportaciones.Raiz);
        Check(tamanos.All(sha => bitacora.Descendants(Api.Ns + "sha256").Any(e => e.Value == sha)), "Reportes · Exportaciones: la bitácora registra las tres descargas con su SHA-256");
        try { await plan.Download("reportes", "reportes/no_existe/exportar?formato=csv", "csv"); throw new Exception("descargó un reporte inexistente"); }
        catch (ApiError e) { Check(e.Status == 404, "Descarga de un reporte que no existe: 404 en XML"); }
        try { await plan.Download("reportes", "reportes/pedidos_por_dia/exportar?formato=csv&zona_id=abc", "csv"); throw new Exception("aceptó un filtro inválido"); }
        catch (ApiError e) { Check(e.Status == 400, "Descarga con un filtro inválido: 400 en XML"); }

        // Permisos: el auditor consulta y descarga, pero no ve simulaciones
        using var aud = await Entrar("auditor@codex.mx");
        Check((await aud.Download("reportes", Tablas.ConsultaReporte("pedidos_por_zona", "/exportar", desde, hasta, null, null, "csv"), "csv")).Contenido.Length > 0, "Auditor: descarga un reporte");
        Check(Tablas.Principal(await aud.Call("costos", Modulos.Costos.Acciones[1].Armar(), root: Modulos.Costos.Acciones[1].Raiz)).Rows.Count > 0, "Auditor: consulta costos");
        try { await aud.Call("simulacion", sim[0].Armar(), root: sim[0].Raiz); throw new Exception("auditor vio simulaciones"); }
        catch (ApiError e) { Check(e.Status == 403, "Auditor: simulaciones → 403 (sin simulacion.ver)"); }
    }

    sealed class FakeHandler : HttpMessageHandler
    {
        public Uri? Last; public string? Accept, Authorization; public bool UnauthorizedOnce, WrongContent, RenewalFails; public int Renewals, Calls, SlowUnauthorized, RetryAfter;
        public (HttpStatusCode code, string body)? Next;
        public Func<HttpRequestMessage, HttpResponseMessage?>? Custom;
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
            if (Custom?.Invoke(request) is { } propia) return propia;
            if (Next is { } n) { Next = null; var r = Xml(n.code, n.body); if (RetryAfter > 0) r.Headers.RetryAfter = new System.Net.Http.Headers.RetryConditionHeaderValue(TimeSpan.FromSeconds(RetryAfter)); return r; }
            if (WrongContent) return new HttpResponseMessage(HttpStatusCode.OK) { Content = new StringContent("{}", Encoding.UTF8, "application/json") };
            var ruta = Last.AbsolutePath;
            return Xml(HttpStatusCode.OK, Ex(ruta.EndsWith("/productos") ? "ProductoLista.ok.xml" : ruta.EndsWith("/zonas") ? "ZonaLista.ok.xml" : ruta.EndsWith("/microhubs") ? "MicrohubLista.ok.xml" : ruta.EndsWith("/candidatos") ? "CandidatoLista.ok.xml" : "PedidoLista.ok.xml"));
        }
        static HttpResponseMessage Xml(HttpStatusCode code, string body) => new(code) { Content = new StringContent(body, Encoding.UTF8, "application/xml") };
    }
}
