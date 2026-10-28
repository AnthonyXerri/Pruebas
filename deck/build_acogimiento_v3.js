// Diapositiva «Flujo de proceso y Pain Points» de la prestación por acogimiento familiar, versión resumida.
// El pleno de la Comisión de Tutela no forma parte de prestaciones: va fuera del proceso, como la entrada que lo dispara.
// Uso: node build_acogimiento_v3.js <salida.pptx>
const pptxgen = require('pptxgenjs');

const OUT = process.argv[2] || 'FlujoPainPoints_Acogimiento_v3.pptx';
const C = {
  rosa: 'F4A7AF', rosaBorde: 'F0C5CA', rojo: 'C00000', rojoOsc: '8B0000',
  azul: '2C4BD9', azulOsc: '1F2A5C', lila: 'EEF1FC', lilaBorde: 'C9D0F2', navy: '0A1F44',
  morado: '6C3FD1', fucsia: 'E2336B', naranja: 'E39B2F', naranjaTxt: 'B86A00',
  gris: '595959', grisClaro: '8C8C8C', gBadge: 'D4D4D4', gBadgeBorde: 'A6A6A6',
  negro: '1A1A1A', blanco: 'FFFFFF', fondo: 'FAFAFA', linea: 'BDBDBD', sep: 'E4E4E4',
};
const F = 'Calibri', FT = 'Century Gothic', FM = 'Courier New';

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';
pres.title = 'Flujo de proceso y Pain Points · Acogimiento familiar';
const s = pres.addSlide();
s.background = { color: C.blanco };
const S = pres.ShapeType;

/* ── utilidades: cada llamada crea sus propios objetos (pptxgenjs los modifica) ── */
const rect = (x, y, w, h, o = {}) => s.addShape(o.tipo || S.roundRect, {
  x, y, w, h, rectRadius: o.r ?? 0.08,
  fill: o.fill ? { color: o.fill } : { type: 'none' },
  line: o.line ? { color: o.line, width: o.lw ?? 1, dashType: o.dash || 'solid' } : { type: 'none' },
  shadow: o.sombra ? { type: 'outer', blur: 6, offset: 2, angle: 90, color: '000000', opacity: 0.14 } : undefined,
  objectName: o.nombre });
const txt = (x, y, w, h, partes, o = {}) => s.addText(
  (Array.isArray(partes) ? partes : [[partes, {}]]).map(([t, p], i, a) => ({
    text: t, options: { fontFace: p.font || F, fontSize: p.size || 8, bold: !!p.bold, italic: !!p.italic,
      color: p.color || C.negro, charSpacing: p.cs, breakLine: i < a.length - 1 } })),
  { x, y, w, h, isTextBox: true, margin: 0, align: o.align || 'left', valign: o.valign || 'top', objectName: o.nombre });
const linea = (x1, y1, x2, y2, o = {}) => s.addShape(S.line, {
  x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1), flipH: x2 < x1, flipV: y2 < y1,
  line: { color: o.color || C.azul, width: o.w ?? 1.25, dashType: o.dash || 'solid', endArrowType: o.flecha ? 'triangle' : undefined } });
const badge = (cx, cy, n, d = 0.28) => {
  s.addShape(S.ellipse, { x: cx - d / 2, y: cy - d / 2, w: d, h: d, fill: { color: C.gBadge }, line: { color: C.gBadgeBorde, width: 1 }, objectName: 'Marca ' + n });
  txt(cx - d / 2, cy - d / 2, d, d, [[String(n), { bold: true, size: 10, color: C.blanco }]], { align: 'center', valign: 'middle' });
};
const centrado = { align: 'center', valign: 'middle' };

