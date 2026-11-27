using System.Net.Http;

namespace Microhubs;

/// <summary>
/// Una acción de una pantalla de análisis: a qué servicio y ruta va, qué raíz XML debe volver y, si envía algo, la plantilla del
/// ejemplo oficial que se edita antes de mandarla. `{id}` en la ruta se sustituye por la columna `Columna` de la fila elegida;
/// `Parametros` es la consulta que se propone y la persona puede cambiar.
/// </summary>
sealed record Accion(string Titulo, string Servicio, string Ruta, string Raiz, string Metodo = "GET", string? Plantilla = null,
                     string? Parametros = null, bool Escribe = false, string Columna = "id")
{
    public HttpMethod Http => new(Metodo);
    public bool PorFila => Ruta.Contains("{id}");

    /// <summary>La ruta final con el id de la fila y la consulta. El id y la consulta se revisan para no armar rutas raras.</summary>
    public string Armar(string? id = null, string? consulta = null)
    {
        var ruta = Ruta;
        if (PorFila)
        {
            if (string.IsNullOrWhiteSpace(id)) throw new Exception($"Selecciona un registro (columna «{Columna}»).");
            id = id.Trim();
            var esNumero = int.TryParse(id, out var n) && n > 0;                 // la mayoría de los recursos
            if (!esNumero && !Guid.TryParseExact(id, "D", out _)) throw new Exception($"El id seleccionado no es válido: {id}");   // simulaciones: UUID
            ruta = ruta.Replace("{id}", esNumero ? n.ToString() : id.ToLowerInvariant());
        }
        consulta = (consulta ?? Parametros ?? "").Trim().TrimStart('?');
        if (consulta.IndexOfAny(['#', ' ', '/', '\\']) >= 0) throw new Exception("La consulta solo lleva pares clave=valor separados por &.");
        return consulta == "" ? ruta : ruta + "?" + consulta;
    }
}

/// <summary>Una pantalla de análisis: su servicio y sus acciones.</summary>
sealed record Modulo(string Nombre, string Descripcion, Accion[] Acciones);

/// <summary>Las pantallas de análisis del escritorio. Todas hablan XML con sus servicios y validan contra los XSD oficiales.</summary>
static class Modulos
{
    public static readonly Modulo Cobertura = new("Cobertura", "Qué zonas y hogares atiende la red y qué agregaría una ubicación nueva (servicio 5116).", [
        new("Zonas", "cobertura", "cobertura/zonas", "cobertura_zonas"),
        new("Resumen", "cobertura", "cobertura/resumen", "cobertura_resumen"),
        new("Punto", "cobertura", "cobertura/punto", "cobertura_punto", Parametros: "latitud=25.7491&longitud=-100.3611"),
        new("Candidatos", "cobertura", "cobertura/candidatos", "cobertura_candidatos"),
        new("Escenarios de radio", "cobertura", "cobertura/escenarios", "cobertura_escenarios"),
        new("Evaluaciones", "cobertura", "cobertura/evaluaciones", "cobertura_evaluaciones"),
        new("Evaluar ubicación", "cobertura", "cobertura/evaluaciones", "cobertura_evaluacion", "POST", "CoberturaEvaluacionNueva.ok.xml"),
        new("Supuestos", "cobertura", "cobertura/supuestos", "supuestos_cobertura"),
    ]);

    public static readonly Modulo Rutas = new("Rutas", "Planes de reparto: proponer, comparar métodos, confirmar o cancelar (servicio 5118).", [
        new("Planes", "rutas", "rutas/planes", "ruta_planes"),
        new("Abrir plan", "rutas", "rutas/planes/{id}", "ruta_plan"),
        new("Proponer plan", "rutas", "rutas/planes", "ruta_plan", "POST", "RutaPlanNuevo.ok.xml", Escribe: true),
        new("Confirmar plan", "rutas", "rutas/planes/{id}/confirmar", "ruta_plan", "POST", Escribe: true),
        new("Cancelar plan", "rutas", "rutas/planes/{id}/cancelar", "ruta_plan", "POST", Escribe: true),
        new("Comparar métodos", "rutas", "rutas/comparaciones", "ruta_comparacion", "POST", "RutaComparacionNueva.ok.xml"),
        new("Supuestos", "rutas", "rutas/supuestos", "supuestos_rutas"),
    ]);

