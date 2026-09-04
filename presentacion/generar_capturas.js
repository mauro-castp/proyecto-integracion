const puppeteer = require("puppeteer-core");
const path = require("path");

const CHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const OUT = __dirname + "/capturas";

async function shot(page, url, file, opts = {}) {
  await page.goto(url, { waitUntil: "networkidle0" });
  if (opts.before) await opts.before(page);
  await new Promise((r) => setTimeout(r, 300));
  await page.screenshot({ path: path.join(OUT, file) });
  console.log("guardado", file);
}

async function main() {
  const fs = require("fs");
  fs.mkdirSync(OUT, { recursive: true });

  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: true,
    defaultViewport: { width: 1280, height: 800, deviceScaleFactor: 2 },
  });
  const page = await browser.newPage();

  // 1. Catálogo público (sin sesión)
  await shot(page, "http://localhost:5000/", "01_catalogo.png");

  // 2. Cobertura con CP ambiguo
  await shot(page, "http://localhost:5000/cobertura?zona=64103", "02_cobertura.png");

  // 3. Login como admin
  await page.goto("http://localhost:5000/entrar", { waitUntil: "networkidle0" });
  await page.type("#correo", "admin@codex.mx");
  await page.type("#clave", "Codex#2026");
  await Promise.all([
    page.waitForNavigation({ waitUntil: "networkidle0" }),
    page.click("button.btn"),
  ]);

  // 4. Indicadores (ya con sesión)
  await shot(page, "http://localhost:5000/indicadores", "03_indicadores.png");

  // 5. Bitácora
  await shot(page, "http://localhost:5000/bitacora", "04_bitacora.png");

  // 6. Bandeja del turno (para mostrar el flujo operativo) -- como admin no hay microhub asignado, usamos operador
  await page.goto("http://localhost:5000/salir", { waitUntil: "networkidle0" }).catch(() => {});
  // logout via POST form; navigate then submit
  await page.goto("http://localhost:5000/", { waitUntil: "networkidle0" });
  await page.evaluate(() => {
    const f = document.querySelector('form[action*="/salir"]');
    if (f) f.submit();
  });
  await new Promise((r) => setTimeout(r, 500));
  await page.goto("http://localhost:5000/entrar", { waitUntil: "networkidle0" });
  await page.type("#correo", "operador.mh01@codex.mx");
  await page.type("#clave", "Codex#2026");
  await Promise.all([
    page.waitForNavigation({ waitUntil: "networkidle0" }),
    page.click("button.btn"),
  ]);
  await shot(page, "http://localhost:5000/operacion", "05_bandeja.png");

  await browser.close();
  console.log("listo todas las capturas");
}

main().catch((e) => { console.error(e); process.exit(1); });
