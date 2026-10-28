// Dos diapositivas que enseñan el mockup de acogimiento (pantalla «Seguimiento del proceso»)
// con capturas y muy poco texto. Mismo estilo que la de flujo y pain points.
// Uso: node build_mockup_acogimiento.js <carpeta de capturas> <salida.pptx>
const path = require('path');
const pptxgen = require('pptxgenjs');

const IMG = process.argv[2] || path.join(__dirname, 'img_acogimiento');
const OUT = process.argv[3] || 'Mockup_Acogimiento_Seguimiento.pptx';
const TAM = require(path.join(IMG, 'sizes.json'));          // ancho y alto de cada captura
const C = { rosa: 'F4A7AF', rosaBorde: 'F0C5CA', rojo: 'C0172E', negro: '1A1A1A', gris: '595959', grisClaro: '8C8C8C',
  blanco: 'FFFFFF', fondo: 'FAFAFA', marco: 'DADCE3', granate: '5A1A22' };
const F = 'Calibri', FT = 'Century Gothic';

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';
pres.title = 'Mockup · Seguimiento del proceso · Acogimiento familiar';

function diapositiva(subtitulo) {
  const s = pres.addSlide();
  s.background = { color: C.blanco };
  s.addShape(pres.ShapeType.roundRect, { x: 0.38, y: 0.3, w: 12.55, h: 0.95, rectRadius: 0.2, fill: { color: C.rosa }, line: { type: 'none' }, objectName: 'Banda del título' });
  s.addText([
    { text: '3. Mockup · Seguimiento del proceso', options: { fontFace: FT, bold: true, fontSize: 24, color: C.negro } },
    { text: '   ' + subtitulo, options: { fontFace: FT, fontSize: 15, color: C.granate } },
  ], { x: 0.78, y: 0.38, w: 11.8, h: 0.55, valign: 'middle', margin: 0, isTextBox: true, objectName: 'Título' });
  s.addShape(pres.ShapeType.roundRect, { x: 0.33, y: 0.98, w: 12.7, h: 6.35, rectRadius: 0.15, fill: { color: C.blanco }, line: { color: 'E3E3E3', width: 1 },
    shadow: { type: 'outer', blur: 6, offset: 2, angle: 90, color: '000000', opacity: 0.14 }, objectName: 'Tarjeta' });
  s.addText('Maqueta con datos ficticios · Fuentes previstas: GPME, AME y Nexus', { x: 7.2, y: 7.06, w: 5.6, h: 0.18, fontFace: F, fontSize: 7.5,
    italic: true, color: C.grisClaro, align: 'right', margin: 0, isTextBox: true });
  return s;
}
// captura con marco y sombra, ajustada sin deformar dentro de w × h
function captura(s, nombre, x, y, w, h, alt) {
  const [iw, ih] = TAM[nombre], k = Math.min(w / iw, h / ih), cw = iw * k, ch = ih * k, cx = x + (w - cw) / 2, cy = y;
  s.addShape(pres.ShapeType.rect, { x: cx - 0.03, y: cy - 0.03, w: cw + 0.06, h: ch + 0.06, fill: { color: C.blanco }, line: { color: C.marco, width: 0.75 },
    shadow: { type: 'outer', blur: 5, offset: 1.5, angle: 90, color: '000000', opacity: 0.16 } });
  s.addImage({ path: path.join(IMG, nombre + '.png'), x: cx, y: cy, w: cw, h: ch, altText: alt });
  return { x: cx, y: cy, w: cw, h: ch };
}
function marca(s, cx, cy, n, d = 0.28) {
  s.addShape(pres.ShapeType.ellipse, { x: cx - d / 2, y: cy - d / 2, w: d, h: d, fill: { color: C.rojo }, line: { color: C.blanco, width: 1.25 }, objectName: 'Marca ' + n });
  s.addText(String(n), { x: cx - d / 2, y: cy - d / 2, w: d, h: d, fontFace: F, fontSize: 10.5, bold: true, color: C.blanco, align: 'center', valign: 'middle', margin: 0, isTextBox: true });
}
// leyenda: marca + título + una línea
function rotulo(s, x, y, w, n, tit, linea) {
  marca(s, x + 0.14, y + 0.13, n);
  s.addText([
    { text: tit, options: { fontFace: F, fontSize: 11, bold: true, color: C.negro, breakLine: true } },
    { text: linea, options: { fontFace: F, fontSize: 8.5, color: C.gris } },
  ], { x: x + 0.36, y, w: w - 0.36, h: 0.5, valign: 'top', margin: 0, isTextBox: true, paraSpaceAfter: 1 });
}

/* ═══════════ 1 · visión de punta a punta y cabecera ═══════════ */
{
  const s = diapositiva('Visión de punta a punta');
  const im = captura(s, 'top', 0.78, 1.3, 11.9, 4.3, 'Cabecera de la pantalla: filtros, recorrido del pleno a la nómina, las dos partes e indicadores');
  const k = im.h / (TAM.top[1] / 2);                        // pulgadas por píxel de la pantalla (captura a 2x)
  [[145, 1], [205, 2], [266, 3], [429, 4]].forEach(([py, n]) => marca(s, 0.54, im.y + py * k, n));
  const L = [
    ['Filtros', 'Periodo, hecho, procedimiento, tipo de acogimiento y notificación'],
    ['Del pleno a la nómina', 'El recorrido en 3 tramos, con el tiempo perdido antes de AME a la vista'],
    ['Antes y después del pleno', 'Lo que hace Protección, en resumen, y la prestación en AME, completa'],
    ['Indicadores clave', 'Del pleno a AME, tramitación, tiempos, retrabajo y gestión económica'],
  ];
  L.forEach(([t, l], i) => rotulo(s, 0.7 + i * 3.05, 6.05, 2.95, i + 1, t, l));
}

/* ═══════════ 2 · análisis y detalle ═══════════ */
{
  const s = diapositiva('Análisis y detalle');
  const XL = 0.65, WC = 3.65, GX = 0.2, XR = 8.45, WR = 4.3;
  const IZQ = [
    ['sec1', 'Tiempo por fase', 'Días y procedimientos en cada fase'],
    ['sec2', 'Entradas, salidas y pendientes', 'El ritmo, mes a mes o por propuesta mensual'],
    ['sec3', 'Tiempo perdido del pleno a AME', 'Acuerdos que llegan tarde y lo que cuestan'],
    ['sec4', 'Pendientes por antigüedad', 'Lo abierto hoy, por fase y antigüedad'],
  ];
  IZQ.forEach(([img, t, l], i) => {
    const x = XL + (i % 2) * (WC + GX), y = 1.32 + Math.floor(i / 2) * 2.84;
    const im = captura(s, img, x, y, WC, 2.06, t);
    rotulo(s, x, im.y + im.h + 0.12, WC, i + 1, t, l);
  });
  const DER = [
    ['antes_chart', 'Antes del pleno', 'Acuerdos de cada pleno y días hasta AME'],
    ['eco', 'Gestión económica', 'Nómina, atrasos, pagado de más y reintegros'],
    ['curso', 'Procedimientos en curso', 'Uno a uno: quién lo tiene y su impacto'],
  ];
  let y = 1.32;
  DER.forEach(([img, t, l], i) => {
    const im = captura(s, img, XR, y, WR, 2, t);
    rotulo(s, XR, im.y + im.h + 0.12, WR, i + 5, t, l);
    y = im.y + im.h + 0.12 + 0.5 + 0.2;
  });
}

pres.writeFile({ fileName: OUT }).then(f => console.log('escrito', f));