/* ── marco de la diapositiva ── */
rect(0.38, 0.3, 12.55, 0.95, { fill: C.rosa, r: 0.2, nombre: 'Banda del título' });
txt(0.78, 0.38, 11.8, 0.55, [['2. Flujo de proceso y Pain Points (puntos de dolor)', { font: FT, bold: true, size: 25 }]], { valign: 'middle', nombre: 'Título' });
rect(0.33, 0.98, 12.7, 6.35, { fill: C.blanco, line: 'E3E3E3', r: 0.15, sombra: true, nombre: 'Tarjeta' });
rect(0.72, 1.18, 11.95, 6.0, { fill: C.fondo, line: C.rosaBorde, lw: 0.75, r: 0.45, nombre: 'Panel' });

/* ════════════════ IZQUIERDA · el proceso, resumido ════════════════ */
const X1 = 1.12, W1 = 2.75, CX = X1 + W1 / 2, X2 = 4.1, W2 = 2.65;
rect(1.0, 2.55, 5.9, 4.5, { fill: C.lila, line: C.lilaBorde, r: 0.12, nombre: 'Panel del proceso' });
rect(3.05, 2.37, 3.7, 0.36, { fill: C.azul, r: 0.18, nombre: 'Etiqueta del proceso' });
txt(3.05, 2.37, 3.7, 0.36, [['PRESTACIÓN ECONÓMICA · PROCESO', { font: FM, bold: true, size: 11.5, color: C.blanco, cs: 1 }]], centrado);
badge(6.75, 2.55, 5);

// el pleno no es de prestaciones: queda fuera del proceso y solo aporta la fecha de efectos
rect(X1, 1.35, W1, 0.58, { fill: 'F3F3F7', line: '8E91AD', lw: 1.25, dash: 'dash', r: 0.2, nombre: 'Pleno (fuera de prestaciones)' });
txt(X1, 1.35, W1, 0.58, [['Pleno de la Comisión de Tutela', { bold: true, size: 10.5, color: '4A5280' }], ['formaliza el acogimiento · los miércoles', { size: 7.5, color: C.gris }]], centrado);
txt(X2, 1.42, W2 + 0.1, 0.5, [['FUERA DE PRESTACIONES', { font: FM, bold: true, size: 7.5, color: '6B74A8' }],
  ['Infancia · Comisión de Tutela (GPME). Lo que se acuerda llega a AME por correo.', { italic: true, size: 7.5, color: C.gris }]]);
linea(CX, 1.93, CX, 2.92, { flecha: true });
badge(CX, 2.24, 1);
txt(CX + 0.22, 2.16, 1.9, 0.16, [['grabación en AME y aviso por correo', { italic: true, size: 7.5, color: C.gris }]]);

// reconocimiento en AME, en cinco pasos
const YA = 2.92, HA = 1.6;
rect(X1, YA, W1, HA, { fill: C.blanco, line: '3F4FB8', lw: 1.25, r: 0.06, nombre: 'Reconocimiento en AME' });
txt(X1, YA + 0.07, W1, 0.22, [['Reconocimiento en AME', { bold: true, size: 10 }]], { align: 'center' });
const PASOS = ['Acuerdo de inicio', '10 días de alegaciones', 'Propuesta mensual (terceros y D)', 'Fiscalización y resolución', 'Pago en la nómina'];
const yP = i => YA + 0.38 + i * 0.235;
PASOS.forEach((p, i) => {
  const y = yP(i), ult = i === PASOS.length - 1;
  s.addShape(S.ellipse, { x: X1 + 0.14, y: y + 0.015, w: 0.17, h: 0.17, fill: { color: ult ? C.morado : C.blanco }, line: { color: C.morado, width: 1 } });
  txt(X1 + 0.14, y + 0.015, 0.17, 0.17, [[String(i + 1), { size: 7, bold: true, color: ult ? C.blanco : C.morado }]], centrado);
  rect(X1 + 0.4, y, W1 - 0.52, 0.2, { fill: ult ? 'E6E1FA' : 'F7F8FE', line: 'E1E4F5', lw: 0.5, r: 0.05 });
  txt(X1 + 0.48, y, W1 - 0.6, 0.2, [[p, { size: 8, bold: ult, color: '2B2B4A' }]], { valign: 'middle' });
});

