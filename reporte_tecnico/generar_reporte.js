// Genera Reporte_Tecnico_Equipo04.docx (36 apartados de la rúbrica).
//   node generar_reporte.js
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun, HeadingLevel,
  AlignmentType, WidthType, ShadingType, BorderStyle, LevelFormat, PageBreak, Footer, PageNumber,
} = require("docx");

const RAIZ = path.resolve(__dirname, "..");
const W = 9360; // ancho útil, Letter con márgenes de 1"
const FUENTE = "Calibri";
const borde = { style: BorderStyle.SINGLE, size: 4, color: "BFC5C0" };
const bordes = { top: borde, bottom: borde, left: borde, right: borde };

const t = (texto, o = {}) => new TextRun({ text: texto, font: FUENTE, ...o });
const p = (texto, o = {}) => new Paragraph({ spacing: { after: 120 }, ...o.par,
  children: Array.isArray(texto) ? texto : [t(texto, o)] });
const h1 = (texto) => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 160 }, children: [t(texto, { bold: true, size: 32, color: "1F4E79" })] });
const h2 = (texto) => new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 100 }, children: [t(texto, { bold: true, size: 26, color: "1B241F" })] });
const li = (texto) => new Paragraph({ numbering: { reference: "vin", level: 0 }, spacing: { after: 60 },
  children: Array.isArray(texto) ? texto : [t(texto)] });
const cod = (texto) => new Paragraph({ spacing: { after: 60 }, shading: { type: ShadingType.CLEAR, fill: "F1F2EE" },
  children: [t(texto, { font: "Consolas", size: 19 })] });
const nota = (texto) => new Paragraph({ spacing: { before: 80, after: 160 }, shading: { type: ShadingType.CLEAR, fill: "E7EFF6" },
  border: { left: { style: BorderStyle.SINGLE, size: 24, color: "1F4E79", space: 8 } },
  children: [t(texto, { size: 20 })] });

function tabla(cabeceras, filas, anchos) {
  const total = anchos.reduce((a, b) => a + b, 0);
  const celda = (txt, i, cab) => new TableCell({
    borders: bordes, width: { size: anchos[i], type: WidthType.DXA },
    shading: { type: ShadingType.CLEAR, fill: cab ? "1F4E79" : "FFFFFF" },
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({ children: [t(String(txt), { size: 18, bold: cab, color: cab ? "FFFFFF" : "1B241F" })] })],
  });
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: anchos,
    rows: [new TableRow({ tableHeader: true, children: cabeceras.map((c, i) => celda(c, i, true)) }),
      ...filas.map((f) => new TableRow({ children: f.map((c, i) => celda(c, i, false)) }))],
  });
}
const espacio = () => new Paragraph({ spacing: { after: 120 }, children: [] });

function imagen(archivo, ancho, alto, pie) {
  const ruta = path.join(RAIZ, archivo);
  if (!fs.existsSync(ruta)) return [p(`(Imagen no disponible: ${archivo})`)];
  return [new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 100, after: 60 },
    children: [new ImageRun({ type: "png", data: fs.readFileSync(ruta), transformation: { width: ancho, height: alto },
      altText: { title: pie, description: pie, name: pie } })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 }, children: [t(pie, { italics: true, size: 18, color: "5C6660" })] })];
}

const APARTADOS = ["Portada", "Integrantes", "Matrículas", "Control de versiones", "Resumen ejecutivo", "Objetivo", "Alcance",
  "Exclusiones", "Análisis del problema", "Actores", "Procesos", "Requerimientos", "Historias de usuario", "Criterios de aceptación",
  "Reglas de negocio", "Casos de uso", "Matriz de trazabilidad", "Matriz de perfiles y permisos", "Arquitectura", "Diagramas",
  "PostgreSQL", "MongoDB — análisis futuro", "Redis — análisis y justificación", "Microservicios — análisis futuro",
  "Contenedores — análisis futuro", "Seguridad", "Auditoría", "Evidencias del sistema", "Pruebas ejecutadas", "Problemas encontrados",
  "Deuda técnica", "Participación individual", "Evidencia Git", "Plan de trabajo", "Conclusiones", "Referencias"];
let n = 0;
const S = (titulo) => h1(`${++n}. ${titulo}`);

const c = [];

