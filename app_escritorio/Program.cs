using System.Data;
using System.Net.Http;
using System.Xml.Linq;
namespace Microhubs;
static class Program { [STAThread] static void Main(){ApplicationConfiguration.Initialize();Application.Run(new MainWindow());} }
sealed class MainWindow : Form
{
    readonly Api api=new();
    readonly FlowLayoutPanel bar=new(){Dock=DockStyle.Top,AutoSize=true,WrapContents=true};
    readonly DataGridView grid=new(){Dock=DockStyle.Fill,ReadOnly=true,AutoSizeColumnsMode=DataGridViewAutoSizeColumnsMode.DisplayedCells,AllowUserToAddRows=false};
    readonly TextBox mail=new(){PlaceholderText="Correo",Width=180},password=new(){PlaceholderText="Clave",UseSystemPasswordChar=true},host=new(){Text="http://localhost",Width=170},search=new(){PlaceholderText="Buscar",Width=130};
    readonly CheckBox demo=new(){Text="Ejemplos oficiales",Checked=false,AutoSize=true};
    readonly ComboBox state=new(){DropDownStyle=ComboBoxStyle.DropDownList,Width=130};
    readonly DateTimePicker desde=new(){Format=DateTimePickerFormat.Short,ShowCheckBox=true,Checked=false},hasta=new(){Format=DateTimePickerFormat.Short,ShowCheckBox=true,Checked=false};
    readonly Label status=new(){Dock=DockStyle.Bottom,Height=50,Text="Sin sesión"};
    readonly List<(Button button,bool write)> secured=new();
    XDocument? latest; string service="",resource=""; int page=1,pages=1;
    public MainWindow()
    {
        Text="Microhubs · Planeación XML v1";Width=1250;Height=760;
        Controls.Add(grid);Controls.Add(bar);Controls.Add(status);
        bar.Controls.AddRange(new Control[]{host,demo,mail,password});
        Add("Entrar",async()=>{
            api.Clear(); api.Demo=demo.Checked;api.Host=host.Text.Trim();
            try { api.SetSession(await api.Call("auth","auth/login",HttpMethod.Post,Api.Body("login",("correo",mail.Text.Trim()),("clave",password.Text)))); }
            catch {api.Clear();throw;}
            password.Clear();SetMenu();status.Text=api.Role;
        });
        Add("Productos",()=>LoadList("catalogos","productos"),true);
        Add("Zonas",()=>LoadList("catalogos","zonas"),true);
        Add("Microhubs",()=>LoadList("catalogos","microhubs"),true);
        Add("Pedidos",()=>LoadList("pedidos","pedidos"),true);
        Add("Candidatos",()=>LoadList("planeacion","candidatos"),true);
        Add("Escenarios",()=>LoadList("planeacion","escenarios"),true);
        Add("Detalle",async()=>{
            if(resource is "zonas" or "microhubs"){ShowRow();return;}
            Show(await api.Call(service,$"{resource}/{SelectedId()}"));
        },true);
        Add("Historial",async()=>{if(resource!="pedidos")throw new Exception("Selecciona un pedido.");Show(await api.Call("pedidos",$"pedidos/{SelectedId()}/historial"));},true);
        Add("Crear candidato",()=>EditCandidate(false),true,true);
        Add("Editar candidato",()=>EditCandidate(true),true,true);
        Add("Simular selección",async()=>{RequireCandidates();ShowResults(await api.Call("planeacion",$"candidatos/{SelectedId()}/simular",HttpMethod.Post,Api.Body("simular")));},true,true);
        Add("Decidir",async()=>{
            RequireCandidates();var id=SelectedId();
            var body=Edit("Decisión humana",Api.Body("decision",("decision","condicionado"),("motivo","")));
            if(body!=null){Show(await api.Call("planeacion",$"candidatos/{id}/decision",HttpMethod.Post,body));await Reload();}
        },true,true);
        Add("Simulación libre",async()=>{var b=Edit("Supuestos",Template("Simulacion.ok.xml"));if(b!=null)ShowResults(await api.Call("planeacion","simulaciones",HttpMethod.Post,b));},true,true);
        Add("Guardar escenario",async()=>{var b=Edit("Escenario",Template("EscenarioNuevo.ok.xml"));if(b!=null){Show(await api.Call("planeacion","escenarios",HttpMethod.Post,b));await LoadList("planeacion","escenarios");}},true,true);
        Add("Resumen",async()=>Show(await api.Call("planeacion","simulaciones/resumen")),true);
        Add("Anterior",async()=>{if(page>1){page--;await Reload();}},true);
        Add("Siguiente",async()=>{if(page<pages){page++;await Reload();}},true);
        Add("Buscar / filtrar",async()=>{page=1;await Reload();},true);
        Add("Exportar XML",()=>{if(latest==null)throw new Exception("Consulta primero.");using var d=new SaveFileDialog{Filter="XML|*.xml",FileName="microhubs.xml"};if(d.ShowDialog()==DialogResult.OK)latest.Save(d.FileName);return Task.CompletedTask;},true);
        Add("Salir",async()=>{try{await api.Call("auth","auth/salir",HttpMethod.Post,Api.Body("salir",("token_renovacion",api.Refresh)));}finally{api.Clear();grid.DataSource=null;latest=null;SetMenu();}},true);
        FilterOptions();
        bar.Controls.AddRange(new Control[]{search,state,new Label{Text="Desde",AutoSize=true},desde,new Label{Text="Hasta",AutoSize=true},hasta});
        SetMenu();FormClosed+=(_,_)=>api.Dispose();
    }
    static XElement Template(string name)=>Api.Example(name);
    static readonly string[] OrderStates={"creado","pendiente_asignacion","asignado","en_preparacion","en_ruta","entregado","entrega_parcial","entrega_fallida","cancelado"};
    static readonly string[] Decisions={"pendiente","aceptado","rechazado","condicionado"};
    void FilterOptions()
    {
        state.Items.Clear();state.Items.Add("Todos");
        if(resource=="pedidos")state.Items.AddRange(OrderStates);else if(resource=="candidatos")state.Items.AddRange(Decisions);
        state.Enabled=state.Items.Count>1;state.SelectedIndex=0;
    }
    string SelectedId()=>grid.CurrentRow?.Cells["id"].Value?.ToString()??throw new Exception("Selecciona un registro.");
    void RequireCandidates(){if(resource!="candidatos")throw new Exception("Selecciona un candidato.");}
    async Task EditCandidate(bool edit)
    {
        XElement body;string path="candidatos";
        if(edit){RequireCandidates();path+="/"+SelectedId();var source=(await api.Call("planeacion",path)).Root!;body=Template("CandidatoNuevo.ok.xml");foreach(var field in body.Elements())field.Value=source.Element(field.Name)!.Value;}
        else {body=Template("CandidatoNuevo.ok.xml");body.Element(Api.Ns+"clave")!.Value="R-"+DateTimeOffset.UtcNow.ToUnixTimeSeconds();}
        var result=Edit("Candidato · 14 campos",body);
        if(result!=null){await api.Call("planeacion",path,edit?HttpMethod.Put:HttpMethod.Post,result);await LoadList("planeacion","candidatos");}
    }
    XElement? Edit(string title,XElement source)
    {
        using var dialog=new Form{Text=title,Width=650,Height=680,StartPosition=FormStartPosition.CenterParent};
        var panel=new TableLayoutPanel{Dock=DockStyle.Fill,AutoScroll=true,ColumnCount=2};
        var controls=new Dictionary<string,TextBox>();var copy=new XElement(source);
        var errors=new ErrorProvider{ContainerControl=dialog};
        foreach(var leaf in copy.Descendants().Where(e=>!e.HasElements))
        {
            var key=string.Join(".",leaf.Ancestors().Reverse().Skip(1).Select(e=>e.Name.LocalName).Append(leaf.Name.LocalName));
            var text=new TextBox{Text=leaf.Value,Width=340};controls[key]=text;panel.Controls.Add(new Label{Text=key,AutoSize=true});panel.Controls.Add(text);
        }
        var save=new Button{Text="Validar y guardar",Dock=DockStyle.Bottom,Height=40};
        dialog.Controls.Add(panel);dialog.Controls.Add(save);
        save.Click+=(_,_)=>{
            errors.Clear();foreach(var leaf in copy.Descendants().Where(e=>!e.HasElements)){var key=string.Join(".",leaf.Ancestors().Reverse().Skip(1).Select(e=>e.Name.LocalName).Append(leaf.Name.LocalName));leaf.Value=controls[key].Text.Trim();}
            try{api.Validate(copy.ToString());dialog.DialogResult=DialogResult.OK;}
            catch(Exception e){foreach(var c in controls.Values)errors.SetError(c,e.Message);MessageBox.Show(dialog,e.Message,"Revisa los campos");}
        };
        return dialog.ShowDialog(this)==DialogResult.OK?copy:null;
    }
    void Add(string label,Func<Task> action,bool secure=false,bool write=false)
    {
        var b=new Button{Text=label,AutoSize=true};bar.Controls.Add(b);if(secure)secured.Add((b,write));
        b.Click+=async(_,_)=>{b.Enabled=false;try{await action();}catch(ApiError e){status.Text=$"{e.Message} · Traza {e.Trace}";MessageBox.Show(e.Message+"\n"+string.Join("\n",e.Fields.Select(f=>$"{f.Key}: {f.Value}"))+"\nTraza: "+e.Trace,"Servicio");}catch(Exception e){status.Text=e.Message;MessageBox.Show(e.Message,"Microhubs");}finally{b.Enabled=true;SetMenu();}};
    }
    void SetMenu(){foreach(var (b,write) in secured)b.Enabled=api.Access!="" && (!write || api.Role is "planeador" or "administrador");}
    async Task LoadList(string s,string r){service=s;resource=r;page=1;FilterOptions();await Reload();}
    async Task Reload()
    {
        if(resource=="")return;
        var query=$"{resource}?pagina={page}&por_pagina=20&q={Uri.EscapeDataString(search.Text)}";
        if(state.Text!="Todos" && resource is "pedidos" or "candidatos")query+=$"&{(resource=="candidatos"?"decision":"estado")}={Uri.EscapeDataString(state.Text)}";
        if(resource=="pedidos"){if(desde.Checked)query+="&desde="+desde.Value.ToString("yyyy-MM-dd");if(hasta.Checked)query+="&hasta="+hasta.Value.ToString("yyyy-MM-dd");}
        latest=await api.Call(service,query);pages=int.Parse(latest.Root!.Element(Api.Ns+"paginacion")!.Element(Api.Ns+"paginas")!.Value);
        grid.DataSource=ToTable(latest);status.Text=$"{resource} · página {page}/{pages} · {api.Role}";
    }
    /// <summary>Convierte una lista del contrato (datos + paginacion) en la tabla que ve la persona.</summary>
    internal static DataTable ToTable(XDocument list)
    {
        var rows=list.Root!.Element(Api.Ns+"datos")!.Elements().Select(Flatten).ToList();var table=new DataTable();
        foreach(var col in rows.SelectMany(r=>r.Keys).Distinct())table.Columns.Add(col);
        foreach(var row in rows){var item=table.NewRow();foreach(var cell in row)item[cell.Key]=cell.Value;table.Rows.Add(item);}
        return table;
    }
    internal static Dictionary<string,string> Flatten(XElement row)=>row.Descendants().Where(e=>!e.HasElements).GroupBy(e=>string.Join("/",e.Ancestors().TakeWhile(a=>a!=row).Reverse().Select(a=>a.Name.LocalName).Append(e.Name.LocalName))).ToDictionary(g=>g.Key,g=>string.Join("; ",g.Select(e=>e.Value)));
    void ShowRow(){var row=grid.CurrentRow??throw new Exception("Selecciona un registro.");MessageBox.Show(string.Join("\n",row.Cells.Cast<DataGridViewCell>().Select(c=>$"{grid.Columns[c.ColumnIndex].HeaderText}: {c.Value}")),"Detalle");}
    void Show(XDocument doc){latest=doc;MessageBox.Show(string.Join("\n",Flatten(doc.Root!).Select(k=>$"{k.Key}: {k.Value}")),"Detalle");}
    void ShowResults(XDocument doc){latest=doc;var r=doc.Root!;var eq=r.Element(Api.Ns+"equilibrio")!;MessageBox.Show($"{r.Element(Api.Ns+"decision")!.Value}\nUtilización: {r.Element(Api.Ns+"utilizacion")!.Value}% · {r.Element(Api.Ns+"nivel")!.Value}\nEquilibrio mensual: {eq.Element(Api.Ns+"mensual")!.Value}\nDiario: {eq.Element(Api.Ns+"diario")!.Value}\nMargen/pedido: {eq.Element(Api.Ns+"margen_pedido")!.Value}\n"+string.Join("\n",r.Element(Api.Ns+"explicacion")!.Elements().Select(e=>e.Value)),"Viabilidad y explicación");}
}
