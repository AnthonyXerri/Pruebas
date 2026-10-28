// Dos diapositivas que enseñan el mockup de reintegros (prescripción por mensualidad) del caso de acogimiento,
// con capturas y muy poco texto. Mismo estilo que las del mockup de seguimiento del proceso.
// Uso: node build_mockup_reintegros.js <carpeta de capturas> <salida.pptx>
const path = require('path');
const pptxgen = require('pptxgenjs');

const IMG = process.argv[2] || path.join(__dirname, 'img_reintegros');
const OUT = process.argv[3] || 'Mockup_Reintegros.pptx';
const TAM = require(path.join(IMG, 'sizes.json'));
const C = { rosa: 'F4A7AF', rojo: 'C0172E', negro: '1A1A1A', gris: '595959', grisClaro: '8C8C8C', blanco: 'FFFFFF',
  marco: 'DADCE3', granate: '5A1A22', navy: '0A1F44', teal: '005B60', fondo: 'F7F8FA' };
const F = 'Calibri', FT = 'Century Gothic', FM = 'Courier New';
const CSS = TAM.top[0] / 2, X0 = 28, Y0 = 6;             // la captura de arriba empieza en (28, 6) de la página, a 2x

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';
pres.title = 'Mockup · Reintegros y prescripción · Acogimiento familiar';

function diapositiva(subtitulo) {
  const s = pres.addSlide();
  s.background = { color: C.blanco };
  s.addShape(pres.ShapeType.roundRect, { x: 0.38, y: 0.3, w: 12.55, h: 0.95, rectRadius: 0.2, fill: { color: C.rosa }, line: { type: 'none' }, objectName: 'Banda del título' });
  s.addText([
    { text: '4. Mockup · Reintegros y prescripción', options: { fontFace: FT, bold: true, fontSize: 24, color: C.negro } },
    { text: '   ' + subtitulo, options: { fontFace: FT, fontSize: 15, color: C.granate } },
  ], { x: 0.78, y: 0.38, w: 11.8, h: 0.55, valign: 'middle', margin: 0, isTextBox: true, objectName: 'Título' });
  s.addShape(pres.ShapeType.roundRect, { x: 0.33, y: 0.98, w: 12.7, h: 6.35, rectRadius: 0.15, fill: { color: C.blanco }, line: { color: 'E3E3E3', width: 1 },
    shadow: { type: 'outer', blur: 6, offset: 2, angle: 90, color: '000000', opacity: 0.14 }, objectName: 'Tarjeta' });
  s.addText('Maqueta con datos ficticios · Fuente: AME', { x: 7.2, y: 7.06, w: 5.6, h: 0.18, fontFace: F, fontSize: 7.5,
    italic: true, color: C.grisClaro, align: 'right', margin: 0, isTextBox: true });
  return s;
}
// captura con marco y sombra, ajustada sin deformar dentro de w × h (centrada en horizontal)
function captura(s, nombre, x, y, w, h, alt) {
  const [iw, ih] = TAM[nombre], k = Math.min(w / iw, h / ih), cw = iw * k, ch = ih * k, cx = x + (w - cw) / 2;
  s.addShape(pres.ShapeType.rect, { x: cx - 0.03, y: y - 0.03, w: cw + 0.06, h: ch + 0.06, fill: { color: C.blanco }, line: { color: C.marco, width: 0.75 },
    shadow: { type: 'outer', blur: 5, offset: 1.5, angle: 90, color: '000000', opacity: 0.16 } });
  s.addImage({ path: path.join(IMG, nombre + '.png'), x: cx, y, w: cw, h: ch, altText: alt });
  return { x: cx, y, w: cw, h: ch };
}
function marca(s, cx, cy, n, d = 0.28) {
  s.addShape(pres.ShapeType.ellipse, { x: cx - d / 2, y: cy - d / 2, w: d, h: d, fill: { color: C.rojo }, line: { color: C.blanco, width: 1.25 }, objectName: 'Marca ' + n });
  s.addText(String(n), { x: cx - d / 2, y: cy - d / 2, w: d, h: d, fontFace: F, fontSize: 10.5, bold: true, color: C.blanco, align: 'center', valign: 'middle', margin: 0, isTextBox: true });
}
function rotulo(s, x, y, w, n, tit, linea, h = 0.5) {
  marca(s, x + 0.14, y + 0.13, n);
  s.addText([
    { text: tit, options: { fontFace: F, fontSize: 11, bold: true, color: C.negro, breakLine: true } },
    { text: linea, options: { fontFace: F, fontSize: 8.5, color: C.gris } },
  ], { x: x + 0.36, y, w: w - 0.36, h, valign: 'top', margin: 0, isTextBox: true, paraSpaceAfter: 1 });
}