    public static readonly Modulo Costos = new("Costos", "Cuánto cuesta operar un microhub o una ubicación candidata (servicio 5119).", [
        new("Conceptos", "costos", "costos/conceptos", "conceptos_costo"),
        new("Resumen", "costos", "costos/resumen", "resumen_costos", Parametros: "microhub_id=1"),
        new("Unitarios", "costos", "costos/unitarios", "costos_unitarios", Parametros: "microhub_id=1"),
        new("Rentabilidad", "costos", "costos/rentabilidad", "rentabilidad", Parametros: "microhub_id=1"),
        new("Sensibilidad", "costos", "costos/sensibilidad", "sensibilidad_costos", Parametros: "microhub_id=1"),
        new("Nuevo concepto", "costos", "costos/conceptos", "concepto_costo", "POST", "ConceptoCostoNuevo.ok.xml", Escribe: true),
        new("Supuestos", "costos", "costos/supuestos", "supuestos_costos"),
    ]);

    public static readonly Modulo Capacidad = new("Capacidad", "Cuántos pedidos procesa cada microhub y qué tan cerca está de saturarse (servicio 5117).", [
        new("Microhubs", "capacidad", "capacidad/microhubs", "capacidad_microhubs"),
        new("Detalle", "capacidad", "capacidad/microhubs/{id}", "capacidad_microhub", Columna: "microhub/id"),
        new("Personal", "capacidad", "capacidad/recursos", "recursos_capacidad"),
        new("Cargas", "capacidad", "capacidad/cargas", "capacidad_cargas", Parametros: "microhub_id=1"),
        new("Simular", "capacidad", "capacidad/simulaciones", "capacidad_simulacion", "POST", "CapacidadSimulacionNueva.ok.xml"),
        new("Supuestos", "capacidad", "capacidad/supuestos", "supuestos_capacidad"),
    ]);

    public static readonly Modulo Equilibrio = new("Punto de equilibrio", "Pedidos necesarios para no perder dinero y si la demanda los alcanza (servicio 5120).", [
        new("Microhubs", "punto-equilibrio", "punto-equilibrio/microhubs", "equilibrio_microhubs"),
        new("Calcular", "punto-equilibrio", "punto-equilibrio/calculos", "equilibrio_calculo", "POST", "EquilibrioCalculoNuevo.ok.xml"),
        new("Sensibilidad", "punto-equilibrio", "punto-equilibrio/sensibilidad", "equilibrio_sensibilidad", "POST", "EquilibrioSensibilidadNueva.ok.xml"),
        new("Escenarios", "punto-equilibrio", "punto-equilibrio/escenarios", "equilibrio_escenarios"),
        new("Abrir escenario", "punto-equilibrio", "punto-equilibrio/escenarios/{id}", "equilibrio_calculo"),
        new("Comparar", "punto-equilibrio", "punto-equilibrio/comparacion", "equilibrio_comparacion", Parametros: "ids=1,2"),
        new("Supuestos", "punto-equilibrio", "punto-equilibrio/supuestos", "supuestos_equilibrio"),
    ]);

    public static readonly Modulo Simulacion = new("Simulación", "Monte Carlo de la operación: demanda variable y ausentismo (servicio 5121).", [
        new("Ejecuciones", "simulacion", "simulacion/ejecuciones", "simulacion_ejecuciones"),
        new("Nueva simulación", "simulacion", "simulacion/ejecuciones", "simulacion_ejecucion", "POST", "SimulacionNueva.ok.xml", Escribe: true),
        new("Ver ejecución", "simulacion", "simulacion/ejecuciones/{id}", "simulacion_ejecucion"),
        new("Repetir", "simulacion", "simulacion/ejecuciones/{id}/repetir", "simulacion_ejecucion", "POST", Escribe: true),
        new("Cancelar", "simulacion", "simulacion/ejecuciones/{id}/cancelar", "simulacion_ejecucion", "POST", Escribe: true),
        new("Comparar", "simulacion", "simulacion/comparacion", "simulacion_comparacion", Parametros: "ids=1,2"),
        new("Supuestos", "simulacion", "simulacion/supuestos", "supuestos_simulacion"),
    ]);

    public static readonly Modulo[] Todos = [Cobertura, Rutas, Costos, Capacidad, Equilibrio, Simulacion];

    /// <summary>Reportes (5123): catálogo, indicadores y bitácora. Ver, graficar y descargar usan la clave de la fila elegida.</summary>
    public static readonly Accion Catalogo = new("Catálogo", "reportes", "reportes", "reportes_catalogo");
    public static readonly Accion Indicadores = new("Indicadores", "reportes", "reportes/indicadores", "indicadores");
    public static readonly Accion Exportaciones = new("Exportaciones", "reportes", "reportes/exportaciones", "reportes_exportaciones");
}
