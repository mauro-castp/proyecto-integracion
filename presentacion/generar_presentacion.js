const pptxgen = require("pptxgenjs");
const path = require("path");
const { renderIcon } = require("./icons.js");
const CAP_DIR = path.join(__dirname, "capturas");

// ---------- paleta (misma que el sistema web y los diagramas del proyecto) ----------
const AZUL = "1F4E79";
const AZUL_DARK = "12283C";
const AZUL_TINT = "E7EFF6";
const VERDE = "2E6B4F";
const VERDE_TINT = "E5F1EA";
const AMBAR = "8A5A17";
const AMBAR_TINT = "F6EEE0";
const VINO = "7B2D4E";
const VINO_TINT = "F5E7ED";
const VIOLETA = "54417B";
const VIOLETA_TINT = "EEEAF5";
const INK = "1B241F";
const INK2 = "5C6660";
const WHITE = "FFFFFF";

const F_HEAD = "Cambria";
const F_BODY = "Calibri";

const W = 13.333, H = 7.5;

async function main() {
  const pres = new pptxgen();
  pres.defineLayout({ name: "WIDE", width: W, height: H });
  pres.layout = "WIDE";

  // pre-render every icon used, at the color it will be shown in
  const iconDefs = [
    ["FaStore", WHITE], ["FaStore", AZUL],
    ["FaMoneyBillWave", AZUL], ["FaCoins", VERDE], ["FaCity", AMBAR],
    ["FaRoad", VINO], ["FaWifi", VIOLETA], ["FaPercentage", AZUL],
    ["FaChartBar", AZUL], ["FaMapMarkerAlt", VERDE], ["FaSearchLocation", AMBAR],
    ["FaCogs", VINO], ["FaWarehouse", VIOLETA], ["FaBoxes", AZUL],
    ["FaShoppingCart", VERDE], ["FaTruck", AMBAR], ["FaBalanceScale", VINO],
    ["FaGlobe", WHITE], ["FaNetworkWired", INK2], ["FaMobileAlt", INK2], ["FaDesktop", INK2],
    ["FaShieldAlt", WHITE], ["FaLock", AZUL], ["FaDatabase", WHITE],
    ["FaDatabase", AZUL], ["FaLayerGroup", VERDE], ["FaBolt", AMBAR],
    ["FaCheckCircle", VERDE], ["FaCheckCircle", WHITE], ["FaDocker", AZUL],
    ["FaHistory", VIOLETA], ["FaUserShield", AZUL], ["FaKey", VERDE],
    ["FaMapMarkedAlt", WHITE], ["FaFlagCheckered", WHITE],
    ["FaSearchLocation", AZUL], ["FaGlobe", AZUL], ["FaGlobe", AZUL_DARK],
    ["FaCheckCircle", AZUL_DARK], ["FaDocker", AZUL_DARK], ["FaDatabase", AZUL_DARK],
    ["FaLock", VERDE], ["FaHistory", AMBAR], ["FaShoppingCart", VINO],
    ["FaChartBar", VIOLETA], ["FaUserShield", AMBAR],
    ["FaWarehouse", VERDE], ["FaChartBar", AMBAR],
  ];
  const ic = {};
  for (const [name, color] of iconDefs) {
    ic[name + ":" + color] = await renderIcon(name, color, 256);
  }
  const I = (name, color) => {
    const k = name + ":" + color;
    if (!ic[k]) console.warn("MISSING ICON", k);
    return ic[k];
  };

  // ---------- helpers ----------
  function bg(slide, color) { slide.background = { color }; }

  function iconCircle(slide, { x, y, d, icon, color, tint }) {
    slide.addShape("ellipse", { x, y, w: d, h: d, fill: { color: tint }, line: { type: "none" } });
    const pad = d * 0.28;
    slide.addImage({ data: I(icon, color), x: x + pad / 2, y: y + pad / 2, w: d - pad, h: d - pad });
  }

  function cardIconLabel(slide, { x, y, w, h, icon, color, tint, title, body }) {
    const dCirc = 0.62;
    iconCircle(slide, { x: x + 0.05, y: y, d: dCirc, icon, color, tint });
    slide.addText(title, {
      x: x + dCirc + 0.22, y: y - 0.03, w: w - dCirc - 0.3, h: 0.52,
      fontFace: F_BODY, fontSize: 13, bold: true, color: INK, align: "left", valign: "top",
      isTextBox: true, margin: 0, lineSpacingMultiple: 1.05,
    });
    if (body) {
      slide.addText(body, {
        x: x + dCirc + 0.22, y: y + 0.5, w: w - dCirc - 0.3, h: h - 0.5,
        fontFace: F_BODY, fontSize: 10.5, color: INK2, align: "left", valign: "top",
        isTextBox: true, margin: 0, lineSpacingMultiple: 1.12,
      });
    }
  }

  function kicker(slide, text, color) {
    slide.addText(text.toUpperCase(), {
      x: 0.7, y: 0.42, w: 8, h: 0.35, fontFace: F_BODY, fontSize: 12.5, bold: true,
      color, charSpacing: 1.5, isTextBox: true, margin: 0,
    });
  }

  function title(slide, text, opts = {}) {
    slide.addText(text, {
      x: 0.7, y: opts.y || 0.72, w: opts.w || 11.6, h: opts.h || 0.9,
      fontFace: F_HEAD, fontSize: opts.size || 32, bold: true, color: opts.color || INK,
      isTextBox: true, margin: 0,
    });
  }

  function pageNum(slide, n) {
    slide.addText(String(n).padStart(2, "0"), {
      x: W - 0.9, y: H - 0.55, w: 0.6, h: 0.35, fontFace: F_BODY, fontSize: 10,
      color: INK2, align: "right", isTextBox: true, margin: 0,
    });
  }

  // ==================================================================
  // 1. PORTADA
  // ==================================================================
  {
    const s = pres.addSlide();
    bg(s, AZUL_DARK);
    // nodos decorativos (motivo de microhubs conectados)
    const nodes = [[10.7, 1.3, 0.16, AMBAR], [11.7, 2.3, 0.22, VERDE], [10.3, 3.1, 0.13, VIOLETA], [12.2, 3.9, 0.18, VINO], [11.0, 4.7, 0.15, AMBAR]];
    for (let i = 0; i < nodes.length - 1; i++) {
      const [x1, y1] = nodes[i], [x2, y2] = nodes[i + 1];
      s.addShape("line", { x: Math.min(x1, x2) + 0.08, y: Math.min(y1, y2) + 0.08, w: Math.abs(x2 - x1), h: Math.abs(y2 - y1), line: { color: "3C5A72", width: 1.25 } });
    }
    for (const [x, y, d, color] of nodes) {
      s.addShape("ellipse", { x, y, w: d, h: d, fill: { color }, line: { type: "none" } });
    }
    iconCircle(s, { x: 0.75, y: 0.7, d: 0.62, icon: "FaStore", color: AZUL, tint: WHITE });
    s.addText("CODEX INNOVATIONS  ·  EQUIPO 04", {
      x: 0.75, y: 1.55, w: 8, h: 0.4, fontFace: F_BODY, fontSize: 13, bold: true,
      color: "9FB0C4", charSpacing: 1.8, isTextBox: true, margin: 0,
    });
    s.addText("Microhubs", {
      x: 0.72, y: 2.65, w: 10, h: 1.6, fontFace: F_HEAD, fontSize: 68, bold: true,
      color: WHITE, isTextBox: true, margin: 0,
    });
    s.addText("Comercio de proximidad para el sector San Bernabé", {
      x: 0.75, y: 3.95, w: 8.5, h: 0.6, fontFace: F_BODY, fontSize: 19,
      color: "CADCFC", isTextBox: true, margin: 0,
    });
    s.addText("Primer Parcial · Ingeniería de Software · Monterrey, Nuevo León", {
      x: 0.75, y: 6.55, w: 9, h: 0.4, fontFace: F_BODY, fontSize: 12.5,
      color: "7C93AC", isTextBox: true, margin: 0,
    });
  }

  // ==================================================================
  // 2. EL PROBLEMA
  // ==================================================================
  {
    const s = pres.addSlide();
    bg(s, WHITE);
    kicker(s, "El problema", AZUL);
    title(s, "La entrega rápida tradicional\nno cuadra en estas colonias", { size: 28, h: 1.3 });
    s.addText("Bajo poder adquisitivo, distancias cortas pero cobertura irregular, y márgenes que no toleran una operación de alto costo. El reto no es tecnológico primero — es de modelo de negocio.", {
      x: 0.7, y: 2.05, w: 5.3, h: 1.7, fontFace: F_BODY, fontSize: 13.5, color: INK2,
      isTextBox: true, margin: 0, lineSpacingMultiple: 1.3,
    });

    const items = [
      ["FaMoneyBillWave", AZUL, AZUL_TINT, "Bajo ticket promedio", "El gasto por pedido es pequeño."],
      ["FaCoins", VERDE, VERDE_TINT, "Alta sensibilidad al costo", "Un envío caro cancela la compra."],
      ["FaCity", AMBAR, AMBAR_TINT, "Densidad variable", "Unas colonias concentran, otras no."],
      ["FaRoad", VINO, VINO_TINT, "Infraestructura limitada", "Calles y accesos poco uniformes."],
      ["FaWifi", VIOLETA, VIOLETA_TINT, "Conectividad irregular", "No siempre hay datos estables."],
      ["FaPercentage", AZUL, AZUL_TINT, "Márgenes reducidos", "Poco espacio para ineficiencias."],
    ];
    const colW = 3.85, gx = 0.25, x0 = 6.35, y0 = 1.95;
    items.forEach((it, i) => {
      const col = i % 2, row = Math.floor(i / 2);
      const x = x0 + col * (colW + gx);
      const y = y0 + row * 1.55;
      cardIconLabel(s, { x, y, w: colW, h: 1.3, icon: it[0], color: it[1], tint: it[2], title: it[3], body: it[4] });
    });
    pageNum(s, 2);
  }

  // ==================================================================
  // 3. LA ZONA + EL INSIGHT DEL CP AMBIGUO
  // ==================================================================
  {
    const s = pres.addSlide();
    bg(s, WHITE);
    kicker(s, "Dónde opera", AZUL);
    title(s, "Cuatro colonias, una sola red", { size: 28 });

    const zonas = [
      ["San Bernabé", "CP 64100", "$70", AZUL, AZUL_TINT],
      ["Valles de San Bernabé", "CP 64103", "$80", VERDE, VERDE_TINT],
      ["Paseo de San Bernabé", "CP 64103", "$90", AMBAR, AMBAR_TINT],
      ["San Bernabé X (F-113)", "CP 64105", "$85", VIOLETA, VIOLETA_TINT],
    ];
    const cw = 2.85, gap = 0.22, x0 = 0.7, y0 = 2.0;
    zonas.forEach((z, i) => {
      const x = x0 + i * (cw + gap);
      s.addShape("roundRect", { x, y: y0, w: cw, h: 2.05, rectRadius: 0.1, fill: { color: z[4] }, line: { type: "none" } });
      s.addText(z[0], { x: x + 0.2, y: y0 + 0.22, w: cw - 0.4, h: 0.7, fontFace: F_BODY, fontSize: 14, bold: true, color: INK, isTextBox: true, margin: 0, lineSpacingMultiple: 1.05 });
      s.addText(z[1], { x: x + 0.2, y: y0 + 0.92, w: cw - 0.4, h: 0.3, fontFace: F_BODY, fontSize: 11, color: INK2, isTextBox: true, margin: 0 });
      s.addText(z[2], { x: x + 0.2, y: y0 + 1.28, w: cw - 0.4, h: 0.6, fontFace: F_HEAD, fontSize: 27, bold: true, color: z[3], isTextBox: true, margin: 0 });
      s.addText("pedido mínimo", { x: x + 0.2, y: y0 + 1.78, w: cw - 0.4, h: 0.25, fontFace: F_BODY, fontSize: 9.5, color: INK2, isTextBox: true, margin: 0 });
    });

    s.addShape("roundRect", { x: 0.7, y: 4.45, w: cw * 4 + gap * 3, h: 2.15, rectRadius: 0.12, fill: { color: AZUL_DARK }, line: { type: "none" } });
    iconCircle(s, { x: 1.0, y: 4.78, d: 0.75, icon: "FaSearchLocation", color: AZUL, tint: WHITE });
    s.addText("Dos colonias comparten el mismo código postal — con reglas distintas", {
      x: 2.05, y: 4.62, w: 9.4, h: 0.6, fontFace: F_BODY, fontSize: 14.5, bold: true, color: WHITE, isTextBox: true, margin: 0, lineSpacingMultiple: 1.1,
    });
    s.addText("Valles y Paseo de San Bernabé comparten el 64103, pero el pedido mínimo difiere en $10. Por eso la identidad real de una zona es (colonia + CP), nunca el CP solo — y cuando alguien consulta un CP ambiguo, el sistema pregunta la colonia en vez de adivinar.", {
      x: 2.05, y: 5.35, w: 9.4, h: 1.15, fontFace: F_BODY, fontSize: 11.5, color: "CADCFC", isTextBox: true, margin: 0, lineSpacingMultiple: 1.28,
    });
    pageNum(s, 3);
  }

  // ==================================================================
  // 4. OBJETIVOS DEL SISTEMA
  // ==================================================================
  {
    const s = pres.addSlide();
    bg(s, WHITE);
    kicker(s, "Alcance del sistema", VERDE);
    title(s, "Nueve capacidades para decidir con datos", { size: 26 });

    const obj = [
      ["FaChartBar", AZUL, AZUL_TINT, "Analizar demanda"],
      ["FaMapMarkerAlt", VERDE, VERDE_TINT, "Proponer ubicaciones"],
      ["FaSearchLocation", AMBAR, AMBAR_TINT, "Estimar cobertura"],
      ["FaCogs", VINO, VINO_TINT, "Simular operación"],
      ["FaWarehouse", VIOLETA, VIOLETA_TINT, "Calcular capacidad"],
      ["FaBoxes", AZUL, AZUL_TINT, "Planear surtido"],
      ["FaShoppingCart", VERDE, VERDE_TINT, "Gestionar pedidos"],
      ["FaTruck", AMBAR, AMBAR_TINT, "Optimizar entregas"],
      ["FaBalanceScale", VINO, VINO_TINT, "Punto de equilibrio"],
    ];
    const cw = 3.86, ch = 1.42, gx = 0.2, gy = 0.22, x0 = 0.7, y0 = 2.05;
    obj.forEach((o, i) => {
      const col = i % 3, row = Math.floor(i / 3);
      const x = x0 + col * (cw + gx), y = y0 + row * (ch + gy);
      s.addShape("roundRect", { x, y, w: cw, h: ch, rectRadius: 0.09, fill: { color: "F7F7F5" }, line: { type: "none" } });
      iconCircle(s, { x: x + 0.22, y: y + 0.24, d: 0.58, icon: o[0], color: o[1], tint: o[2] });
      s.addText(o[3], { x: x + 0.95, y: y, w: cw - 1.1, h: ch, fontFace: F_BODY, fontSize: 14, bold: true, color: INK, valign: "middle", isTextBox: true, margin: 0, lineSpacingMultiple: 1.05 });
    });
    pageNum(s, 4);
  }

  // ==================================================================
  // 4B. ANÁLISIS Y REQUERIMIENTOS
  // ==================================================================
  {
    const s = pres.addSlide();
    bg(s, WHITE);
    kicker(s, "Análisis y requerimientos", AZUL);
    title(s, "Antes de programar, entendimos el problema", { size: 27 });

    const stats = [
      ["50", "requerimientos\nfuncionales", AZUL],
      ["36", "requerimientos no\nfuncionales", VERDE],
      ["32", "historias de\nusuario", AMBAR],
      ["40", "reglas de\nnegocio", VINO],
      ["10", "casos de\nuso", VIOLETA],
    ];
    const cw = 2.22, ch = 1.9, gx = 0.16, x0 = 0.7, y0 = 2.05;
    stats.forEach((st, i) => {
      const x = x0 + i * (cw + gx);
      s.addShape("roundRect", { x, y: y0, w: cw, h: ch, rectRadius: 0.09, fill: { color: WHITE }, line: { color: "E4E4DD", width: 1 }, shadow: { type: "outer", color: "1B241F", opacity: 0.12, blur: 8, offset: 3, angle: 90 } });
      s.addText(st[0], { x: x + 0.15, y: y0 + 0.2, w: cw - 0.3, h: 0.95, fontFace: F_HEAD, fontSize: 42, bold: true, color: st[2], isTextBox: true, margin: 0 });
      s.addText(st[1], { x: x + 0.15, y: y0 + 1.18, w: cw - 0.3, h: 0.65, fontFace: F_BODY, fontSize: 12, color: INK2, isTextBox: true, margin: 0, lineSpacingMultiple: 1.1 });
    });

    s.addShape("roundRect", { x: 0.7, y: 4.35, w: 11.93, h: 1.05, rectRadius: 0.1, fill: { color: AZUL_TINT }, line: { type: "none" } });
    s.addText("Todo clasificado por componente", { x: 1.0, y: 4.5, w: 11.3, h: 0.32, fontFace: F_BODY, fontSize: 12.5, bold: true, color: AZUL, isTextBox: true, margin: 0 });
    s.addText("Web  ·  Microservicios  ·  Android  ·  Escritorio  ·  Infraestructura  ·  Seguridad  ·  Monitoreo", { x: 1.0, y: 4.85, w: 11.3, h: 0.4, fontFace: F_BODY, fontSize: 12, color: INK2, isTextBox: true, margin: 0 });

    s.addShape("roundRect", { x: 0.7, y: 5.6, w: 11.93, h: 1.05, rectRadius: 0.1, fill: { color: VERDE_TINT }, line: { type: "none" } });
    s.addText("Una matriz de trazabilidad conecta todo", { x: 1.0, y: 5.75, w: 11.3, h: 0.32, fontFace: F_BODY, fontSize: 12.5, bold: true, color: VERDE, isTextBox: true, margin: 0 });
    s.addText("Cada requisito apunta a su historia de usuario, su caso de uso y el componente que lo implementa — nada quedó suelto.", { x: 1.0, y: 6.1, w: 11.3, h: 0.4, fontFace: F_BODY, fontSize: 12, color: INK2, isTextBox: true, margin: 0 });
    pageNum(s, "4b");
  }

  // ==================================================================
  // 5. ARQUITECTURA: QUÉ SE CONSTRUYE Y CUÁNDO
  // ==================================================================
  {
    const s = pres.addSlide();
    bg(s, WHITE);
    kicker(s, "Arquitectura", VERDE);
    title(s, "Cuatro componentes, un plan de cuatro etapas", { size: 26 });
    s.addText("El Primer Parcial construye y prueba el sistema web de punta a punta. Los demás componentes ya están diseñados en los diagramas de arquitectura — se construyen después.", {
      x: 0.7, y: 1.62, w: 11.4, h: 0.5, fontFace: F_BODY, fontSize: 12.5, color: INK2, isTextBox: true, margin: 0,
    });

    const comps = [
      ["FaGlobe", "Sistema web", "Primer Parcial", true],
      ["FaNetworkWired", "Microservicios", "Segundo Parcial", false],
      ["FaMobileAlt", "App Android", "Segundo Parcial", false],
      ["FaDesktop", "App escritorio", "Segundo Parcial", false],
    ];
    const cw = 2.85, gap = 0.22, x0 = 0.7, y0 = 2.35;
    comps.forEach((c, i) => {
      const x = x0 + i * (cw + gap);
      const on = c[3];
      s.addShape("roundRect", {
        x, y: y0, w: cw, h: 2.55, rectRadius: 0.1,
        fill: { color: on ? AZUL : "F2F2EE" }, line: { type: "none" },
      });
      iconCircle(s, { x: x + cw / 2 - 0.4, y: y0 + 0.32, d: 0.8, icon: c[0], color: on ? AZUL : INK2, tint: on ? WHITE : "E4E4DD" });
      s.addText(c[1], { x: x + 0.15, y: y0 + 1.3, w: cw - 0.3, h: 0.5, fontFace: F_BODY, fontSize: 15, bold: true, color: on ? WHITE : INK, align: "center", isTextBox: true, margin: 0 });
      s.addText(c[2], { x: x + 0.15, y: y0 + 1.85, w: cw - 0.3, h: 0.4, fontFace: F_BODY, fontSize: 11, color: on ? "CADCFC" : INK2, align: "center", isTextBox: true, margin: 0 });
      s.addText(on ? "✓ Construido y probado" : "Ya diseñado en los diagramas", {
        x: x + 0.15, y: y0 + 2.2, w: cw - 0.3, h: 0.3, fontFace: F_BODY, fontSize: 9.5, bold: on, color: on ? WHITE : INK2, align: "center", isTextBox: true, margin: 0,
      });
    });
    s.addText("Debajo de los cuatro: PostgreSQL · MongoDB · Redis — la capa de datos compartida que ya está diseñada y en operación.", {
      x: 0.7, y: 5.25, w: 11.4, h: 0.4, fontFace: F_BODY, fontSize: 11.5, italic: true, color: INK2, isTextBox: true, margin: 0,
    });
    pageNum(s, 5);
  }

  // ==================================================================
  // 6. LA DECISIÓN CLAVE (slide oscura de impacto)
  // ==================================================================
  {
    const s = pres.addSlide();
    bg(s, AZUL_DARK);
    kicker(s, "Decisión de diseño");
    s.getObjects && null;
    s.addText("LA DECISIÓN CENTRAL", {
      x: 0.7, y: 0.55, w: 8, h: 0.35, fontFace: F_BODY, fontSize: 12.5, bold: true, color: "8FE0B8", charSpacing: 1.5, isTextBox: true, margin: 0,
    });
    s.addText("Las reglas de negocio\nno viven en Python.", {
      x: 0.7, y: 1.05, w: 8.5, h: 1.9, fontFace: F_HEAD, fontSize: 34, bold: true, color: WHITE, isTextBox: true, margin: 0, lineSpacingMultiple: 1.05,
    });
    s.addText("Viven en PostgreSQL, como restricciones, funciones y disparadores. Por eso no hay ORM: la aplicación abre la transacción, dice quién actúa, y llama a la función del motor.", {
      x: 0.7, y: 3.05, w: 7.3, h: 1.1, fontFace: F_BODY, fontSize: 14, color: "CADCFC", isTextBox: true, margin: 0, lineSpacingMultiple: 1.3,
    });

    const rows = [
      ["Sobreventa", "Imposible: es un CHECK del motor, no una validación que alguien podría olvidar."],
      ["Bitácora", "Inmutable por diseño: ni un administrador puede editarla o borrarla."],
      ["Transiciones de estado", "Una tabla de reglas decide qué cambio es válido — no si condicionales dispersos."],
    ];
    let y = 4.35;
    rows.forEach((r) => {
      iconCircle(s, { x: 0.7, y, d: 0.42, icon: "FaCheckCircle", color: AZUL_DARK, tint: "8FE0B8" });
      s.addText(r[0], { x: 1.3, y: y - 0.05, w: 2.3, h: 0.5, fontFace: F_BODY, fontSize: 13, bold: true, color: WHITE, isTextBox: true, margin: 0 });
      s.addText(r[1], { x: 3.75, y: y - 0.05, w: 8.2, h: 0.55, fontFace: F_BODY, fontSize: 11.5, color: "9FB0C4", isTextBox: true, margin: 0, lineSpacingMultiple: 1.15 });
      y += 0.72;
    });
    pageNum(s, 6);
  }

  // ==================================================================
  // 7. EL MODELO DE DATOS EN NÚMEROS
  // ==================================================================
  {
    const s = pres.addSlide();
    bg(s, WHITE);
    kicker(s, "Modelo de datos", AZUL);
    title(s, "Un motor con reglas de verdad, no de adorno", { size: 26 });

    const stats = [
      ["24", "tablas", AZUL],
      ["41", "restricciones CHECK", VERDE],
      ["37", "llaves foráneas", AMBAR],
      ["66", "índices", VINO],
      ["19", "funciones", VIOLETA],
      ["22", "disparadores (triggers)", AZUL],
      ["8", "enums de dominio", VERDE],
      ["3", "vistas de indicadores", AMBAR],
    ];
    const cw = 2.75, ch = 1.75, gx = 0.2, gy = 0.2, x0 = 0.7, y0 = 2.1;
    stats.forEach((st, i) => {
      const col = i % 4, row = Math.floor(i / 4);
      const x = x0 + col * (cw + gx), y = y0 + row * (ch + gy);
      s.addShape("roundRect", { x, y, w: cw, h: ch, rectRadius: 0.09, fill: { color: WHITE }, line: { color: "E4E4DD", width: 1 }, shadow: { type: "outer", color: "1B241F", opacity: 0.12, blur: 8, offset: 3, angle: 90 } });
      s.addText(st[0], { x: x + 0.18, y: y + 0.18, w: cw - 0.36, h: 0.95, fontFace: F_HEAD, fontSize: 40, bold: true, color: st[2], isTextBox: true, margin: 0 });
      s.addText(st[1], { x: x + 0.18, y: y + 1.15, w: cw - 0.36, h: 0.5, fontFace: F_BODY, fontSize: 11.5, color: INK2, isTextBox: true, margin: 0 });
    });
    pageNum(s, 7);
  }

  // ==================================================================
  // 8. TRES BASES, UN PROPÓSITO CADA UNA
  // ==================================================================
  {
    const s = pres.addSlide();
    bg(s, WHITE);
    kicker(s, "Persistencia poliglota", VERDE);
    title(s, "Cada dato vive donde su naturaleza lo pide", { size: 26 });

    const dbs = [
      ["FaDatabase", AZUL, AZUL_TINT, "PostgreSQL", "Transaccional", "Pedidos, inventario, pagos: si se pierde, rompe un saldo o una relación."],
      ["FaLayerGroup", VERDE, VERDE_TINT, "MongoDB", "Documentos flexibles", "Eventos, telemetría e historial: si se pierde, solo estorba un análisis."],
      ["FaBolt", AMBAR, AMBAR_TINT, "Redis", "Caché y sesiones", "Carrito, tokens revocados, bloqueos: si se pierde, solo obliga a rehacer."],
    ];
    const cw = 3.75, gap = 0.25, x0 = 0.7, y0 = 2.05;
    dbs.forEach((d, i) => {
      const x = x0 + i * (cw + gap);
      s.addShape("roundRect", { x, y: y0, w: cw, h: 3.1, rectRadius: 0.1, fill: { color: d[2] }, line: { type: "none" } });
      iconCircle(s, { x: x + 0.28, y: y0 + 0.3, d: 0.75, icon: d[0], color: d[1], tint: WHITE });
      s.addText(d[3], { x: x + 0.28, y: y0 + 1.2, w: cw - 0.56, h: 0.45, fontFace: F_BODY, fontSize: 17, bold: true, color: INK, isTextBox: true, margin: 0 });
      s.addText(d[4].toUpperCase(), { x: x + 0.28, y: y0 + 1.62, w: cw - 0.56, h: 0.3, fontFace: F_BODY, fontSize: 10, bold: true, color: d[1], charSpacing: 1, isTextBox: true, margin: 0 });
      s.addText(d[5], { x: x + 0.28, y: y0 + 2.0, w: cw - 0.56, h: 1.0, fontFace: F_BODY, fontSize: 11, color: INK2, isTextBox: true, margin: 0, lineSpacingMultiple: 1.25 });
    });
    s.addText("Redis usa dos bases lógicas con políticas distintas: la de bloqueos de inventario nunca expulsa datos; la de caché sí. Unificarlas podría provocar sobreventa en un pico de tráfico.", {
      x: 0.7, y: 5.4, w: 11.4, h: 0.5, fontFace: F_BODY, fontSize: 11.5, italic: true, color: INK2, isTextBox: true, margin: 0,
    });
    pageNum(s, 8);
  }

  // ==================================================================
  // 9. VERIFICADO DE VERDAD (slide oscura de prueba)
  // ==================================================================
  {
    const s = pres.addSlide();
    bg(s, AZUL_DARK);
    kicker(s, "Evidencia, no promesas");
    s.addText("VERIFICADO DE VERDAD", {
      x: 0.7, y: 0.55, w: 8, h: 0.35, fontFace: F_BODY, fontSize: 12.5, bold: true, color: "8FE0B8", charSpacing: 1.5, isTextBox: true, margin: 0,
    });
    title(s, "No describimos lo que debería pasar.\nLo corrimos.", { size: 30, color: WHITE, y: 1.05, h: 1.6 });

    const proofs = [
      ["FaCheckCircle", "26 / 26 reglas de negocio", "VR-01 a VR-16 verificadas contra PostgreSQL real, incluida sobreventa bajo concurrencia."],
      ["FaDocker", "4 contenedores sanos", "PostgreSQL, Redis, MongoDB y la app web, levantados con un solo comando."],
      ["FaDatabase", "Datos reales, no de mentira", "51 productos · 148 pedidos · 3,113 registros de bitácora · 48 usuarios."],
      ["FaGlobe", "Recorridos probados en vivo", "Login, roles, cobertura ambigua, ticket mínimo, panel e indicadores."],
    ];
    const cw = 5.65, ch = 1.55, gx = 0.3, gy = 0.25, x0 = 0.7, y0 = 3.1;
    proofs.forEach((p, i) => {
      const col = i % 2, row = Math.floor(i / 2);
      const x = x0 + col * (cw + gx), y = y0 + row * (ch + gy);
      iconCircle(s, { x, y: y + 0.1, d: 0.6, icon: p[0], color: AZUL_DARK, tint: "8FE0B8" });
      s.addText(p[1], { x: x + 0.78, y: y, w: cw - 0.78, h: 0.4, fontFace: F_BODY, fontSize: 14, bold: true, color: WHITE, isTextBox: true, margin: 0 });
      s.addText(p[2], { x: x + 0.78, y: y + 0.4, w: cw - 0.78, h: 1.0, fontFace: F_BODY, fontSize: 10.5, color: "9FB0C4", isTextBox: true, margin: 0, lineSpacingMultiple: 1.2 });
    });
    pageNum(s, 9);
  }

  // ==================================================================
  // 9B. ASÍ SE VE HOY (capturas reales)
  // ==================================================================
  {
    const s = pres.addSlide();
    bg(s, WHITE);
    kicker(s, "Capturas reales", VERDE);
    title(s, "Así se ve hoy — no es una maqueta", { size: 27 });

    const shots = [
      [path.join(CAP_DIR, "01_catalogo.png"), AZUL, "Catálogo público", "Consulta libre, datos reales de PostgreSQL"],
      [path.join(CAP_DIR, "02_cobertura.png"), AMBAR, "Cobertura con CP ambiguo", "64103 pregunta la colonia en vez de adivinar"],
      [path.join(CAP_DIR, "03_indicadores.png"), VERDE, "Panel de indicadores", "148 pedidos y 3 microhubs, en vivo"],
      [path.join(CAP_DIR, "04_bitacora.png"), VIOLETA, "Bitácora de auditoría", "3,115 registros, ninguno editable"],
    ];
    const cw = 5.84, ch = 2.35, gx = 0.25, gy = 0.28, x0 = 0.7, y0 = 1.78;
    shots.forEach((sh, i) => {
      const col = i % 2, row = Math.floor(i / 2);
      const x = x0 + col * (cw + gx), y = y0 + row * (ch + gy + 0.42);
      s.addShape("rect", { x: x - 0.02, y: y - 0.02, w: cw + 0.04, h: ch + 0.04, fill: { color: sh[1] }, line: { type: "none" } });
      s.addImage({ path: sh[0], x, y, w: cw, h: ch, sizing: { type: "cover", w: cw, h: ch } });
      s.addText(sh[2], { x, y: y + ch + 0.06, w: cw, h: 0.28, fontFace: F_BODY, fontSize: 12.5, bold: true, color: INK, isTextBox: true, margin: 0 });
      s.addText(sh[3], { x, y: y + ch + 0.32, w: cw, h: 0.25, fontFace: F_BODY, fontSize: 10, color: INK2, isTextBox: true, margin: 0 });
    });
    pageNum(s, "9b");
  }

  // ==================================================================
  // 10. PRODUCTO MÍNIMO FUNCIONAL
  // ==================================================================
  {
    const s = pres.addSlide();
    bg(s, WHITE);
    kicker(s, "Lo que ya funciona", VERDE);
    title(s, "El sistema web, de punta a punta", { size: 28 });

    const feats = [
      ["FaGlobe", AZUL, AZUL_TINT, "Sitio público", "Catálogo y cobertura, sin necesidad de cuenta."],
      ["FaLock", VERDE, VERDE_TINT, "JWT + roles", "Sesión, permisos y revocación en Redis."],
      ["FaHistory", AMBAR, AMBAR_TINT, "Bitácora automática", "La escribe el motor, nadie puede alterarla."],
      ["FaShoppingCart", VINO, VINO_TINT, "Proceso de pedido completo", "Carrito → asignación → preparación → entrega."],
      ["FaChartBar", VIOLETA, VIOLETA_TINT, "Panel de indicadores", "Tasa de entrega y demanda no atendida, en vivo."],
      ["FaUserShield", AZUL, AZUL_TINT, "Control por ruta", "Cada acción se verifica, no solo se oculta del menú."],
    ];
    const cw = 3.86, gx = 0.2, gy = 0.28, x0 = 0.7, y0 = 2.0;
    feats.forEach((f, i) => {
      const col = i % 3, row = Math.floor(i / 3);
      const x = x0 + col * (cw + gx), y = y0 + row * 1.75;
      cardIconLabel(s, { x, y, w: cw, h: 1.55, icon: f[0], color: f[1], tint: f[2], title: f[3], body: f[4] });
    });
    pageNum(s, 10);
  }

  // ==================================================================
  // 10B. PERFILES Y CONTROL DE ACCESO
  // ==================================================================
  {
    const s = pres.addSlide();
    bg(s, WHITE);
    kicker(s, "Perfiles", VERDE);
    title(s, "Seis perfiles, cada uno con su ámbito", { size: 27 });

    const roles = [
      ["FaUserShield", AZUL, "Administrador", "Configuración y administración global"],
      ["FaWarehouse", VERDE, "Operador", "Operación del microhub"],
      ["FaChartBar", AMBAR, "Planeador", "Análisis y planeación"],
      ["FaShoppingCart", VINO, "Cliente", "Catálogo y pedidos"],
      ["FaTruck", AMBAR, "Repartidor", "Entregas"],
      ["FaHistory", VIOLETA, "Auditor", "Consulta y auditoría"],
    ];
    const rx = 0.7, rw = 7.1, ry0 = 2.05, rh = 0.76;
    roles.forEach((r, i) => {
      const y = ry0 + i * rh;
      iconCircle(s, { x: rx, y: y + 0.08, d: 0.5, icon: r[0], color: r[1], tint: r[1] === AMBAR ? AMBAR_TINT : r[1] === VERDE ? VERDE_TINT : r[1] === VINO ? VINO_TINT : r[1] === VIOLETA ? VIOLETA_TINT : AZUL_TINT });
      s.addText(r[2], { x: rx + 0.68, y: y, w: 2.3, h: rh, fontFace: F_BODY, fontSize: 14, bold: true, color: INK, valign: "middle", isTextBox: true, margin: 0 });
      s.addText(r[3], { x: rx + 3.0, y: y, w: rw - 3.0, h: rh, fontFace: F_BODY, fontSize: 12.5, color: INK2, valign: "middle", isTextBox: true, margin: 0 });
      if (i < roles.length - 1) s.addShape("line", { x: rx, y: y + rh, w: rw, h: 0, line: { color: "EAEAE2", width: 1 } });
    });

    const principles = [
      "Permisos diferentes por perfil",
      "Restricción por microhub / usuario",
      "Validación también en el backend, no solo visual",
      "Menús adaptados al perfil",
    ];
    const px = 8.25, pw = 4.4, py0 = 2.15;
    principles.forEach((p, i) => {
      const y = py0 + i * 1.15;
      iconCircle(s, { x: px, y, d: 0.5, icon: "FaCheckCircle", color: VERDE, tint: VERDE_TINT });
      s.addText(p, { x: px + 0.68, y: y - 0.05, w: pw - 0.68, h: 0.85, fontFace: F_BODY, fontSize: 13, bold: true, color: INK, valign: "middle", isTextBox: true, margin: 0, lineSpacingMultiple: 1.15 });
    });
    pageNum(s, "10b");
  }

  // ==================================================================
  // 11. SEGURIDAD POR DISEÑO
  // ==================================================================
  {
    const s = pres.addSlide();
    bg(s, WHITE);
    kicker(s, "Seguridad", VINO);
    title(s, "Seguridad por diseño, no por buena voluntad", { size: 27 });

    const sec = [
      ["FaKey", VERDE, VERDE_TINT, "Contraseñas con hash seguro", "bcrypt, nunca texto plano ni reversible."],
      ["FaLock", AZUL, AZUL_TINT, "JWT de corta duración", "Con revocación inmediata desde Redis."],
      ["FaUserShield", AMBAR, AMBAR_TINT, "Control por rol y por ruta", "Cada endpoint valida el permiso, siempre."],
      ["FaHistory", VIOLETA, VIOLETA_TINT, "Bitácora inmutable", "Registra también los accesos denegados."],
    ];
    const cw = 5.65, gx = 0.3, gy = 0.3, x0 = 0.7, y0 = 2.15;
    sec.forEach((it, i) => {
      const col = i % 2, row = Math.floor(i / 2);
      const x = x0 + col * (cw + gx), y = y0 + row * 1.9;
      cardIconLabel(s, { x, y, w: cw, h: 1.7, icon: it[0], color: it[1], tint: it[2], title: it[3], body: it[4] });
    });
    pageNum(s, 11);
  }

  // ==================================================================
  // 11B. RETOS Y DECISIONES TÉCNICAS
  // ==================================================================
  {
    const s = pres.addSlide();
    bg(s, WHITE);
    kicker(s, "Lecciones del camino", VINO);
    title(s, "Cuatro retos que sí nos costó resolver", { size: 26 });

    const rows = [
      [AZUL, "Concurrencia de inventario", "Dos pedidos pueden intentar consumir la última unidad al mismo tiempo.", "Validaciones transaccionales + bloqueos temporales en el motor."],
      [VERDE, "Permisos por URL", "Ocultar un botón del menú no impide entrar por la dirección directa.", "Autorización desde el backend en cada ruta — responde 403 y lo audita."],
      [AMBAR, "Tipos de datos distintos", "No toda la información necesita el mismo tipo de almacenamiento.", "PostgreSQL + MongoDB + Redis, cada uno con un criterio explícito."],
      [VIOLETA, "Crecimiento del sistema", "Después hay que integrar web, móvil, escritorio y microservicios.", "Arquitectura separada por responsabilidades desde el Primer Parcial."],
    ];
    const x0 = 0.7, y0 = 2.05, rh = 1.18, colReto = 3.0, colProb = 4.6, colSol = 4.15;
    // encabezados
    s.addText("RETO", { x: x0, y: y0 - 0.42, w: colReto, h: 0.3, fontFace: F_BODY, fontSize: 11, bold: true, color: INK2, charSpacing: 1, isTextBox: true, margin: 0 });
    s.addText("PROBLEMA", { x: x0 + colReto + 0.15, y: y0 - 0.42, w: colProb, h: 0.3, fontFace: F_BODY, fontSize: 11, bold: true, color: INK2, charSpacing: 1, isTextBox: true, margin: 0 });
    s.addText("SOLUCIÓN", { x: x0 + colReto + colProb + 0.3, y: y0 - 0.42, w: colSol, h: 0.3, fontFace: F_BODY, fontSize: 11, bold: true, color: INK2, charSpacing: 1, isTextBox: true, margin: 0 });
    s.addShape("line", { x: x0, y: y0 - 0.1, w: colReto + colProb + colSol + 0.45, h: 0, line: { color: "DEDED4", width: 1 } });

    rows.forEach((r, i) => {
      const y = y0 + i * rh;
      s.addShape("rect", { x: x0, y: y + 0.06, w: 0.06, h: rh - 0.3, fill: { color: r[0] }, line: { type: "none" } });
      s.addText(r[1], { x: x0 + 0.22, y, w: colReto - 0.22, h: rh - 0.15, fontFace: F_BODY, fontSize: 13.5, bold: true, color: INK, valign: "top", isTextBox: true, margin: 0, lineSpacingMultiple: 1.15 });
      s.addText(r[2], { x: x0 + colReto + 0.15, y, w: colProb, h: rh - 0.15, fontFace: F_BODY, fontSize: 11.5, color: INK2, valign: "top", isTextBox: true, margin: 0, lineSpacingMultiple: 1.2 });
      s.addText(r[3], { x: x0 + colReto + colProb + 0.3, y, w: colSol, h: rh - 0.15, fontFace: F_BODY, fontSize: 11.5, color: INK, valign: "top", isTextBox: true, margin: 0, lineSpacingMultiple: 1.2 });
      if (i < rows.length - 1) s.addShape("line", { x: x0, y: y + rh - 0.12, w: colReto + colProb + colSol + 0.45, h: 0, line: { color: "EAEAE2", width: 1 } });
    });
    pageNum(s, "11b");
  }

  // ==================================================================
  // 12. LO QUE SIGUE (timeline)
  // ==================================================================
  {
    const s = pres.addSlide();
    bg(s, WHITE);
    kicker(s, "Ruta del semestre", AZUL);
    title(s, "Cuatro etapas, un incremento funcional cada vez", { size: 25 });

    const stages = [
      ["1", "Primer Parcial", "Análisis, arquitectura y sistema web mínimo funcional", true],
      ["2", "Segundo Parcial", "Microservicios, app Android y app de escritorio", false],
      ["3", "Tercer Parcial", "Integración completa, nube, seguridad y escalabilidad", false],
      ["4", "Entrega Final", "Estabilización, pruebas de carga y documentación integral", false],
    ];
    const y = 3.0, r = 0.32, xStart = 1.3, xEnd = 12.0;
    s.addShape("line", { x: xStart + r, y: y + r, w: xEnd - xStart - 2 * r, h: 0, line: { color: "DEDED4", width: 2.5 } });
    const step = (xEnd - xStart) / 3;
    stages.forEach((st, i) => {
      const x = xStart + step * i;
      s.addShape("ellipse", { x, y, w: r * 2, h: r * 2, fill: { color: st[3] ? AZUL : "E4E4DD" }, line: { type: "none" } });
      s.addText(st[0], { x, y, w: r * 2, h: r * 2, fontFace: F_BODY, fontSize: 15, bold: true, color: st[3] ? WHITE : INK2, align: "center", valign: "middle", isTextBox: true, margin: 0 });
      s.addText(st[1], { x: x - 0.85, y: y + r * 2 + 0.25, w: 2.7, h: 0.4, fontFace: F_BODY, fontSize: 13.5, bold: true, color: st[3] ? AZUL : INK, align: "center", isTextBox: true, margin: 0 });
      s.addText(st[2], { x: x - 0.95, y: y + r * 2 + 0.68, w: 2.9, h: 1.3, fontFace: F_BODY, fontSize: 10.5, color: INK2, align: "center", isTextBox: true, margin: 0, lineSpacingMultiple: 1.2 });
      if (st[3]) {
        s.addText("HOY", { x: x - 0.3, y: y - 0.42, w: 0.9, h: 0.3, fontFace: F_BODY, fontSize: 9.5, bold: true, color: AZUL, align: "center", isTextBox: true, margin: 0 });
      }
    });

    s.addShape("roundRect", { x: 0.7, y: 5.75, w: 11.93, h: 1.15, rectRadius: 0.1, fill: { color: AMBAR_TINT }, line: { type: "none" } });
    s.addText("En proceso ahora mismo", { x: 1.0, y: 5.9, w: 4, h: 0.3, fontFace: F_BODY, fontSize: 12.5, bold: true, color: AMBAR, isTextBox: true, margin: 0 });
    s.addText("Integración completa del web con MongoDB   ·   catálogos administrativos adicionales   ·   refinamiento de pruebas y documentación", {
      x: 1.0, y: 6.25, w: 11.3, h: 0.5, fontFace: F_BODY, fontSize: 12, color: INK2, isTextBox: true, margin: 0, lineSpacingMultiple: 1.2,
    });
    pageNum(s, 12);
  }

  // ==================================================================
  // 13. CIERRE
  // ==================================================================
  {
    const s = pres.addSlide();
    bg(s, AZUL_DARK);
    iconCircle(s, { x: W / 2 - 0.5, y: 1.15, d: 1.0, icon: "FaStore", color: AZUL, tint: WHITE });
    s.addText("Gracias", {
      x: 0, y: 2.35, w: W, h: 1.0, fontFace: F_HEAD, fontSize: 46, bold: true, color: WHITE, align: "center", isTextBox: true, margin: 0,
    });
    s.addText("Comercio de proximidad, con reglas que no se pueden romper.", {
      x: 1.5, y: 3.35, w: W - 3, h: 0.5, fontFace: F_BODY, fontSize: 15, italic: true, color: "CADCFC", align: "center", isTextBox: true, margin: 0,
    });
    s.addText("Ruth Elizabeth Soriano   ·   Vanessa Morante López   ·   Mauro Castillo Peña\nMaría José Cedillo Mata   ·   Jorge Antonio Arreola Cantú", {
      x: 1, y: 4.55, w: W - 2, h: 0.9, fontFace: F_BODY, fontSize: 12.5, color: "9FB0C4", align: "center", isTextBox: true, margin: 0, lineSpacingMultiple: 1.4,
    });
    s.addText("Codex Innovations · Equipo 04", {
      x: 0, y: 6.7, w: W, h: 0.4, fontFace: F_BODY, fontSize: 11, color: "5C7691", align: "center", isTextBox: true, margin: 0,
    });
  }

  await pres.writeFile({ fileName: "Microhubs_Presentacion.pptx" });
  console.log("listo");
}

main().catch((e) => { console.error(e); process.exit(1); });
