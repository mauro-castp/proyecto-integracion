using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Xml;
using System.Xml.Linq;
using System.Xml.Schema;

namespace Microhubs;

sealed class ApiError(int status, string message, Dictionary<string,string> fields, string trace) : Exception(message)
{
    public int Status { get; } = status;
    public Dictionary<string,string> Fields { get; } = fields;
    public string Trace { get; } = trace;
}

sealed class Api : IDisposable
{
    internal static readonly XNamespace Ns = "urn:microhubs:v1";
    readonly HttpClient http;
    readonly XmlSchemaSet schemas = new() { XmlResolver = null };
    readonly SemaphoreSlim renewal = new(1,1);
    DateTimeOffset retryAt;
    public string Access = "", Refresh = "", Role = "";
    public bool Demo;
    public string Host = "http://localhost";
    public string LastTrace { get; private set; } = "";
    public Api(HttpMessageHandler? handler = null)
    {
        http = handler == null ? new HttpClient() : new HttpClient(handler);
        http.Timeout = TimeSpan.FromSeconds(25);
        foreach (var file in Directory.GetFiles(Path.Combine(AppContext.BaseDirectory,"contratos"),"*.xsd"))
        {
            using var reader = XmlReader.Create(file, new XmlReaderSettings { DtdProcessing=DtdProcessing.Prohibit, XmlResolver=null });
            schemas.Add(XmlSchema.Read(reader, (_,e)=>throw new XmlSchemaException(e.Message))!);
        }
        schemas.Compile();
    }
    public static XElement Body(string name, params (string key,string value)[] fields) => new(Ns+name, fields.Select(f=>new XElement(Ns+f.key,f.value)));
    /// <summary>Ejemplo oficial del contrato (carpeta contratos/ejemplos), p. ej. "CandidatoNuevo.ok.xml".</summary>
    public static XElement Example(string name) => XDocument.Load(Path.Combine(AppContext.BaseDirectory,"contratos","ejemplos",name)).Root!;
    public XDocument Validate(string xml, string? expected=null)
    {
        using var reader=XmlReader.Create(new StringReader(xml),new XmlReaderSettings { DtdProcessing=DtdProcessing.Prohibit,XmlResolver=null,MaxCharactersInDocument=2_000_000 });
        var doc=XDocument.Load(reader);
        if(doc.Root?.Name.Namespace!=Ns || !schemas.GlobalElements.Contains(new XmlQualifiedName(doc.Root.Name.LocalName,Ns.NamespaceName))) throw new XmlSchemaValidationException("Raíz XML desconocida.");
        if(expected!=null && doc.Root.Name!=Ns+expected) throw new XmlSchemaValidationException($"Se esperaba {expected}.");
        doc.Validate(schemas,(_,e)=>throw new XmlSchemaValidationException(e.Message)); return doc;
    }
    static string RootFor(string path, HttpMethod method)
    {
        var p=path.Split('?')[0].Split('/');
        if(p[0]=="auth") return p[1] switch { "login"=>"sesion", "renovar"=>"tokens", "validar"=>"validacion", _=>"salir" };
        if(p[^1]=="simular" || p[0]=="simulaciones" && method==HttpMethod.Post) return "resultados";
        if(p[^1]=="resumen") return "simulaciones_resumen";
        if(p[^1]=="historial") return "historial";
        if(p[0]=="pedidos" && p.Length>1) return "pedido_detalle";
        if(p.Length==1 && method==HttpMethod.Get) return p[0];
        return p[0] switch { "productos"=>"producto", "candidatos"=>"candidato", "escenarios"=>"escenario", "zonas"=>"zona", "microhubs"=>"microhub", _=>p[0] };
    }
    public async Task<XDocument> Call(string service,string path,HttpMethod? method=null,XElement? body=null,bool retry=true)
    {
        method ??= HttpMethod.Get;
        if(body!=null) Validate(body.ToString());
        if(Demo)
        {
            var root=RootFor(path,method);
            var file=Directory.GetFiles(Path.Combine(AppContext.BaseDirectory,"contratos","ejemplos"),"*.xml").FirstOrDefault(f=>XDocument.Load(f).Root?.Name==Ns+root);
            if(file==null) throw new Exception("No hay ejemplo oficial para "+root);
            var example=Validate(File.ReadAllText(file),root);
            if(path=="auth/login") example.Root!.Descendants(Ns+"rol").Single().Value="planeador"; // la demostración local entra como planeación
            return example;
        }
        if(DateTimeOffset.UtcNow<retryAt) throw new Exception($"Espera {Math.Ceiling((retryAt-DateTimeOffset.UtcNow).TotalSeconds)} segundos antes de reintentar.");
        var ports=new Dictionary<string,int>{{"auth",5101},{"catalogos",5103},{"pedidos",5104},{"planeacion",5106}};
        var host=new Uri(Host);
        if(host.Scheme!="https" && !(host.Scheme=="http" && host.IsLoopback)) throw new Exception("Usa HTTPS; HTTP solo se permite en localhost.");
        if(host.UserInfo!="") throw new Exception("Host inválido.");
        var parts=path.Split('?',2); var uri=new UriBuilder(host){Port=ports[service],Path="/api/v1/"+parts[0],Query=parts.Length==2?parts[1]:""};
        var sentToken=Access;
        using var req=new HttpRequestMessage(method,uri.Uri);
        req.Headers.Accept.Add(new MediaTypeWithQualityHeaderValue("application/xml"));
        if(sentToken!="") req.Headers.Authorization=new AuthenticationHeaderValue("Bearer",sentToken);
        if(body!=null) req.Content=new StringContent(body.ToString(),Encoding.UTF8,"application/xml");
        using var response=await http.SendAsync(req);
        if(response.StatusCode==HttpStatusCode.Unauthorized && retry && Refresh!="" && !path.StartsWith("auth/"))
        {
            await renewal.WaitAsync();
            try { if(Access==sentToken) SetSession(await Call("auth","auth/renovar",HttpMethod.Post,Body("renovar",("token_renovacion",Refresh)),false)); }
            catch { Clear(); throw; } finally { renewal.Release(); }
            return await Call(service,path,method,body,false);
        }
        if(response.StatusCode==HttpStatusCode.NoContent && response.IsSuccessStatusCode) return new XDocument();
        if(response.StatusCode==(HttpStatusCode)429)
            retryAt=response.Headers.RetryAfter?.Date ?? DateTimeOffset.UtcNow+(response.Headers.RetryAfter?.Delta ?? TimeSpan.FromSeconds(60));
        if(response.Content.Headers.ContentType?.MediaType!="application/xml") throw new Exception("El servicio no devolvió application/xml.");
        var doc=Validate(await response.Content.ReadAsStringAsync(),response.IsSuccessStatusCode?RootFor(path,method):"error");
        if(!response.IsSuccessStatusCode)
        {
            LastTrace=doc.Root!.Element(Ns+"traza_id")?.Value??"";
            var fields=doc.Descendants(Ns+"detalle").ToDictionary(e=>e.Element(Ns+"campo")!.Value,e=>e.Element(Ns+"mensaje")!.Value);
            if(response.StatusCode==HttpStatusCode.Unauthorized) Clear();
            throw new ApiError((int)response.StatusCode,doc.Root.Element(Ns+"mensaje")!.Value,fields,LastTrace);
        }
        return doc;
    }
    public void SetSession(XDocument doc)
    {
        var root=doc.Root!;
        if(root.Name!=Ns+"sesion" && root.Name!=Ns+"tokens") throw new Exception("Sesión inválida.");
        var role=root.Name==Ns+"tokens"?Role:root.Descendants(Ns+"rol").Single().Value;
        var access=root.Element(Ns+"token_acceso")!.Value; var refresh=root.Element(Ns+"token_renovacion")!.Value;
        if(string.IsNullOrWhiteSpace(access)||string.IsNullOrWhiteSpace(refresh)||role=="") { Clear();throw new Exception("Sesión incompleta."); }
        Access=access;Refresh=refresh;Role=role;
    }
    public void Clear(){Access=Refresh=Role="";}
    public void Dispose(){http.Dispose();renewal.Dispose();}
}
