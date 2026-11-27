using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Security.Cryptography;
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

/// <summary>Un archivo descargado (reportes en CSV, Excel o PDF): nombre sugerido, tipo, bytes y su SHA-256.</summary>
sealed record Archivo(string Nombre, string Tipo, byte[] Contenido, string Sha256, int? Filas);

sealed class Api : IDisposable
{
    /// <summary>Puerto de cada servicio del contrato v1 que usa el escritorio.</summary>
    internal static readonly Dictionary<string,int> Puertos = new()
    {
        {"auth",5101},{"productos",5103},{"pedidos",5104},{"planeacion",5106},{"zonas",5108},{"microhubs",5109},
        {"cobertura",5116},{"capacidad",5117},{"rutas",5118},{"costos",5119},{"punto-equilibrio",5120},{"simulacion",5121},{"reportes",5123}
    };
    /// <summary>Formatos que entrega GET /reportes/{clave}/exportar y el tipo MIME que debe traer la respuesta.</summary>
    internal static readonly Dictionary<string,string> Formatos = new()
    {
        {"csv","text/csv"},{"xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},{"pdf","application/pdf"}
    };
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
    /// <param name="root">Raíz XML esperada en la respuesta; si se omite se deduce de la ruta (pantallas originales).</param>
    public async Task<XDocument> Call(string service,string path,HttpMethod? method=null,XElement? body=null,bool retry=true,string? root=null)
    {
        method ??= HttpMethod.Get;
        if(body!=null) Validate(body.ToString());
        if(Demo)
        {
            root??=RootFor(path,method);
            var file=Directory.GetFiles(Path.Combine(AppContext.BaseDirectory,"contratos","ejemplos"),"*.xml").FirstOrDefault(f=>XDocument.Load(f).Root?.Name==Ns+root);
            if(file==null) throw new Exception("No hay ejemplo oficial para "+root);
            var example=Validate(File.ReadAllText(file),root);
            if(path=="auth/login") example.Root!.Descendants(Ns+"rol").Single().Value="planeador"; // la demostración local entra como planeación
            return example;
        }
        var sentToken=Access;
        using var req=Request(service,path,method,"application/xml",sentToken);
        if(body!=null) req.Content=new StringContent(body.ToString(),Encoding.UTF8,"application/xml");
        using var response=await http.SendAsync(req);
        if(response.StatusCode==HttpStatusCode.Unauthorized && retry && Refresh!="" && !path.StartsWith("auth/"))
        {
            await Renew(sentToken);
            return await Call(service,path,method,body,false,root);
        }
        if(response.StatusCode==HttpStatusCode.NoContent && response.IsSuccessStatusCode) return new XDocument();
        RememberRetry(response);
        if(response.Content.Headers.ContentType?.MediaType!="application/xml") throw new Exception("El servicio no devolvió application/xml.");
        var doc=Validate(await response.Content.ReadAsStringAsync(),response.IsSuccessStatusCode?root??RootFor(path,method):"error");
        if(!response.IsSuccessStatusCode) throw ToError(response,doc);
        return doc;
    }

    /// <summary>
    /// Descarga un archivo binario (GET /reportes/{clave}/exportar?formato=csv|xlsx|pdf). No pasa por <see cref="Call"/> porque
    /// la respuesta no es XML; los errores sí llegan en XML y se validan igual. Verifica el tipo, la firma del archivo y el SHA-256
    /// que manda el servicio en X-Reporte-SHA256.
    /// </summary>
    public async Task<Archivo> Download(string service,string path,string format,bool retry=true)
    {
        if(!Formatos.TryGetValue(format,out var type)) throw new Exception("Formato no soportado: "+format);
        if(Demo) return DemoFile(path,format,type);
        var sentToken=Access;
        using var req=Request(service,path,HttpMethod.Get,type,sentToken);
        req.Headers.Accept.Add(new MediaTypeWithQualityHeaderValue("application/xml",0.5));   // los errores llegan en XML
        using var response=await http.SendAsync(req,HttpCompletionOption.ResponseHeadersRead);
        if(response.StatusCode==HttpStatusCode.Unauthorized && retry && Refresh!="")
        {
            await Renew(sentToken);
            return await Download(service,path,format,false);
        }
        RememberRetry(response);
        var media=response.Content.Headers.ContentType?.MediaType;
        if(!response.IsSuccessStatusCode)
        {
            if(media!="application/xml") throw new Exception($"El servicio respondió {(int)response.StatusCode} sin el error XML del contrato.");
            throw ToError(response,Validate(await response.Content.ReadAsStringAsync(),"error"));
        }
        if(media!=type) throw new Exception($"Se esperaba {type} y el servicio devolvió {media ?? "(sin tipo)"}.");
        var bytes=await response.Content.ReadAsByteArrayAsync();
        if(!Signature(format,bytes)) throw new Exception($"El archivo no parece un {format.ToUpperInvariant()} válido.");
        var sha=Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
        var declared=response.Headers.TryGetValues("X-Reporte-SHA256",out var v)?v.FirstOrDefault():null;
        if(declared!=null && !string.Equals(declared,sha,StringComparison.OrdinalIgnoreCase)) throw new Exception("El archivo llegó incompleto o alterado: su SHA-256 no coincide con el del servicio.");
        int? rows=response.Headers.TryGetValues("X-Reporte-Filas",out var f) && int.TryParse(f.FirstOrDefault(),out var n)?n:null;
        var name=SafeName(response.Content.Headers.ContentDisposition?.FileNameStar ?? response.Content.Headers.ContentDisposition?.FileName, path, format);
        return new Archivo(name,type,bytes,sha,rows);
    }

    /// <summary>CSV que empieza con BOM o texto; XLSX es un ZIP (PK\x03\x04); PDF empieza con %PDF-.</summary>
    internal static bool Signature(string format,byte[] b) => format switch
    {
        "xlsx" => b.Length>4 && b[0]==0x50 && b[1]==0x4B && b[2]==0x03 && b[3]==0x04,
        "pdf" => b.Length>5 && Encoding.ASCII.GetString(b,0,5)=="%PDF-",
        _ => b.Length>0 && !b.Take(4096).Contains((byte)0)
    };

    /// <summary>Nombre de archivo sin rutas ni caracteres inválidos; si el servicio no manda uno, se arma con la clave del reporte.</summary>
    internal static string SafeName(string? suggested,string path,string format)
    {
        var name=Path.GetFileName((suggested??"").Trim('"',' '));
        foreach(var c in Path.GetInvalidFileNameChars().Concat(new[]{'/','\\',':'})) name=name.Replace(c,'_');
        if(string.IsNullOrWhiteSpace(name) || name.Trim('.','_')=="") name=path.Split('?')[0].Split('/').Reverse().Skip(1).FirstOrDefault()??"reporte";
        return name.EndsWith("."+format,StringComparison.OrdinalIgnoreCase)?name:name+"."+format;
    }

    /// <summary>Con «Ejemplos oficiales» solo se puede armar el CSV del reporte de ejemplo; Excel y PDF los genera el servicio.</summary>
    static Archivo DemoFile(string path,string format,string type)
    {
        if(format!="csv") throw new Exception("Con ejemplos oficiales solo se descarga CSV; Excel y PDF los genera el servicio de reportes.");
        var doc=XDocument.Load(Path.Combine(AppContext.BaseDirectory,"contratos","ejemplos","Reporte.ok.xml"));
        var csv=new StringBuilder();
        string Line(IEnumerable<string> cells)=>string.Join(",",cells.Select(c=>c.Contains(',')||c.Contains('"')?"\""+c.Replace("\"","\"\"")+"\"":c));
        csv.AppendLine(Line(doc.Descendants(Ns+"columna").Select(c=>c.Element(Ns+"titulo")!.Value)));
        foreach(var row in doc.Descendants(Ns+"fila")) csv.AppendLine(Line(row.Descendants(Ns+"celda").Select(c=>c.Value)));
        var bytes=Encoding.UTF8.GetBytes(csv.ToString());
        return new Archivo(SafeName(null,path,format),type,bytes,Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant(),doc.Descendants(Ns+"fila").Count());
    }

    HttpRequestMessage Request(string service,string path,HttpMethod method,string accept,string token)
    {
        if(DateTimeOffset.UtcNow<retryAt) throw new Exception($"Espera {Math.Ceiling((retryAt-DateTimeOffset.UtcNow).TotalSeconds)} segundos antes de reintentar.");
        var host=new Uri(Host);
        if(host.Scheme!="https" && !(host.Scheme=="http" && host.IsLoopback)) throw new Exception("Usa HTTPS; HTTP solo se permite en localhost.");
        if(host.UserInfo!="") throw new Exception("Host inválido.");
        if(!Puertos.TryGetValue(service,out var port)) throw new Exception("Servicio desconocido: "+service);
        var parts=path.Split('?',2); var uri=new UriBuilder(host){Port=port,Path="/api/v1/"+parts[0],Query=parts.Length==2?parts[1]:""};
        var req=new HttpRequestMessage(method,uri.Uri);
        req.Headers.Accept.Add(new MediaTypeWithQualityHeaderValue(accept));
        if(token!="") req.Headers.Authorization=new AuthenticationHeaderValue("Bearer",token);
        return req;
    }

    /// <summary>Una sola renovación a la vez: quien llegue después ya encuentra los tokens nuevos.</summary>
    async Task Renew(string sentToken)
    {
        await renewal.WaitAsync();
        try { if(Access==sentToken) SetSession(await Call("auth","auth/renovar",HttpMethod.Post,Body("renovar",("token_renovacion",Refresh)),false)); }
        catch { Clear(); throw; } finally { renewal.Release(); }
    }

    void RememberRetry(HttpResponseMessage response)
    {
        if(response.StatusCode==(HttpStatusCode)429)
            retryAt=response.Headers.RetryAfter?.Date ?? DateTimeOffset.UtcNow+(response.Headers.RetryAfter?.Delta ?? TimeSpan.FromSeconds(60));
    }

    ApiError ToError(HttpResponseMessage response,XDocument doc)
    {
        LastTrace=doc.Root!.Element(Ns+"traza_id")?.Value??"";
        var fields=doc.Descendants(Ns+"detalle").ToDictionary(e=>e.Element(Ns+"campo")!.Value,e=>e.Element(Ns+"mensaje")!.Value);
        if(response.StatusCode==HttpStatusCode.Unauthorized) Clear();
        return new ApiError((int)response.StatusCode,doc.Root.Element(Ns+"mensaje")!.Value,fields,LastTrace);
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