// ---------------------------------------------------------------- 1 Portada
c.push(new Paragraph({ spacing: { before: 1600 }, alignment: AlignmentType.CENTER, children: [t("REPORTE TÉCNICO", { bold: true, size: 56, color: "1F4E79" })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [t("Plataforma de Microhubs y Comercio de Proximidad", { size: 36 })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 }, children: [t("Evaluación de viabilidad, ubicación, capacidad y punto de equilibrio", { size: 26, color: "5C6660" })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 600 }, children: [t("Codex Innovations · Equipo 04", { bold: true, size: 30 })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, children: [t("Integración de Aplicaciones · Universidad de Monterrey", { size: 24 })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200 }, children: [t("Entrega: Avance 2 — módulos de planeación y viabilidad", { size: 24 })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, children: [t("Monterrey, Nuevo León · Septiembre de 2026", { size: 24 })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 400 }, children: [t("Repositorio: https://github.com/mauro-castp/proyecto-integracion", { size: 20, color: "5C6660" })] }));
c.push(new Paragraph({ children: [new PageBreak()] }));
n = 1; // la portada es el apartado 1

c.push(h1("Contenido"));
APARTADOS.forEach((a, i) => c.push(p(`${i + 1}. ${a}`)));
c.push(nota("Los documentos especializados de los bloques A, B, C y D se conservan como anexos y se citan en cada apartado. Este reporte integra su contenido y lo actualiza con los módulos de planeación."));
c.push(new Paragraph({ children: [new PageBreak()] }));

// ---------------------------------------------------------------- 2 Integrantes / 3 Matrículas
c.push(S("Integrantes"));
c.push(tabla(["Integrante", "Contribución principal documentada"], [
  ["Ruth Elizabeth Soriano Barrera", "Análisis del problema, propuesta, presentación, integración del repositorio"],
  ["Vanessa Morante López", "Módulos CRUD (productos, catálogos), modo local, script de base de datos de planeación"],
  ["Mauro Castillo Peña", "Creación del repositorio, catálogo de imágenes"],
  ["María José Cedillo Mata", "Documentos de los bloques A y B"],
  ["Jorge Antonio Arreola Cantú", "Por completar por el equipo"],
], [3200, 6160]));
c.push(nota("La atribución de contribuciones se dedujo del historial de Git (apartado 33). El equipo debe confirmarla y completarla en el apartado 32."));

c.push(S("Matrículas"));
c.push(tabla(["Integrante", "Matrícula"], [
  ["Ruth Elizabeth Soriano Barrera", "[pendiente de capturar]"], ["Vanessa Morante López", "[pendiente de capturar]"],
  ["Mauro Castillo Peña", "[pendiente de capturar]"], ["María José Cedillo Mata", "[pendiente de capturar]"],
  ["Jorge Antonio Arreola Cantú", "[pendiente de capturar]"],
], [5000, 4360]));
c.push(nota("Las matrículas no aparecen en ningún archivo del repositorio; cada integrante debe capturar la suya antes de entregar."));

// ---------------------------------------------------------------- 4 Control de versiones
c.push(S("Control de versiones"));
c.push(tabla(["Versión", "Fecha", "Cambio"], [
  ["1.0", "05-ago-2026", "Análisis del problema, propuesta y plan de trabajo (Entregable 1)"],
  ["1.1", "01-sep-2026", "Modelo de datos, arquitectura y sistema web mínimo funcional (Primer Parcial)"],
  ["1.2", "17-sep-2026", "CRUD de catálogos y productos; modo de demostración local"],
  ["2.0", "29-sep-2026", "Módulos de planeación y viabilidad (8 módulos), reporte técnico único, migración automática"],
  ["2.1", "30-sep-2026", "Integración con la versión de planeación de Vanessa (rama feature/planeacion-integrada): modo local de demostración, estado «listo para despacho», datos de reparto en el detalle del pedido"],
], [1200, 1800, 6360]));

// ---------------------------------------------------------------- 5 Resumen ejecutivo
c.push(S("Resumen ejecutivo"));
c.push(p("La plataforma nació como un sistema de pedidos para una red de microhubs (microalmacenes de barrio) en el sector San Bernabé de Monterrey. La retroalimentación del Primer Parcial señaló que ese sistema respondía bien a «¿cómo proceso un pedido en un microhub que ya existe?», pero no a la pregunta que justifica el proyecto: «¿conviene abrir un microhub aquí?»."));
c.push(p("Esta entrega incorpora la cadena completa: demanda → ubicación → cobertura → capacidad → surtido → operación → optimización de entrega → costos → punto de equilibrio → decisión de apertura. Se implementaron los ocho módulos solicitados dentro del mismo monolito Flask, con algoritmos sencillos y transparentes, parámetros configurables y una ficha de viabilidad cuya decisión final sigue siendo humana."));
c.push(li("Análisis de demanda por día, hora, zona y categoría, con ticket promedio, productos por pedido y demanda no atendida."));
c.push(li("Catálogo de ubicaciones candidatas con score configurable y cobertura por radio (hogares, demanda cubierta y fuera de cobertura, última milla, solapamiento)."));
c.push(li("Simulación de operación, capacidad por etapa, utilización con umbrales justificados, punto de equilibrio con el cálculo a la vista y análisis de sensibilidad de ocho variables."));
c.push(li("Planeación de surtido (ABC) con recomendaciones Aumentar, Mantener, Reducir y Eliminar."));
c.push(li("Optimización de entregas: agrupar por zona, asignar repartidor, ordenar paradas (TSP exacto hasta 8 paradas, vecino más cercano con 2-opt) y registrar la ruta."));
c.push(li("Escenarios guardables, comparables y exportables a CSV; paneles por perfil."));
c.push(p("Verificación: 16 pruebas unitarias de los cálculos, 6 pruebas del modo local, 23 comprobaciones de extremo a extremo contra la aplicación en Docker y las 26 verificaciones de reglas del motor (05_pruebas_reglas.sql) pasan. Limitación principal: los datos históricos de demostración son escasos (aproximadamente cuatro pedidos diarios entre todas las zonas), por lo que con ellos ningún candidato alcanza el equilibrio; el módulo lo señala tal cual y permite simular demandas mayores."));

// ---------------------------------------------------------------- 6 Objetivo
c.push(S("Objetivo"));
c.push(p([t("General. ", { bold: true }), t("Proveer al planeador una plataforma cuantitativa que evalúe si conviene abrir un microhub en una ubicación, con qué capacidad y surtido, y cuántos pedidos necesita para recuperar sus costos, sin dejar de operar los pedidos de los microhubs existentes.")]));
c.push(p([t("Específicos.", { bold: true })]));
c.push(li("Convertir el histórico de pedidos y la demanda no atendida en indicadores de demanda por zona, hora y categoría."));
c.push(li("Comparar ubicaciones candidatas con un score transparente y pesos configurables."));
c.push(li("Estimar capacidad, utilización, costo por pedido y punto de equilibrio, y permitir el análisis de sensibilidad."));
c.push(li("Recomendar surtido y ordenar entregas con heurísticas explicables."));
c.push(li("Mantener la decisión de apertura en manos de una persona, con trazabilidad en la bitácora."));

// ---------------------------------------------------------------- 7 Alcance / 8 Exclusiones
c.push(S("Alcance"));
c.push(li("Sitio público (catálogo y cobertura) y portal privado con autenticación JWT y permisos por perfil."));
c.push(li("Operación de pedidos: carrito, ticket mínimo, asignación, descuento de inventario, preparación, entrega, cierre, entrega parcial e incidencias."));
c.push(li("Planeación y viabilidad: los ocho módulos descritos en el apartado 12, más paneles del planeador, operador y administrador."));
c.push(li("Persistencia en PostgreSQL con lógica en el motor; sesiones, caché y bloqueos en Redis; ejecución completa con Docker Compose."));
c.push(S("Exclusiones"));
c.push(li("Optimización industrial: no se resuelve un VRP completo (ventanas de tiempo, capacidades por vehículo, tráfico); tampoco p-median ni facility location."));
c.push(li("GIS empresarial: no hay polígonos ni solapamiento geométrico exacto; se usan centroides y distancia Haversine."));
c.push(li("Teoría de colas M/M/c: la capacidad usa un modelo lineal de operadores por productividad."));
c.push(li("Pasarela de pago, aplicación móvil del repartidor y notificaciones."));
c.push(li("Microservicios y MongoDB como almacén operativo: se analizan como evolución futura (apartados 22 y 24)."));
c.push(li("Captura de costo unitario por producto en la interfaz: el costo se estima con un margen por omisión configurable cuando falta."));

// ---------------------------------------------------------------- 9 Análisis del problema
c.push(S("Análisis del problema"));
c.push(p("El abasto de proximidad en México se apoya en el canal tradicional: compras frecuentes y de bajo monto donde la cercanía pesa tanto como el precio (fuentes: NielsenIQ, ANPEC; detalle en el Análisis del Problema, anexo A1). Ese ticket reducido vuelve inviables los modelos de entrega rápida que dependen de costos de última milla altos."));
c.push(p("Un microhub es rentable solo si el margen por pedido, después del costo de entrega, cubre los costos fijos de renta, nómina y servicios con la demanda de su zona, y si su capacidad alcanza para atenderla sin saturarse. El problema, por tanto, es de decisión cuantitativa: dónde abrir, con qué recursos y cuánta demanda se necesita. Las preguntas de negocio que el sistema debe contestar son:"));
c.push(tabla(["Pregunta", "Dónde se responde"], [
  ["¿Conviene abrir un microhub aquí?", "Ficha de viabilidad del candidato"],
  ["¿Cuántos pedidos necesita?", "Punto de equilibrio (módulo 7)"],
  ["¿Qué capacidad requiere?", "Capacidad y simulación (módulos 3 y 4)"],
  ["¿Qué surtido debería tener?", "Planeación de surtido (módulo 5)"],
  ["¿Qué zona cubre y cuánto cuesta la última milla?", "Cobertura y mapa"],
  ["¿Qué ubicación es mejor?", "Score de ubicaciones (módulo 2)"],
  ["¿Qué ocurre si el ticket promedio baja?", "Análisis de sensibilidad"],
], [4600, 4760]));

// ---------------------------------------------------------------- 10 Actores
c.push(S("Actores"));
c.push(tabla(["Actor", "Responsabilidad"], [
  ["Visitante", "Consulta catálogo y cobertura sin autenticarse"],
  ["Cliente", "Integra carrito, confirma y da seguimiento a sus pedidos"],
  ["Operador de microhub", "Prepara pedidos, mantiene inventario, planea y despacha entregas de su microhub"],
  ["Repartidor", "Ejecuta la ruta y registra el resultado de la entrega"],
  ["Planeador", "Analiza demanda, compara ubicaciones, simula, guarda escenarios y decide la apertura"],
  ["Administrador", "Gestiona usuarios, catálogos, parámetros y supervisa seguridad, auditoría y salud"],
  ["Auditor", "Consulta bitácora y planeación en solo lectura"],
  ["Sistema", "Asigna pedidos, calcula indicadores y registra la auditoría"],
], [2600, 6760]));

// ---------------------------------------------------------------- 11 Procesos
c.push(S("Procesos"));
c.push(h2("11.1 Proceso operativo del pedido"));
c.push(p("Carrito → validación de ticket mínimo → confirmación → asignación al microhub elegible → descuento de inventario → preparación → planeación de ruta y asignación de repartidor → entrega (completa, parcial o fallida) → cierre. Las transiciones de estado son datos en la tabla transicion_permitida, validadas por un trigger del motor."));
c.push(h2("11.2 Proceso de planeación y viabilidad (flujo de 26 pasos)"));
c.push(tabla(["#", "Paso", "Dónde ocurre"], [
  ["1-2", "El administrador inicia sesión y consulta o configura parámetros", "/entrar, /admin/parametros"],
  ["3-4", "El planeador consulta la demanda histórica y por zona", "/planeacion/demanda"],
  ["5", "Registra ubicaciones candidatas", "/planeacion/candidatos/nuevo"],
  ["6-7", "El sistema calcula cobertura y compara candidatos", "/planeacion/cobertura, /candidatos"],
  ["8", "Selecciona un candidato", "/planeacion/candidatos/<id>"],
  ["9-11", "Configura capacidad, ejecuta la simulación y se calcula la utilización", "/planeacion/simulacion"],
  ["12", "El sistema recomienda surtido inicial", "/planeacion/surtido"],
  ["13-14", "Calcula costos y punto de equilibrio", "/planeacion/simulacion"],
  ["15-17", "Modifica supuestos, compara y guarda escenarios", "/planeacion/escenarios"],
  ["18-20", "El cliente genera el pedido, se asigna microhub, el operador prepara y lo marca listo para despacho", "Portal existente, /operacion/pedido/<id>"],
  ["21-23", "El sistema agrupa por zona, calcula ruta y asigna repartidor", "/planeacion/entregas"],
  ["24-25", "Se entrega; se actualizan inventario e indicadores", "Portal existente"],
  ["26", "Todo queda auditado", "Tabla auditoria (triggers)"],
], [900, 5400, 3060]));

// ---------------------------------------------------------------- 12 Requerimientos
c.push(S("Requerimientos"));
c.push(p("Los requerimientos de la base operativa (50 funcionales, 36 no funcionales) están en el anexo B1. Esta entrega añade los siguientes, identificados con el prefijo PL."));
c.push(tabla(["ID", "Requerimiento", "Módulo"], [
  ["PL-01", "Analizar demanda por día, hora, zona y categoría, con ticket, productos por pedido y demanda no atendida", "1"],
  ["PL-02", "Registrar y editar ubicaciones candidatas con coordenadas, renta, superficie, capacidad física, accesibilidad, zona, población y costo fijo", "2"],
  ["PL-03", "Calcular un score de ubicación con cuatro pesos configurables y documentados", "2"],
  ["PL-04", "Calcular cobertura: hogares, demanda cubierta y fuera de cobertura, tiempo, costo de última milla y solapamiento", "2"],
  ["PL-05", "Mostrar un mapa con zonas, demanda, microhubs, candidatos, cobertura y demanda no atendida", "2"],
  ["PL-06", "Simular la operación de un candidato con supuestos editables", "3"],
  ["PL-07", "Calcular capacidad por etapa (picking, packing, despacho, reparto) y utilización con umbrales 70 % y 85 %", "4"],
  ["PL-08", "Generar recomendaciones de surtido por SKU con clasificación ABC configurable", "5"],
  ["PL-09", "Agrupar pedidos listos por zona, asignar repartidor y calcular ruta, distancia y tiempo", "6"],
  ["PL-10", "Calcular el punto de equilibrio mostrando el cálculo paso a paso", "7"],
  ["PL-11", "Análisis de sensibilidad sobre ticket, pedidos/día, renta, nómina, costo de entrega, margen, operadores y repartidores", "7"],
  ["PL-12", "Emitir una ficha de viabilidad con explicación; la decisión de apertura la registra una persona con motivo", "7-8"],
  ["PL-13", "Guardar, abrir, editar, comparar y exportar escenarios", "8"],
  ["PL-14", "Paneles por perfil: planeador, operador y administrador", "—"],
  ["PL-15", "Auditar altas y cambios de candidatos, escenarios y rutas", "—"],
  ["PL-16", "Aplicar la migración de planeación a bases existentes sin perder datos", "—"],
  ["PL-17", "Ejecutar los módulos con datos de demostración sin Docker (modo local), reproduciendo el ejemplo de la retroalimentación", "—"],
  ["PL-18", "Marcar un pedido en preparación como listo para despacho y mostrar en su detalle repartidor, ruta, distancia, tiempo y costo de entrega", "6"],
], [900, 7460, 1000]));

// ---------------------------------------------------------------- 13 Historias / 14 Criterios
c.push(S("Historias de usuario"));
c.push(p("Las 32 historias de la base operativa están en el anexo B2. Historias nuevas:"));
c.push(tabla(["ID", "Historia"], [
  ["HU-P01", "Como planeador, quiero ver la demanda por zona, hora y categoría para saber dónde y cuándo se concentra la compra."],
  ["HU-P02", "Como planeador, quiero registrar y comparar ubicaciones candidatas para elegir la más favorable."],
  ["HU-P03", "Como planeador, quiero simular la operación con supuestos editables para conocer capacidad, costos y utilización."],
  ["HU-P04", "Como planeador, quiero ver cómo se calcula el punto de equilibrio para justificar la decisión."],
  ["HU-P05", "Como planeador, quiero variar ticket, renta u operadores y ver el efecto para entender la sensibilidad."],
  ["HU-P06", "Como planeador, quiero guardar y comparar escenarios para presentar alternativas."],
  ["HU-P07", "Como planeador, quiero registrar la decisión de apertura con su motivo para que sea auditable."],
  ["HU-P08", "Como planeador, quiero recomendaciones de surtido por SKU para definir el inventario inicial."],
  ["HU-P09", "Como operador, quiero que el sistema agrupe mis pedidos listos, asigne repartidor y ordene las paradas para reducir tiempo y distancia."],
  ["HU-P10", "Como administrador, quiero un panel con usuarios, microhubs, seguridad, auditoría y salud para supervisar el sistema."],
  ["HU-P11", "Como operador, quiero marcar un pedido como listo para despacho y ver después su repartidor, ruta, tiempo y costo, para dar seguimiento al reparto."],
], [1100, 8260]));
c.push(S("Criterios de aceptación"));
c.push(tabla(["Historia", "Criterios"], [
  ["HU-P01", "CA1: la tabla por zona muestra pedidos/día, ticket, no atendidos y pico. CA2: hay demanda por hora y por categoría."],
  ["HU-P02", "CA1: el catálogo guarda coordenadas, renta, superficie, capacidad, accesibilidad, zona, población y costo fijo. CA2: el ranking muestra el desglose del score."],
  ["HU-P03", "CA1: entrega atendidos, rechazados, utilización, tiempo, capacidad requerida, costo por pedido, ingreso y margen. CA2: cada cambio recalcula."],
  ["HU-P04", "CA1: con costos fijos 72,000 y margen 24 el sistema muestra 3,000 pedidos/mes y 100/día. CA2: se muestra la cuenta, no solo el resultado."],
  ["HU-P05", "CA1: las ocho variables son modificables. CA2: se ven equilibrio, utilización, costo por pedido y utilidad."],
  ["HU-P06", "CA1: un escenario guardado se puede abrir y editar. CA2: dos o más se comparan lado a lado. CA3: se exportan a CSV."],
  ["HU-P07", "CA1: aceptar, condicionar o rechazar exige motivo. CA2: queda en la bitácora con usuario y fecha."],
  ["HU-P08", "CA1: cada SKU trae clase ABC, cobertura, quiebres y recomendación. CA2: los umbrales son parámetros."],
  ["HU-P09", "CA1: los pedidos se agrupan por zona. CA2: cada repartidor recibe un máximo de paradas. CA3: se guardan distancia, tiempo y orden."],
  ["HU-P10", "CA1: el panel muestra usuarios, microhubs, parámetros, eventos de seguridad, auditoría y salud. CA2: solo el administrador entra."],
  ["HU-P11", "CA1: solo los pedidos en preparación pueden marcarse listos. CA2: los listos aparecen en Entregas y el panel del operador los cuenta aparte de los que se preparan. CA3: el detalle muestra repartidor, parada, distancia, minutos y costo."],
], [1100, 8260]));

// ---------------------------------------------------------------- 15 Reglas de negocio
c.push(S("Reglas de negocio"));
c.push(p("Las 40 reglas operativas (RN01 a RN40) están en el anexo B3. Reglas nuevas de planeación:"));
c.push(tabla(["ID", "Regla"], [
  ["RN-P01", "Todo peso, umbral o productividad se lee de la tabla configuracion, con su justificación; no hay constantes de negocio en el código."],
  ["RN-P02", "score = demanda × p1 − renta(miles) × p2 − distancia × p3 + accesibilidad × p4."],
  ["RN-P03", "capacidad = mínimo entre la capacidad de operación (operadores × tasa combinada de picking, packing y despacho), la de reparto y el tope físico del local."],
  ["RN-P04", "Utilización < 70 % estable; 70 a 85 % atención; > 85 % riesgo de saturación."],
  ["RN-P05", "margen por pedido = ticket × margen bruto − costo de entrega; equilibrio = costos fijos ÷ margen por pedido."],
  ["RN-P06", "Si el margen por pedido no es positivo, el proyecto es no viable con cualquier volumen."],
  ["RN-P07", "VIABLE: demanda atendida ≥ equilibrio y utilización ≤ 85 %. VIABLE CON RIESGO: cumple equilibrio pero supera 85 %. NO VIABLE: no alcanza equilibrio."],
  ["RN-P08", "La decisión de apertura la toma una persona y exige motivo; el sistema solo recomienda."],
  ["RN-P09", "ABC: A hasta 80 % del movimiento acumulado, B hasta 95 %, C el resto."],
  ["RN-P10", "Recomendación: Eliminar sin movimiento o clase C con margen no positivo; Aumentar con quiebres, existencia en el mínimo o cobertura menor a la mitad del objetivo; Reducir con cobertura mayor al exceso; en otro caso Mantener."],
  ["RN-P11", "Un repartidor recibe como máximo max_paradas_repartidor paradas por salida; hasta 8 paradas se resuelve el orden óptimo."],
  ["RN-P12", "Despachar exige el rol operador (transición en_preparacion → en_ruta de la máquina de estados)."],
  ["RN-P13", "Solo un pedido listo para despacho (en_preparacion con listo_en) entra a la planeación de rutas; el despacho directo sin ruta sigue disponible como excepción."],
  ["RN-P14", "Costo de entrega estimado = pago base por entrega + kilómetros del tramo × costo por kilómetro (ambos parámetros)."],
], [1100, 8260]));

// ---------------------------------------------------------------- 16 Casos de uso
c.push(S("Casos de uso"));
c.push(p("Los diez casos de uso principales (CU01 a CU10) están en el anexo B4. Casos nuevos:"));
c.push(tabla(["ID", "Caso de uso", "Actor", "Flujo principal"], [
  ["CU-P01", "Evaluar una ubicación candidata", "Planeador", "Registra el candidato → el sistema calcula cobertura y score → abre la ficha → registra la decisión con motivo"],
  ["CU-P02", "Simular y guardar un escenario", "Planeador", "Elige candidato → edita supuestos → ejecuta → revisa equilibrio y sensibilidad → guarda"],
  ["CU-P03", "Planear surtido", "Planeador", "Elige microhub → el sistema clasifica ABC → revisa recomendaciones"],
  ["CU-P04", "Despachar entregas", "Operador", "Marca pedidos listos para despacho → ve los listos por zona → el sistema propone repartidor y ruta → confirma → los pedidos pasan a en ruta"],
  ["CU-P05", "Supervisar el sistema", "Administrador", "Abre el panel → revisa seguridad, auditoría y salud"],
], [900, 2300, 1400, 4760]));
c.push(p("Alternativas relevantes: sin motivo la decisión se rechaza; con margen no positivo la ficha declara no viable; sin repartidores o pedidos listos la pantalla de entregas lo informa; un usuario sin el permiso recibe 403 y el intento se registra."));

// ---------------------------------------------------------------- 17 Trazabilidad
c.push(S("Matriz de trazabilidad"));
c.push(tabla(["Req.", "Historia", "Regla", "Implementación", "Prueba"], [
  ["PL-01", "HU-P01", "—", "planeacion.historial(), /planeacion/demanda", "e2e §1"],
  ["PL-02", "HU-P02", "—", "ubicacion_candidata, candidato_form()", "e2e §2"],
  ["PL-03", "HU-P02", "RN-P02", "planeacion_calc.score_ubicacion()", "test Ubicacion"],
  ["PL-04", "HU-P02", "—", "planeacion_calc.cobertura_candidato()", "test cobertura"],
  ["PL-05", "HU-P02", "—", "plan_cobertura.html (Leaflet)", "manual"],
  ["PL-06", "HU-P03", "RN-P03", "planeacion_calc.simular()", "test Simulacion"],
  ["PL-07", "HU-P03", "RN-P03/04", "planeacion_calc.capacidad()", "test umbrales"],
  ["PL-08", "HU-P08", "RN-P09/10", "clasificar_abc(), recomendar_surtido()", "test Surtido"],
  ["PL-09", "HU-P09", "RN-P11/12", "asignar_repartidores(), entregas_confirmar()", "test Rutas, e2e §5"],
  ["PL-10", "HU-P04", "RN-P05/06", "punto_equilibrio()", "test Equilibrio"],
  ["PL-11", "HU-P05", "—", "sensibilidad()", "test sensibilidad, e2e §3"],
  ["PL-12", "HU-P07", "RN-P07/08", "ficha_viabilidad(), candidato_decision()", "e2e §2"],
  ["PL-13", "HU-P06", "—", "escenario_guardar(), escenarios_csv()", "e2e §3"],
  ["PL-14", "HU-P10", "—", "panel_operador(), panel_admin()", "e2e §5-6"],
  ["PL-15", "—", "—", "Triggers trg_aud_* sobre las tablas nuevas", "consulta a auditoria"],
  ["PL-16", "—", "RN-P01", "migrar_planeacion.py, docker-compose.yml", "arranque Docker"],
  ["PL-17", "—", "—", "planeacion_demo.py, MODO_LOCAL en planeacion.py", "test_planeacion_local"],
  ["PL-18", "HU-P11", "RN-P13/14", "marcar_listo(), detalle() en rutas.py", "e2e §5"],
], [800, 900, 1200, 4160, 2300]));

// ---------------------------------------------------------------- 18 Perfiles y permisos
c.push(S("Matriz de perfiles y permisos"));
c.push(p("La matriz completa está en el anexo A2. Permisos nuevos: planeacion.ver y planeacion.editar; el despacho reutiliza entregas.asignar."));
c.push(tabla(["Funcionalidad", "Admin", "Planeador", "Operador", "Repartidor", "Auditor", "Cliente"], [
  ["Ver planeación (demanda, candidatos, cobertura, simulación, surtido, escenarios)", "Sí", "Sí", "No", "No", "Sí", "No"],
  ["Registrar candidatos, guardar escenarios, decidir apertura", "Sí", "Sí", "No", "No", "No", "No"],
  ["Planear y despachar entregas", "Ver", "No", "Sí", "No", "No", "No"],
  ["Panel del operador", "No", "No", "Sí", "No", "No", "No"],
  ["Panel del administrador", "Sí", "No", "No", "No", "No", "No"],
  ["Tablero del planeador", "Sí", "Sí", "No", "No", "Sí", "No"],
], [3260, 900, 1100, 1000, 1100, 1000, 1000]));
c.push(nota("El administrador puede consultar la pantalla de entregas, pero solo un operador puede confirmar el despacho porque la máquina de estados autoriza esa transición únicamente a ese rol. Los permisos de un rol se guardan en caché de Redis por 5 minutos."));

// ---------------------------------------------------------------- 19 Arquitectura
c.push(S("Arquitectura"));
c.push(p("La solución es un monolito modular en Flask: una sola aplicación desplegable cuyo código se separa por módulos (rutas.py, nucleo.py, productos_crud.py, catalogos_crud.py, planeacion.py y planeacion_calc.py). Las reglas de integridad viven en PostgreSQL como restricciones, funciones y triggers; la aplicación abre la transacción, declara el actor y traduce errores."));
c.push(tabla(["Componente", "Responsabilidad", "Persistencia"], [
  ["Navegador", "Formularios, tablas, mapa Leaflet", "Ninguna"],
  ["Flask + Gunicorn (3 procesos)", "Permisos, consultas, cálculos y plantillas", "Sin estado"],
  ["PostgreSQL 16", "Pedidos, inventario, candidatos, escenarios, rutas, auditoría", "Permanente y relacional"],
  ["Redis 7", "Sesiones, revocación, caché de permisos y catálogo, carrito, bloqueos de inventario", "Temporal"],
  ["MongoDB 7", "Colecciones de eventos definidas para análisis futuro", "Complementaria"],
  ["Docker Compose", "Levanta y conecta los servicios; migra la base al iniciar", "Volúmenes"],
], [2800, 4560, 2000]));
c.push(h2("Separación de cálculo y datos"));
c.push(p("planeacion_calc.py no importa Flask ni acceso a datos: recibe números y devuelve estructuras. Esto permite probar cada fórmula sin base de datos y explicar el cálculo al usuario. planeacion.py consulta, arma supuestos y presenta."));
c.push(h2("Algoritmos"));
c.push(tabla(["Módulo", "Algoritmo", "Fórmula o regla"], [
  ["Ubicación", "Score lineal ponderado", "demanda·p1 − renta/1000·p2 − distancia·p3 + accesibilidad·p4"],
  ["Cobertura", "Radio y distancia Haversine", "Zona cubierta si dist(centroide, candidato) ≤ radio"],
  ["Capacidad", "Tasa combinada por operador", "1 / (1/picking + 1/packing + 1/despacho); reparto por distancia y paradas por viaje"],
  ["Utilización", "Razón demanda/capacidad", "demanda ÷ capacidad_día × 100"],
  ["Equilibrio", "Punto de equilibrio contable", "costos fijos ÷ (ticket·margen − costo de entrega)"],
  ["Surtido", "Pareto (ABC) + reglas de cobertura", "acumulado 80 % / 95 %; cobertura = existencia ÷ demanda diaria"],
  ["Entregas", "TSP exacto (≤ 8) / vecino más cercano + 2-opt", "Minimiza distancia Haversine origen → paradas"],
], [1600, 3000, 4760]));

// ---------------------------------------------------------------- 20 Diagramas
c.push(S("Diagramas"));
c.push(p("Los nueve diagramas de arquitectura (contexto, contenedores, componentes, despliegue, red, secuencia, comunicación, autenticación y almacenamiento) están en bloque_d/diagramas con sus fuentes PlantUML. Se muestran los tres principales; el diagrama de flujo de planeación se presenta como tabla en el apartado 11."));
c.push(...imagen("bloque_d/diagramas/01_contexto.png", 560, 224, "Figura 1. Diagrama de contexto"));
c.push(...imagen("bloque_d/diagramas/02_contenedores.png", 440, 374, "Figura 2. Diagrama de contenedores"));
c.push(...imagen("bloque_d/diagramas/03_componentes.png", 470, 399, "Figura 3. Diagrama de componentes"));
c.push(nota("Pendiente: actualizar los diagramas de contenedores y componentes para incluir el módulo de planeación (blueprint planeacion y planeacion_calc). Las fuentes están en bloque_d/fuentes."));

// ---------------------------------------------------------------- 21 PostgreSQL
c.push(S("PostgreSQL"));
c.push(p("El esquema microhubs contiene 24 tablas de la base operativa (anexo C1). Los scripts se ejecutan en orden: 01_esquema, 02_logica, 03_semilla, 04_operacion_demo, 05_pruebas_reglas y 06_planeacion. El último es idempotente y también lo aplica migrar_planeacion.py en cada arranque de la aplicación."));
c.push(h2("Tablas y columnas nuevas"));
c.push(tabla(["Objeto", "Descripción"], [
  ["ubicacion_candidata", "Catálogo de candidatos. costo_fijo es columna generada (renta + nómina + servicios + otros). Guarda la decisión humana con motivo, usuario y fecha."],
  ["escenario_planeacion", "Supuestos y resultados en JSONB, candidato, autor y fechas de creación y actualización."],
  ["plan_ruta, plan_ruta_parada", "Ruta planeada por repartidor: método, distancia, minutos, costo y orden de paradas."],
  ["entrega (columnas nuevas)", "plan_ruta_id, orden_parada, distancia_km, minutos_estimados, costo_entrega_estimado."],
  ["pedido (columna nueva)", "listo_en: marca de «listo para despacho» de un pedido en preparación."],
  ["producto (columnas nuevas)", "costo_unitario (nulo = se estima con margen por omisión) y espacio_unidades."],
  ["zona (columna nueva)", "poblacion, para hogares potencialmente atendidos."],
  ["configuracion", "26 claves nuevas (pesos, productividades, umbrales, velocidad, costos, ABC, cobertura) con su justificación en descripcion."],
  ["permiso / rol_permiso", "planeacion.ver y planeacion.editar asignados a administrador y planeador; ver para auditor."],
], [2600, 6760]));
c.push(p("JSONB se eligió para escenarios porque los supuestos evolucionan sin exigir migraciones y se pueden consultar. Las restricciones CHECK impiden coordenadas fuera de México, accesibilidad fuera de 1 a 10 y decisiones sin motivo."));

// ---------------------------------------------------------------- 22 MongoDB
c.push(S("MongoDB — análisis futuro"));
c.push(p("El contenedor de MongoDB y las colecciones de eventos ya están definidos (bloque_c/mongo) pero ninguna funcionalidad operativa depende de él. Su papel previsto es analítico:"));
c.push(li("Guardar trazas de simulaciones (entradas y salidas completas) para comparar cómo evolucionan las decisiones."));
c.push(li("Registrar eventos de geolocalización de repartidores para calibrar velocidad real y reemplazar el supuesto de 22 km/h."));
c.push(li("Conservar consultas no atendidas con atributos variables (dispositivo, texto libre) que no encajan en columnas fijas."));
c.push(p("Se mantiene fuera del camino crítico: si MongoDB cae, el sistema opera."));

// ---------------------------------------------------------------- 23 Redis
c.push(S("Redis — análisis y justificación"));
c.push(p("Redis usa dos bases lógicas con políticas distintas: db 0 (noeviction) para sesiones, revocación de tokens y bloqueos de inventario, donde perder una clave sería un error de negocio; db 1 para caché y carrito. En planeación se usa la caché de permisos de rol (TTL de 5 minutos). Los cálculos de planeación no se cachean a propósito: dependen de parámetros editables y su costo es bajo con el volumen actual."));
c.push(p("Consecuencia práctica documentada: al cambiar los permisos de un rol, la caché puede tardar hasta 5 minutos en reflejarlo."));

// ---------------------------------------------------------------- 24 Microservicios
c.push(S("Microservicios — análisis futuro"));
c.push(p("Hoy el monolito es la decisión correcta: un equipo de cinco personas, un solo dominio y transacciones que cruzan pedidos, inventario y entrega. Candidatos a separarse cuando el volumen lo justifique:"));
c.push(tabla(["Candidato", "Motivo", "Condición para separarlo"], [
  ["Servicio de planeación", "Cálculo intensivo y ritmo de cambio distinto al de la operación", "Simulaciones masivas o VRP que compitan por CPU con los pedidos"],
  ["Servicio de rutas", "Algoritmos con dependencias propias (mapas, tráfico)", "Integrar un motor de rutas externo"],
  ["Servicio de inventario", "Consistencia estricta y bloqueos", "Varios canales de venta sobre el mismo stock"],
], [2300, 3800, 3260]));
c.push(p("Costo a considerar: consistencia distribuida y observabilidad; hoy las restricciones del motor resuelven la sobreventa de forma sencilla."));

// ---------------------------------------------------------------- 25 Contenedores
c.push(S("Contenedores — análisis futuro"));
c.push(p("Docker Compose ya orquesta cuatro servicios (postgres, redis, mongo, web) en dos redes: datos (interna, sin salida a Internet) y pública (solo el puerto de la aplicación). El contenedor web corre sin privilegios de administrador y tiene comprobación de salud (/salud)."));
c.push(p("Arranque de la aplicación: espera a PostgreSQL y Redis saludables → migrar_planeacion.py → Gunicorn con 3 procesos. La migración es necesaria porque PostgreSQL no vuelve a ejecutar initdb si el volumen existe."));
c.push(li("Futuro: separar una imagen de migraciones, usar secretos en lugar de variables de entorno y añadir un proxy inverso con TLS."));
c.push(li("Futuro: orquestación (Kubernetes) solo si se separan servicios y se requiere escalado horizontal."));
c.push(li("Verificado: el arranque desde volumen vacío y la reaplicación de la migración sobre la misma base concluyeron sin errores."));

// ---------------------------------------------------------------- 26 Seguridad
c.push(S("Seguridad"));
c.push(li("Autenticación con contraseñas bcrypt y tokens JWT de acceso y renovación; revocación de sesión y bloqueo temporal tras intentos fallidos (parámetros configurables)."));
c.push(li("Autorización por rol en cada ruta con el decorador @requiere; ocultar un enlace no sustituye el control (entrar por URL devuelve 403 y queda registrado)."));
c.push(li("Verificado en las pruebas: el planeador recibe 403 en el panel de administrador y en el despacho; el repartidor recibe 403 en planeación."));
c.push(li("Consultas parametrizadas en todo el módulo nuevo; las plantillas escapan la salida por omisión."));
c.push(li("Base de datos no publicada al host; contenedor web sin privilegios de administrador; roles de base de datos app_microhubs y auditor_microhubs con permisos mínimos."));
c.push(li("Riesgos abiertos: los formularios no incluyen token CSRF y la contraseña demo es común a todas las cuentas de demostración; ambos deben resolverse antes de producción."));

// ---------------------------------------------------------------- 27 Auditoría
c.push(S("Auditoría"));
c.push(p("La auditoría se hace en el motor: el trigger fn_auditar_cambio registra alta, modificación o baja con los valores anteriores y nuevos (solo los campos que cambiaron) y el usuario declarado en la transacción. La bitácora es inmutable (trigger que rechaza UPDATE y DELETE)."));
c.push(p("06_planeacion.sql añade triggers a ubicacion_candidata, escenario_planeacion y plan_ruta. Además, la exportación de escenarios a CSV se registra como evento. Comprobación en la base de pruebas tras el recorrido: registros de módulo planeacion con altas de escenarios, rutas y candidatos y modificaciones de escenario y candidato (decisión). Las 132 altas y 127 modificaciones de entrega del módulo entregas provienen de la carga de demostración."));

// ---------------------------------------------------------------- 28 Evidencias
c.push(S("Evidencias del sistema"));
c.push(p("Caso de referencia de la retroalimentación (costos fijos 72,000 = renta 18,000 + nómina 42,000 + servicios 7,000 + otros 5,000; margen por pedido 24):"));
c.push(cod("Margen por pedido = ticket × margen bruto − costo de entrega = 100.00 × 46.00% − 22.00 = 24.00"));
c.push(cod("Punto de equilibrio mensual = 72,000.00 ÷ 24.00 = 3,000 pedidos/mes"));
c.push(cod("Punto de equilibrio diario = 3,000 ÷ 30 días = 100.0 pedidos/día"));
c.push(p("Escenario A guardado desde la interfaz (candidato CAND-01, 120 pedidos/día, 3 operadores, 4 repartidores, ticket $135, costo de entrega $22, renta $18,000, nómina $42,000, servicios $7,000, otros $5,000, tope físico 150):"));
c.push(tabla(["Indicador", "Resultado"], [
  ["Pedidos atendidos / rechazados", "120 / 0"],
  ["Capacidad diaria y cuello de botella", "150 pedidos (espacio físico)"],
  ["Utilización", "80 % (atención)"],
  ["Margen por pedido", "$15.80"],
  ["Punto de equilibrio", "4,557 pedidos/mes = 151.9 pedidos/día"],
  ["Costo por pedido", "$42.00"],
  ["Decisión de la ficha", "NO VIABLE CON LOS SUPUESTOS ACTUALES (la demanda no alcanza el equilibrio)"],
], [4200, 5160]));
c.push(p("Despacho verificado: cinco pedidos en preparación del microhub MH-02 se agruparon en dos zonas, se asignaron a los dos repartidores (3 y 2 paradas), se calculó la ruta con TSP exacto (0.80 km y 14.2 min; 0.58 km y 9.6 min) y quedaron persistidos en plan_ruta, plan_ruta_parada y entrega, con los pedidos en estado en_ruta."));
c.push(...imagen("bloque_d/capturas/1_catalogo.png", 460, 260, "Figura 4. Catálogo público (captura del Primer Parcial)"));
c.push(nota("Pendiente: agregar capturas de las pantallas nuevas (tablero, demanda, candidatos, cobertura y mapa, simulación, surtido, entregas, escenarios y paneles). Rutas para capturarlas: /planeacion/tablero, /planeacion/demanda, /planeacion/candidatos, /planeacion/cobertura, /planeacion/simulacion, /planeacion/surtido, /planeacion/entregas, /planeacion/escenarios, /panel/operador y /panel/administrador."));

// ---------------------------------------------------------------- 29 Pruebas
c.push(S("Pruebas ejecutadas"));
c.push(tabla(["Prueba", "Alcance", "Resultado"], [
  ["test_planeacion.py (unittest)", "16 pruebas: equilibrio (ejemplo de la retro), score y pesos, cobertura y solapamiento, capacidad y umbrales, saturación, tope físico, decisiones de viabilidad, sensibilidad, ABC, recomendaciones, Haversine, TSP, 2-opt, asignación con tope", "16 de 16 pasan"],
  ["test_planeacion_local.py", "Modo local con Flask: los ocho módulos y los paneles, ejemplo de la retro (82/54/39 pedidos/día), equilibrio 3,000/100, escenarios, candidato y decisión humana, entregas", "6 de 6 pasan (ejecutadas en el contenedor)"],
  ["prueba_e2e_planeacion.py", "Contra la aplicación en Docker: carga de pantallas, alta de candidato, decisión sin motivo, ejemplo 3,000/100, sensibilidad de 8 variables, escenarios, permisos 403, paneles, marcar listo y despachar con ruta", "23 de 23 pasan"],
  ["Arranque con Docker", "initdb desde volumen vacío con 06_planeacion.sql y reaplicación con migrar_planeacion.py", "Sin errores"],
  ["Despacho verificado", "Operador prepara, marca listos, planea y despacha; el detalle del pedido muestra el reparto", "Rutas persistidas y pedidos en ruta"],
  ["prueba_e2e.py (Primer Parcial)", "Flujo operativo con navegador (Playwright)", "No se ejecutó en esta entrega: requiere Playwright"],
  ["05_pruebas_reglas.sql", "Reglas de negocio del motor (RN05 a RN40) tras aplicar la migración de planeación", "26 de 26 PASA"],
], [2500, 5060, 1800]));
c.push(p("Comandos:"));
c.push(cod("cd sistema_web && python -m unittest -v test_planeacion.py"));
c.push(cod("docker compose up --build -d"));
c.push(cod("docker compose run --rm --no-deps web python -m unittest -v test_planeacion_local"));
c.push(cod("BASE=http://127.0.0.1:5000 python prueba_e2e_planeacion.py"));

// ---------------------------------------------------------------- 30 Problemas
c.push(S("Problemas encontrados"));
c.push(tabla(["Problema", "Causa", "Solución"], [
  ["El módulo descrito en un manual previo no existía en el repositorio", "Solo se había subido un script SQL suelto", "Se implementó el módulo completo y se verificó con pruebas"],
  ["Volúmenes existentes no recibían las tablas nuevas", "PostgreSQL ejecuta initdb solo con el volumen vacío", "migrar_planeacion.py idempotente al iniciar la aplicación"],
  ["Ningún candidato resulta viable con el histórico", "La demostración tiene unos 4 pedidos diarios en total", "Se documenta; la simulación permite escribir demandas mayores"],
  ["Costo de entrega de $2 con distancias de 0.8 km", "Solo se modelaba el costo por distancia", "Se añadió un pago base por entrega configurable ($18)"],
  ["Dos implementaciones paralelas de Planeación (la de Vanessa y la de esta rama) con nombres de archivo iguales", "Trabajo simultáneo sin coordinar", "Fusión en una rama: base de 8 módulos más el modo local de la otra; se retiran base.html y planeacion.html, que estaban fuera de templates/"],
  ["La versión subida de Planeación no arrancaba en Docker", "Plantillas fuera de templates/ y SQL en la raíz en lugar de bloque_c/sql/", "Archivos ubicados donde Flask y Docker los buscan"],
  ["El botón «Marcar listo para ruta» despachaba el pedido directo, sin agrupar ni asignar repartidor", "El estado listo no existía", "Columna pedido.listo_en y botón «Marcar listo para despacho»; el despacho directo queda como excepción"],
  ["Puerto 5055 bloqueado en Windows durante las pruebas", "Rango reservado por el sistema", "Se usó otro puerto mediante WEB_PORT"],
  ["Mensaje engañoso «el espacio limita la capacidad» con demanda mínima", "Se mostraba siempre que el tope físico fuera el cuello", "Solo se muestra si la utilización llega al umbral estable"],
], [3000, 3000, 3360]));

// ---------------------------------------------------------------- 31 Deuda técnica
c.push(S("Deuda técnica"));
c.push(li("Cobertura sin GIS: centroides y radio; falta solapamiento geométrico y hogares por polígono."));
c.push(li("Capacidad lineal: falta modelo de colas (M/M/1, M/M/c) y picos horarios."));
c.push(li("Reparto sin VRP: no considera ventanas de tiempo, capacidad por vehículo ni tráfico; distancia en línea recta."));
c.push(li("La simulación no separa turnos ni el efecto de los picos por hora."));
c.push(li("costo_unitario y espacio_unidades no se capturan en la interfaz de productos; el margen se estima."));
c.push(li("Sin token CSRF en formularios; contraseña demo compartida."));
c.push(li("El modo local de planeación usa datos en memoria: candidatos y escenarios no persisten y el despacho solo calcula la ruta."));
c.push(li("«Listo para despacho» es una marca (listo_en), no un estado de la máquina de estados; si se requiere en reportes de trazabilidad conviene promoverlo a estado."));
c.push(li("Diagramas de arquitectura y matrices de los bloques A y B sin actualizar con planeación."));
c.push(li("Datos de demostración insuficientes para ilustrar un candidato viable sin editar la demanda."));

// ---------------------------------------------------------------- 32 Participación
c.push(S("Participación individual"));
c.push(p("La siguiente tabla muestra la actividad registrada en Git (apartado 33). Es una evidencia parcial: no refleja trabajo de análisis, diseño o pruebas hecho fuera del repositorio."));
c.push(tabla(["Integrante", "Commits", "Aportes en el repositorio", "Participación declarada"], [
  ["María José Cedillo Mata (mariacedillom-tech)", "14", "Documentos de los bloques A y B", "[por completar]"],
  ["Ruth Soriano", "8", "Modelo de datos, sistema web mínimo, presentación, propuesta, READMEs", "[por completar]"],
  ["Vanessa Morante López (vanessamorante-lgtm)", "4", "CRUD de productos y catálogos, modo local, primera versión de Planeación (planeacion.py, pruebas, migración) e ideas incorporadas en la integración", "[por completar]"],
  ["Mauro Castillo Peña (mauro-castp / mau)", "2", "Repositorio inicial, imágenes del catálogo", "[por completar]"],
  ["Jorge Antonio Arreola Cantú", "0", "Sin commits con su nombre", "[por completar]"],
], [2800, 900, 3460, 2200]));
c.push(nota("Cada integrante debe redactar su participación declarada. Los commits de esta entrega (módulos de planeación) aún no están publicados y se atribuirán al integrante que los suba."));

// ---------------------------------------------------------------- 33 Evidencia Git
c.push(S("Evidencia Git"));
c.push(p("Repositorio: https://github.com/mauro-castp/proyecto-integracion · rama main con 28 commits al 29 de septiembre de 2026; el trabajo de esta entrega está en la rama feature/planeacion-integrada (commits locales sobre main, aún sin publicar)."));
c.push(tabla(["Commit", "Autor", "Fecha", "Mensaje"], [
  ["d58cdb8", "vanessamorante-lgtm", "29-sep", "Add files via upload (versión de Planeación)"],
  ["1a4cf00", "vanessamorante-lgtm", "29-sep", "Add files via upload (06_planeacion.sql)"],
  ["67e6a42", "vanessamorante-lgtm", "17-sep", "Add database files to .gitignore"],
  ["95721e8", "vanessamorante-lgtm", "17-sep", "Add files via upload (CRUD de catálogos y productos)"],
  ["552306e", "Ruth Soriano", "04-sep", "Actualizar documentos del proyecto"],
  ["a5bb008", "Ruth Soriano", "04-sep", "Agregar foto de Bolsas para basura"],
  ["b42e82b", "Ruth Soriano", "04-sep", "Agregar propuesta de negocio (incluye plan de trabajo)"],
  ["c0d8dae", "mau", "03-sep", "Agregar imágenes de productos al catálogo"],
  ["7f149eb", "Ruth Soriano", "01-sep", "Primer Parcial: modelo de datos, arquitectura y sistema web"],
  ["c8f2beb", "mauro-castp", "28-ago", "Initial commit"],
], [1100, 2400, 1000, 4860]));
c.push(p("Convención sugerida para lo que sigue: un commit por módulo con mensaje en español que cite el requerimiento (por ejemplo «Agregar módulo de surtido ABC (PL-08)»), ramas por funcionalidad y revisión por otro integrante antes de fusionar."));

// ---------------------------------------------------------------- 34 Plan de trabajo
c.push(S("Plan de trabajo"));
c.push(tabla(["Etapa", "Entregable", "Estado"], [
  ["1. Base operativa", "Modelo de datos, pedidos, inventario, entrega, auditoría", "Terminado"],
  ["2. Catálogos", "CRUD de productos, categorías, zonas, microhubs, usuarios", "Terminado"],
  ["3. Planeación y viabilidad", "Ocho módulos, paneles, modo local, migración, pruebas", "Implementado, integrado con la versión de Vanessa y verificado; falta publicar y revisar"],
  ["4. Cierre de brechas", "Capturas, diagramas actualizados, matrículas y participación", "Pendiente"],
  ["5. Cobertura avanzada", "GIS con polígonos, solapamiento exacto", "Futuro"],
  ["6. Optimización", "p-median o localización con capacidad; colas M/M/c; VRP", "Futuro"],
  ["7. Analítica", "MongoDB para trazas y telemetría de reparto", "Futuro"],
], [2600, 4760, 2000]));
c.push(p("Siguientes pasos inmediatos: (1) publicar la rama con los módulos, (2) completar matrículas y participación, (3) capturar las pantallas nuevas, (4) actualizar los diagramas y matrices de los bloques A y B, (5) ampliar los datos de demostración para ilustrar un candidato viable."));

// ---------------------------------------------------------------- 35 Conclusiones
c.push(S("Conclusiones"));
c.push(p("El sistema dejó de ser solo una herramienta de pedidos: ahora responde si conviene abrir un microhub, dónde, con qué capacidad y con cuántos pedidos. Las fórmulas son sencillas, están probadas y se muestran al usuario; los parámetros y su justificación viven en la base de datos, y la decisión final es humana y queda auditada."));
c.push(p("Los resultados con los datos actuales son honestos: el histórico de demostración es demasiado pequeño para justificar la apertura de cualquier candidato. Esa conclusión es, en sí, una salida válida del módulo. Con datos reales, o proyectando una demanda mayor en la simulación, la ficha puede llegar a VIABLE o VIABLE CON RIESGO."));
c.push(p("Queda como trabajo explícito la evolución hacia GIS, colas y VRP, descritas en la deuda técnica, y la consolidación de la documentación y de la evidencia de participación."));

// ---------------------------------------------------------------- 36 Referencias
c.push(S("Referencias"));
c.push(li("NielsenIQ (2026). Informe del canal tradicional en México."));
c.push(li("Asociación Nacional de Pequeños Comerciantes (ANPEC). Estadísticas de tiendas de abarrotes."));
c.push(li("Sinnott, R. W. (1984). Virtues of the Haversine. Sky and Telescope, 68(2)."));
c.push(li("Chopra, S. y Meindl, P. Supply Chain Management: Strategy, Planning, and Operation. Pearson."));
c.push(li("Daskin, M. S. Network and Discrete Location: Models, Algorithms, and Applications. Wiley."));
c.push(li("Toth, P. y Vigo, D. (eds.). Vehicle Routing: Problems, Methods, and Applications. SIAM."));
c.push(li("Croes, G. A. (1958). A method for solving traveling-salesman problems. Operations Research, 6(6)."));
c.push(li("Silver, E. A., Pyke, D. F. y Thomas, D. J. Inventory and Production Management in Supply Chains. CRC Press."));
c.push(li("Documentación de PostgreSQL 16, Flask 3, Redis 7, Docker Compose y Leaflet 1.9."));
c.push(li("Anexos del proyecto: bloque_a (A1 Análisis del problema, A2 Matriz de perfiles, A3 Propuesta), bloque_b (B1 Requerimientos, B2 Historias, B3 Reglas, B4 Casos de uso, B5 Trazabilidad), bloque_c (C1 Modelo de datos), bloque_d (D1 Diagramas)."));
c.push(nota("Verificar el formato de citación exigido por el curso y completar los datos bibliográficos (editorial y edición) antes de entregar."));

const doc = new Document({
  creator: "Codex Innovations · Equipo 04", title: "Reporte Técnico — Plataforma de Microhubs",
  styles: { default: { document: { run: { font: FUENTE, size: 22 } } } },
  numbering: { config: [{ reference: "vin", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [t("Reporte Técnico · Codex Innovations · Equipo 04 · Página ", { size: 16, color: "5C6660" }),
        new TextRun({ children: [PageNumber.CURRENT], font: FUENTE, size: 16, color: "5C6660" })] })] }) },
    children: c,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  const salida = path.join(__dirname, "Reporte_Tecnico_Equipo04.docx");
  fs.writeFileSync(salida, buf);
  console.log("Generado:", salida, `(${APARTADOS.length} apartados)`);
});