/* ═══════════ 1 · lo que se pierde cada mes ═══════════ */
{
  const s = diapositiva('Lo que se pierde cada mes');
  const im = captura(s, 'top', 0.75, 1.42, 9.55, 4.75, 'Cabecera del mockup de reintegros: indicadores, filtros, aviso y las dos primeras gráficas');
  const k = im.w / CSS, en = (px, py) => [im.x + (px - X0) * k, im.y + (py - Y0) * k];
  [[32, 49, 1], [32, 178, 2], [32, 277, 3], [32, 343, 4], [751, 343, 5]].forEach(([px, py, n]) => { const [x, y] = en(px, py); marca(s, px === 32 ? im.x - 0.12 : x - 0.04, y + 0.03, n); });
  const L = [
    ['Indicadores', 'Reintegros abiertos, importe recuperable, próximo vencimiento y lo ya perdido'],
    ['Filtros', 'Origen, motivo, estado y urgencia; por semana, mes, trimestre o año'],
    ['Aviso', 'Lo más grave primero: caducados o lo que se pierde en 90 días'],
    ['Lo que prescribe cada mes', 'Cada mensualidad prescribe a los 4 años de su pago'],
    ['Notificar y resolver', 'El ritmo real frente al necesario para que nada caduque'],
  ];
  L.forEach(([t, l], i) => rotulo(s, 10.55, 1.5 + i * 0.95, 2.25, i + 1, t, l, 0.8));
}

/* ═══════════ 2 · prioridad, cola y origen ═══════════ */
{
  const s = diapositiva('Prioridad, cola y origen');
  const XL = 0.65, WL = 5.95, XR = 6.85, WR = 5.9;
  captura(s, 'pri', XL, 1.38, WL, 1.3, 'Prioridad real: expedientes por tiempo hasta perder dinero y estado');
  captura(s, 'origen', XR, 1.38, WR, 1.3, 'Origen del reintegro: importe por motivo y días hasta constar en AME');
  rotulo(s, XL, 2.82, WL, 1, 'Prioridad real', 'Por tiempo hasta perder dinero y estado del procedimiento');
  rotulo(s, XR, 2.82, WR, 2, 'Origen del reintegro', 'Importe por motivo y días hasta que el hecho consta en AME');
  const t = captura(s, 'tabla', XL, 3.55, WL, 2.4, 'La cola de trabajo: expedientes ordenados por la próxima mensualidad que vence');
  rotulo(s, XL, t.y + t.h + 0.13, WL, 3, 'La cola de trabajo', 'Uno a uno, por la próxima mensualidad que vence');

  // reglas de cálculo, en nativo para que se lean
  const RY = 3.55, RH = t.h;
  s.addShape(pres.ShapeType.roundRect, { x: XR, y: RY, w: WR, h: RH, rectRadius: 0.08, fill: { color: C.fondo }, line: { color: C.marco, width: 0.75 }, objectName: 'Reglas de cálculo' });
  s.addText('REGLAS DE CÁLCULO', { x: XR + 0.18, y: RY + 0.12, w: 4, h: 0.18, fontFace: FM, fontSize: 8, bold: true, color: C.navy, margin: 0, isTextBox: true });
  const REG = [['4 años', 'Prescribe cada mensualidad, desde su pago', C.navy], ['Reinicio', 'Notificar el acuerdo de inicio reinicia los 4 años', C.teal],
    ['6 meses', 'Caduca el procedimiento si no se resuelve antes', 'C0172E'], ['+25 %', 'Intereses de demora sobre el interés legal', C.navy]];
  const tw = (WR - 0.5) / 2, th = (RH - 0.55) / 2;
  REG.forEach(([big, txt, col], i) => {
    const x = XR + 0.18 + (i % 2) * (tw + 0.14), y = RY + 0.42 + Math.floor(i / 2) * (th + 0.12);
    s.addShape(pres.ShapeType.roundRect, { x, y, w: tw, h: th, rectRadius: 0.06, fill: { color: C.blanco }, line: { color: 'E4E6EC', width: 0.75 } });
    s.addShape(pres.ShapeType.rect, { x, y: y + 0.12, w: 0.05, h: th - 0.24, fill: { color: col }, line: { type: 'none' } });
    s.addText([{ text: big, options: { fontFace: F, fontSize: 22, color: col, breakLine: true } },
      { text: txt, options: { fontFace: F, fontSize: 9, color: '3A3A3A' } }], { x: x + 0.2, y, w: tw - 0.3, h: th, valign: 'middle', margin: 0, isTextBox: true });
  });
  rotulo(s, XR, t.y + t.h + 0.13, WR, 4, 'Reglas de cálculo', 'A confirmar con el art. 13 del Decreto 44/2022');
}

pres.writeFile({ fileName: OUT }).then(f => console.log('escrito', f));
