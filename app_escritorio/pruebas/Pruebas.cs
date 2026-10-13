using System.Net;
using System.Net.Http;
using System.Text;
using System.Xml.Linq;

namespace Microhubs;

static class Pruebas
{
    static int total;
    static void Check(bool value, string name) { if (!value) throw new Exception(name); Console.WriteLine("PASA: " + name); total++; }
    static void Reject(Action action, string name) { try { action(); } catch { Check(true, name); return; } throw new Exception("Se aceptó: " + name); }
    static string Session(long expiration)
    {
        var payload = Convert.ToBase64String(Encoding.UTF8.GetBytes($"{{\"exp\":{expiration}}}")).TrimEnd('=').Replace('+','-').Replace('/','_');
        return Api.Body("sesion", ("token_acceso", "header." + payload + ".signature"), ("token_renovacion", "refresh"), ("expira_en", "900"),
            ("usuario", "")).ToString().Replace("<usuario></usuario>", "<usuario><id>1</id><nombre>Prueba</nombre><rol>planeador</rol><microhub_id>1</microhub_id></usuario>")
            .Replace("<usuario />", "<usuario><id>1</id><nombre>Prueba</nombre><rol>planeador</rol><microhub_id>1</microhub_id></usuario>");
    }
    static async Task Main()
    {
        using var demo = new Api { Demo = true };
        demo.SetSession(await demo.Call("auth", "auth/login", HttpMethod.Post));
        Check(demo.Role == "planeador", "Login de ejemplo");
        await demo.Call("planeacion", "candidatos", HttpMethod.Post, Api.Body("candidato", ("nombre", "Candidato QA")));
        var lista = await demo.Call("planeacion", "candidatos");
        Check(lista.Descendants(Api.Ns+"candidato").Count()==2, "Crear candidato persiste en memoria");
        await demo.Call("planeacion", "candidatos/2", HttpMethod.Put, Api.Body("candidato", ("nombre", "Modificado")));
        lista = await demo.Call("planeacion", "candidatos");
        Check(lista.Descendants(Api.Ns+"nombre").Any(n=>n.Value=="Modificado"), "Modificar candidato");
        var simulation = await demo.Call("planeacion", "candidatos/2/simular", HttpMethod.Post);
        Check(simulation.Root!.Element(Api.Ns+"candidato_id")!.Value=="2", "Simulación usa el ID seleccionado");
        Check((await demo.Call("catalogos","productos")).Descendants(Api.Ns+"producto").Any(),"Consulta catálogo XML");
        Check((await demo.Call("pedidos","pedidos?estado=entregado")).Descendants(Api.Ns+"pedido").Any(),"Consulta pedidos XML");
        Reject(()=>demo.Validate("<sesion xmlns='urn:microhubs:v1'/>"),"XSD rechaza sesión incompleta");
        Reject(()=>demo.Validate("<!DOCTYPE x [<!ENTITY x SYSTEM 'file:///C:/Windows/win.ini'>]><resultado xmlns='urn:microhubs:v1'><mensaje>&x;</mensaje></resultado>"),"Rechaza DTD y entidades externas");
        var handler = new FakeHandler(); using var real = new Api(handler);
        real.SetSession(real.Validate(Session(DateTimeOffset.UtcNow.ToUnixTimeSeconds()+900)));
        Check(real.Access!="", "Acepta JWT vigente devuelto por el servicio");
        await real.Call("pedidos","pedidos?estado=entregado&pagina=2");
        Check(handler.Last!.Query.Contains("pagina=2") && !handler.Last.AbsolutePath.Contains('?'),"Conserva query y puerto del servicio");
        Check(handler.Last.Port==5104 && handler.Accept=="application/xml", "Solo solicita XML al servicio correcto");
        handler.UnauthorizedOnce=true;
        await real.Call("pedidos","pedidos");
        Check(handler.Renewals==1,"401 renueva una vez y reintenta");
        handler.WrongContent=true;
        try { await real.Call("pedidos","pedidos"); throw new Exception("JSON aceptado"); } catch (Exception e) { Check(e.Message.Contains("application/xml"),"Rechaza respuestas JSON"); }
        Reject(()=>real.SetSession(real.Validate(Session(1))),"Rechaza JWT vencido");
        Check(real.Access=="" && real.Refresh=="", "Sesión rechazada no conserva credenciales");
        Exception? startupError = null;
        var thread = new Thread(() => { try { using var window = new MainWindow(); Check(window.Text.Contains("Planeación") && window.Controls.Count==3,"Inicializa la ventana de escritorio"); } catch(Exception e) { startupError=e; } });
        thread.SetApartmentState(ApartmentState.STA); thread.Start(); thread.Join();
        if (startupError!=null) throw startupError;
        demo.Clear(); Check(demo.Access=="" && demo.Refresh=="" && demo.Role=="","Salir borra credenciales");
        Console.WriteLine($"{total} comprobaciones aprobadas");
    }
    sealed class FakeHandler : HttpMessageHandler
    {
        public Uri? Last; public string? Accept; public bool UnauthorizedOnce,WrongContent; public int Renewals;
        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request,CancellationToken cancellationToken)
        {
            Last=request.RequestUri; Accept=request.Headers.Accept.ToString();
            if (UnauthorizedOnce) { UnauthorizedOnce=false; return Task.FromResult(new HttpResponseMessage(HttpStatusCode.Unauthorized)); }
            if (Last!.AbsolutePath.EndsWith("renovar")) { Renewals++; return Xml(Session(DateTimeOffset.UtcNow.ToUnixTimeSeconds()+900)); }
            if (WrongContent) return Task.FromResult(new HttpResponseMessage(HttpStatusCode.OK){Content=new StringContent("{}",Encoding.UTF8,"application/json")});
            return Xml(File.ReadAllText(Path.Combine(AppContext.BaseDirectory,"contratos","lista.xml")));
        }
        static Task<HttpResponseMessage> Xml(string body)=>Task.FromResult(new HttpResponseMessage(HttpStatusCode.OK){Content=new StringContent(body,Encoding.UTF8,"application/xml")});
    }
}
