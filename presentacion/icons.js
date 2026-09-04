const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const Fa = require("react-icons/fa");

const cache = {};

async function renderIcon(name, colorHex, px = 256) {
  const key = name + ":" + colorHex + ":" + px;
  if (cache[key]) return cache[key];
  const Icon = Fa[name];
  if (!Icon) throw new Error("Unknown icon " + name);
  const svg = ReactDOMServer.renderToStaticMarkup(
    React.createElement(Icon, { color: "#" + colorHex, size: px })
  );
  const full = `<svg xmlns="http://www.w3.org/2000/svg" width="${px}" height="${px}" viewBox="0 0 ${px} ${px}">${svg.replace(/^<svg[^>]*>/, "").replace(/<\/svg>$/, "")}</svg>`;
  const buf = await sharp(Buffer.from(full)).png().toBuffer();
  const dataUri = "image/png;base64," + buf.toString("base64");
  cache[key] = dataUri;
  return dataUri;
}

module.exports = { renderIcon };