// requisito bloqueante
rect(X2, 3.0, W2, 0.62, { fill: C.blanco, line: C.naranja, lw: 1.25, r: 0.08, nombre: 'Requisito bloqueante' });
txt(X2 + 0.14, 3.06, W2 - 0.24, 0.52, [['REQUISITO BLOQUEANTE', { font: FM, bold: true, size: 7, color: C.naranjaTxt }],
  ['Cuenta corriente del beneficiario', { bold: true, size: 9.5 }], ['Si no llega a tiempo, cobra un mes después', { size: 7.5, color: '404040' }]]);
linea(X1 + W1, yP(0) + 0.1, X2, yP(0) + 0.1, { color: C.naranja, w: 1, dash: 'dash' });
badge(X2, 3.0, 2);

// prestación activa y cambios durante la vigencia
linea(CX, YA + HA, CX, 4.76, { flecha: true });
rect(X1, 4.76, W1, 0.55, { fill: C.azul, r: 0.08, sombra: true, nombre: 'Prestación activa' });
txt(X1, 4.76, W1, 0.55, [['Prestación activa', { bold: true, size: 12, color: C.blanco }], ['pago mensual por menor acogido', { size: 7.5, color: 'DDE3FF' }]], centrado);
badge(CX - 0.32, 4.64, 3);
const item = (y, t) => { rect(X2, y, W2, 0.25, { fill: C.blanco, line: C.lilaBorde, lw: 0.75, r: 0.05 });
  txt(X2, y, W2, 0.25, [[t, { size: 8, bold: true, color: '2B2B6B' }]], centrado); };
const XB = X2 - 0.09;
txt(X2, 4.0, W2, 0.16, [['DURANTE LA VIGENCIA · cambio de importe', { font: FM, bold: true, size: 7.5, color: C.azul }]]);
item(4.24, 'Entra o sale un menor (acuerdo del pleno)');
item(4.55, 'Discapacidad del menor');
linea(XB, 4.365, XB, 5.035, { w: 1 });
[4.365, 4.675].forEach(y => linea(XB, y, X2, y, { w: 1 }));
linea(X1 + W1, 5.035, XB, 5.035, { w: 1 });

// extinción
linea(CX, 5.31, CX, 5.5, { flecha: true });
rect(X1, 5.5, W1, 0.4, { fill: C.blanco, line: C.azul, lw: 1.75, r: 0.06, nombre: 'Evento de extinción' });
txt(X1, 5.5, W1, 0.4, [['Evento de extinción', { bold: true, size: 11, color: C.azulOsc }]], centrado);
txt(X2, 5.18, W2, 0.16, [['CAUSAS DE EXTINCIÓN', { font: FM, bold: true, size: 7.5, color: C.azul }]]);
item(5.42, 'Cese del acogimiento (acuerdo del pleno)');
item(5.73, 'Mayoría de edad (18 años)');
linea(XB, 5.545, XB, 5.855, { w: 1 });
[5.545, 5.855].forEach(y => linea(XB, y, X2, y, { w: 1 }));
linea(X1 + W1, 5.7, XB, 5.7, { w: 1 });

// ¿pago indebido?
linea(CX, 5.9, CX, 6.06, { flecha: true });
const DW = 1.6, DH = 0.56, DY = 6.06;
s.addShape(S.diamond, { x: CX - DW / 2, y: DY, w: DW, h: DH, fill: { color: C.blanco }, line: { color: C.morado, width: 1.5 }, objectName: '¿Pago indebido?' });
txt(CX - DW / 2, DY, DW, DH, [['¿Pago indebido?', { bold: true, size: 8.5 }]], centrado);
linea(CX - DW / 2, DY + DH / 2, X1 + 0.5, DY + DH / 2, { flecha: true });
txt(X1 + 0.52, DY + DH / 2 - 0.16, 0.3, 0.13, [['No', { size: 7, color: C.gris }]]);
rect(X1 - 0.02, DY + DH / 2 - 0.12, 0.52, 0.24, { fill: C.blanco, line: C.azul, lw: 1.25, r: 0.12 });
txt(X1 - 0.02, DY + DH / 2 - 0.12, 0.52, 0.24, [['FIN', { bold: true, size: 8, color: C.azulOsc }]], centrado);
const RY = DY + DH / 2 - 0.22, RW = 1.9;
linea(CX + DW / 2, DY + DH / 2, X2, DY + DH / 2, { flecha: true });
txt(CX + DW / 2 + 0.05, DY + DH / 2 - 0.16, 0.3, 0.13, [['Sí', { size: 7, color: C.gris }]]);
rect(X2, RY, RW, 0.44, { fill: C.blanco, line: '7B3FBF', lw: 1.5, r: 0.06, nombre: 'Reintegro' });
txt(X2, RY, RW, 0.44, [['Reintegro', { bold: true, size: 9.5 }], ['empieza ~2 meses después', { size: 7, color: C.gris }]], centrado);
badge(X2, RY, 4);
linea(X2 + RW, DY + DH / 2, X2 + RW + 0.17, DY + DH / 2, { flecha: true });
rect(X2 + RW + 0.18, DY + DH / 2 - 0.12, 0.52, 0.24, { fill: C.blanco, line: C.azul, lw: 1.25, r: 0.12 });
txt(X2 + RW + 0.18, DY + DH / 2 - 0.12, 0.52, 0.24, [['FIN', { bold: true, size: 8, color: C.azulOsc }]], centrado);

/* ── flechas del centro ── */
['F2B3BA', 'E07A88', 'C0172E'].forEach((c, i) => s.addShape(S.chevron, { x: 7.0 + i * 0.29, y: 3.62, w: 0.42, h: 1.0, fill: { color: c }, line: { type: 'none' } }));

/* ════════════════ DERECHA · pain points, en una o dos líneas ════════════════ */
rect(8.0, 1.62, 4.55, 5.33, { fill: C.blanco, line: C.linea, lw: 1, r: 0.55, nombre: 'Panel de pain points' });
rect(8.92, 1.38, 2.75, 0.46, { fill: C.rojo, line: C.rojoOsc, lw: 1, r: 0.05, nombre: 'Cabecera de pain points' });
txt(8.92, 1.38, 2.75, 0.46, [['Pain Points priorizados', { bold: true, size: 15, color: C.blanco }]], centrado);
const PP = [
  ['Pleno → alta en AME', 'El acuerdo llega a AME por correo y a mano; a veces tarda meses y se acumulan atrasos.'],
  ['Reconocimiento → primer pago', 'Hay que llegar a la propuesta mensual con alegaciones y cuenta; si no, cobra un mes después.'],
  ['Cambios de importe', 'Cada cambio es un procedimiento completo y un DECOM manual en gestión económica.'],
  ['Cese → pago indebido → reintegro', 'Si el cese llega tarde a AME se paga de más; el reintegro empieza ~2 meses después.'],
  ['Transversal · integración', 'Pleno (GPME) y prestación (AME + Nexus) sin conexión ni trazabilidad conjunta.'],
];
const PY0 = 2.08, PH = 0.95;
PP.forEach(([t, b], i) => {
  const y = PY0 + i * PH;
  badge(8.42, y + 0.33, i + 1, 0.36);
  txt(8.75, y + 0.04, 3.6, 0.24, [[t, { bold: true, size: 11.5 }]], { nombre: 'Pain point ' + (i + 1) });
  txt(8.75, y + 0.3, 3.55, 0.45, [[b, { size: 9, color: '3A3A3A' }]]);
  if (i < PP.length - 1) linea(8.75, y + PH - 0.08, 12.2, y + PH - 0.08, { color: C.sep, w: 0.75 });
});

txt(8.0, 7.0, 4.6, 0.14, [['Revisado con el servicio (sesión del 14/08) · Decreto 44/2022', { size: 6.5, italic: true, color: C.grisClaro }]], { align: 'right' });
txt(12.75, 7.08, 0.4, 0.2, [['3', { size: 10, color: C.negro }]], { align: 'right' });

pres.writeFile({ fileName: OUT }).then(f => console.log('escrito', f));
