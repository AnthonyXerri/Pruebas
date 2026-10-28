// Flujo de punta a punta de la prestación por acogimiento familiar, con la parte de Protección
// resumida (para validarla con su equipo) y la prestación en AME según la sesión del 14/08.
// Uso: node build_flujo_e2e_acogimiento.js <salida.pptx>
const pptxgen = require('pptxgenjs');

const OUT = process.argv[2] || 'FlujoE2E_Acogimiento.pptx';
const C = {
  rosa: 'F4A7AF', rojo: 'C00000', azul: '2C4BD9', azulOsc: '1F2A5C', navy: '0A1F44',
  lila: 'F4F6FE', lilaBorde: 'C9D0F2', prot: 'F3F3F7', protBorde: 'A9AECB', protTxt: '4A5280',
  gpme: '8E91AD', ame: '2C4BD9', nexus: '00737A', naranja: 'D98324', naranjaClaro: 'FFF4E6', naranjaTxt: 'A85F0E',
  morado: '7B3FBF', gris: '595959', grisClaro: '8C8C8C', negro: '1A1A1A', blanco: 'FFFFFF', fondo: 'FAFAFA',
};
const F = 'Calibri', FT = 'Century Gothic', FM = 'Courier New';

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';
pres.title = 'Flujo de punta a punta · Acogimiento familiar';
const s = pres.addSlide();
s.background = { color: C.blanco };
const S = pres.ShapeType;

/* ── utilidades (cada llamada crea sus objetos: pptxgenjs los modifica) ── */
const rect = (x, y, w, h, o = {}) => s.addShape(o.tipo || S.roundRect, {
  x, y, w, h, rectRadius: o.r ?? 0.06,
  fill: o.fill ? { color: o.fill } : { type: 'none' },
  line: o.line ? { color: o.line, width: o.lw ?? 1, dashType: o.dash || 'solid' } : { type: 'none' },
  shadow: o.sombra ? { type: 'outer', blur: 5, offset: 1.5, angle: 90, color: '000000', opacity: 0.13 } : undefined,
  objectName: o.nombre });
const txt = (x, y, w, h, partes, o = {}) => s.addText(
  (Array.isArray(partes) ? partes : [[partes, {}]]).map(([t, p], i, a) => ({
    text: t, options: { fontFace: p.font || F, fontSize: p.size || 8, bold: !!p.bold, italic: !!p.italic,
      color: p.color || C.negro, charSpacing: p.cs, breakLine: i < a.length - 1 } })),
  { x, y, w, h, isTextBox: true, margin: o.m ?? 0, align: o.align || 'center', valign: o.valign || 'middle', objectName: o.nombre });
const linea = (x1, y1, x2, y2, o = {}) => s.addShape(S.line, {
  x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1), flipH: x2 < x1, flipV: y2 < y1,
  line: { color: o.color || C.azul, width: o.w ?? 1.25, dashType: o.dash || 'solid', endArrowType: o.flecha ? 'triangle' : undefined } });
const caja = (x, y, w, h, tit, sub, o = {}) => {
  rect(x, y, w, h, { fill: o.fill || C.blanco, line: o.line || C.azul, lw: o.lw ?? 1.25, dash: o.dash, r: o.r ?? 0.06, sombra: o.sombra, nombre: tit });
  txt(x + 0.06, y, w - 0.12, h, [[tit, { bold: true, size: o.ts || 9, color: o.tc || C.negro }], ...(sub ? [[sub, { size: o.ss || 7, color: o.sc || C.gris }]] : [])]);
};
const etiqueta = (x, y, w, t, color, o = {}) => txt(x, y, w, 0.16, [[t, { font: FM, bold: true, size: o.size || 7.5, color, cs: 0.5 }]], { align: o.align || 'left' });

/* ── marco, como el resto del deck ── */
rect(0.38, 0.3, 12.55, 0.95, { fill: C.rosa, r: 0.2, nombre: 'Banda del título' });
s.addText([
  { text: '2. Flujo de proceso de punta a punta', options: { fontFace: FT, bold: true, fontSize: 24, color: C.negro } },
  { text: '   Protección (resumida) y prestación', options: { fontFace: FT, fontSize: 15, color: '5A1A22' } },
], { x: 0.78, y: 0.38, w: 11.8, h: 0.55, valign: 'middle', margin: 0, isTextBox: true, objectName: 'Título' });
rect(0.33, 0.98, 12.7, 6.35, { fill: C.blanco, line: 'E3E3E3', r: 0.15, sombra: true, nombre: 'Tarjeta' });

/* ════════════ PROTECCIÓN · columna izquierda, resumida y a validar ════════════ */
const PX = 0.8, PW = 2.3, PC = PX + PW / 2;
rect(0.6, 1.3, 2.8, 5.55, { fill: C.prot, line: C.protBorde, lw: 1, dash: 'dash', r: 0.1, nombre: 'Protección' });
etiqueta(0.75, 1.38, 2.6, 'PROTECCIÓN · GPME', C.protTxt, { size: 8.5 });
txt(0.75, 1.56, 2.6, 0.16, [['resumido · a validar con su equipo', { italic: true, size: 7.5, color: C.grisClaro }]], { align: 'left' });
const prot = { fill: C.blanco, line: C.gpme, lw: 1, dash: 'dash', tc: C.protTxt };
caja(PX, 1.86, PW, 0.5, 'Medida de protección', 'tutela o guarda del menor', prot);
linea(PC, 2.36, PC, 2.6, { color: C.gpme, w: 1, flecha: true });
caja(PX, 2.6, PW, 0.5, 'Valoración y búsqueda de familia', 'familia extensa o ajena', prot);
linea(PC, 3.1, PC, 3.34, { color: C.gpme, w: 1, flecha: true });
caja(PX, 3.34, PW, 0.5, 'Propuesta a la Comisión de Tutela', 'propuesta técnica', prot);
linea(PC, 3.84, PC, 4.3, { color: C.gpme, w: 1, flecha: true });
caja(PX, 4.3, PW, 0.6, 'Pleno de la Comisión de Tutela', 'miércoles · acuerdo con fecha de efectos', { fill: C.navy, line: C.navy, tc: C.blanco, sc: 'C9D0F2', sombra: true });
caja(PX, 5.0, PW, 0.34, 'o programa de urgencia firmado', null, { ...prot, ts: 8 });
linea(PC, 5.34, PC, 5.76, { color: C.gpme, w: 1, dash: 'sysDot' });
txt(PC + 0.08, 5.42, 1.1, 0.2, [['durante el acogimiento', { italic: true, size: 7, color: C.grisClaro }]], { align: 'left' });
caja(PX, 5.76, PW, 0.58, 'Pleno: cese o cambio de menores', 'fin del acogimiento, o entra o sale un menor', { fill: C.blanco, line: C.navy, lw: 1.5, tc: C.navy });

/* ════════════ el puente: grabación en AME (tiempo perdido) ════════════ */
const HX = 3.62, HW = 1.22;
rect(4.2, 3.92, 8.55, 2.93, { fill: C.lila, line: C.lilaBorde, lw: 1, r: 0.1, nombre: 'Infancia' });
etiqueta(5.05, 3.99, 2.6, 'INFANCIA · AME', C.azul, { size: 8.5 });
txt(6.55, 3.99, 4.5, 0.16, [['con gestión económica (Nexus) e Intervención', { italic: true, size: 7.5, color: C.grisClaro }]], { align: 'left' });
const puente = (y, h, sub) => {
  caja(HX, y, HW, h, 'Grabación en AME', sub, { fill: C.naranjaClaro, line: C.naranja, lw: 1.5, ts: 8.5, ss: 6.5, sc: C.naranjaTxt });
  txt(HX - 0.1, y - 0.19, HW + 0.2, 0.16, [['TIEMPO PERDIDO', { font: FM, bold: true, size: 7, color: C.naranja }]]);
};
puente(4.3, 0.62, 'Protección · aviso por correo');
linea(PX + PW, 4.48, HX, 4.48, { color: C.naranja, w: 1.5, flecha: true });
linea(PX + PW, 5.17, 3.36, 5.17, { color: C.gpme, w: 1 }); linea(3.36, 5.17, 3.36, 4.78, { color: C.gpme, w: 1 }); linea(3.36, 4.78, HX, 4.78, { color: C.gpme, w: 1, flecha: true });
puente(5.74, 0.62, 'mismo aviso por correo');
linea(PX + PW, 6.05, HX, 6.05, { color: C.naranja, w: 1.5, flecha: true });

/* ════════════ INFANCIA · la prestación ════════════ */
// fila 1: reconocimiento y prestación activa
const RX = 5.05, RY = 4.22, RW = 5.1, RH = 0.92;
rect(RX, RY, RW, RH, { fill: C.blanco, line: '3F4FB8', lw: 1.25, r: 0.06, nombre: 'Reconocimiento' });
txt(RX + 0.1, RY + 0.04, 3, 0.2, [['Reconocimiento de la prestación', { bold: true, size: 9 }]], { align: 'left' });
const PASOS = ['Acuerdo de inicio', '10 días de alegaciones', 'Borrador de resolución', 'Terceros (Nexus)', 'Doc. contable y propuesta mensual', 'Fiscalización', 'Resolución'];
const pw = 0.65, pg = 0.0617, px0 = RX + 0.1;
PASOS.forEach((p, i) => {
  const x = px0 + i * (pw + pg);
  rect(x, RY + 0.32, pw, 0.48, { fill: 'F7F8FE', line: 'D5DAF3', lw: 0.75, r: 0.05 });
  txt(x + 0.03, RY + 0.32, pw - 0.06, 0.48, [[p, { size: 6.5, color: '2B2B4A', bold: i === PASOS.length - 1 }]]);
  if (i < PASOS.length - 1) linea(x + pw, RY + 0.56, x + pw + pg, RY + 0.56, { w: 0.75, flecha: true });
});
txt(RX, RY + RH + 0.03, 3.6, 0.16, [['Requisito: la cuenta corriente, antes de cargar terceros (día 3)', { italic: true, size: 7, color: C.naranjaTxt }]], { align: 'left' });
linea(HX + HW, 4.61, RX, 4.61, { flecha: true });
const AX = 10.35, AW = 2.25;
caja(AX, 4.24, AW, 0.88, 'Prestación activa', 'primer pago con atrasos y nómina mensual', { fill: C.azul, line: C.azul, tc: C.blanco, sc: 'DDE3FF', ts: 11, ss: 7.5, sombra: true });
linea(RX + RW, 4.68, AX, 4.68, { flecha: true });

// fila 2: modificación o extinción, indebido y reintegro
const MX = 5.05, MW = 2.3, Y2 = 5.74, H2 = 0.62;
linea(HX + HW, 6.05, MX, 6.05, { flecha: true });
caja(MX, Y2, MW, H2, 'Modificación o extinción', 'entra o sale un menor, discapacidad · cese, 18 años', { lw: 1.5 });
// los hechos de la propia prestación (mayoría de edad, discapacidad) también llegan aquí
linea(AX + AW / 2, 5.12, AX + AW / 2, 5.5, { w: 1 }); linea(AX + AW / 2, 5.5, MX + MW / 2, 5.5, { w: 1 }); linea(MX + MW / 2, 5.5, MX + MW / 2, Y2, { w: 1, flecha: true });
txt(8.0, 5.33, 3.0, 0.15, [['mayoría de edad o discapacidad', { italic: true, size: 7, color: C.gris }]]);
const DX = 7.6, DW = 1.6;
linea(MX + MW, 6.05, DX, 6.05, { flecha: true });
s.addShape(S.diamond, { x: DX, y: Y2 - 0.02, w: DW, h: H2 + 0.04, fill: { color: C.blanco }, line: { color: C.morado, width: 1.5 }, objectName: '¿Pago indebido?' });
txt(DX, Y2, DW, H2, [['¿Pago indebido?', { bold: true, size: 8 }]]);
txt(DX - 0.2, Y2 + H2 + 0.08, DW + 0.4, 0.15, [['No: sigue cobrando o termina', { size: 6.5, italic: true, color: C.gris }]]);
const EX = 9.5, EW = 1.75;
linea(DX + DW, 6.05, EX, 6.05, { flecha: true, w: 1.25 });
txt(DX + DW + 0.02, 5.88, 0.25, 0.13, [['Sí', { size: 6.5, color: C.gris }]], { align: 'left' });
caja(EX, Y2, EW, H2, 'Reintegro', '~2 meses después: notificación y recurso', { line: C.morado, lw: 1.5 });
linea(EX + EW, 6.05, 11.45, 6.05, { flecha: true });
rect(11.45, 5.93, 0.55, 0.24, { fill: C.blanco, line: C.azul, lw: 1.25, r: 0.12 });
txt(11.45, 5.93, 0.55, 0.24, [['FIN', { bold: true, size: 8, color: C.azulOsc }]]);

/* ════════════ arriba a la derecha: fechas que mediremos y preguntas ════════════ */
rect(3.62, 1.3, 9.13, 1.3, { fill: C.blanco, line: 'DADCE3', lw: 0.75, r: 0.08, nombre: 'Fechas' });
etiqueta(3.8, 1.37, 6, 'FECHAS QUE MEDIREMOS · DE LA PROPUESTA AL PAGO', C.navy);
const HITOS = [['Propuesta a la Comisión', 'GPME', C.gpme], ['Pleno · fecha de efectos', 'GPME', C.gpme], ['Grabación en AME', 'AME', C.ame],
  ['Acuerdo de inicio', 'AME', C.ame], ['Propuesta mensual', 'AME', C.ame], ['Fiscalización', 'AME', C.ame], ['Resolución', 'AME', C.ame], ['Pago', 'Nexus', C.nexus]];
const TX0 = 4.35, TDX = 1.13, TY = 1.98;
const tx = i => TX0 + i * TDX;
linea(tx(0), TY, tx(1), TY, { color: C.gpme, w: 2.5 });
linea(tx(1), TY, tx(2), TY, { color: C.naranja, w: 3.5 });
linea(tx(2), TY, tx(7), TY, { color: C.ame, w: 2.5 });
txt(tx(0), TY - 0.24, TDX, 0.15, [['Protección', { size: 7, bold: true, color: C.gpme }]]);
txt(tx(1), TY - 0.24, TDX, 0.15, [['tiempo perdido', { size: 7, bold: true, color: C.naranja }]]);
txt(tx(2), TY - 0.24, tx(7) - tx(2), 0.15, [['Infancia · tramitación de la prestación hasta la nómina', { size: 7, bold: true, color: C.ame }]]);
HITOS.forEach(([n, src, col], i) => {
  const d = i === 1 ? 0.2 : 0.15;
  s.addShape(S.ellipse, { x: tx(i) - d / 2, y: TY - d / 2, w: d, h: d, fill: { color: i === 1 ? C.navy : C.blanco }, line: { color: col, width: 1.75 } });
  txt(tx(i) - 0.55, TY + 0.13, 1.1, 0.4, [[n, { size: 7, bold: i === 1, color: C.negro }], [src, { size: 6.5, bold: true, color: col }]], { valign: 'top' });
});

rect(3.62, 2.72, 9.13, 0.9, { fill: 'FFF7F7', line: 'F0C5CA', lw: 0.75, r: 0.08, nombre: 'A validar' });
etiqueta(3.8, 2.79, 6, 'A VALIDAR CON PROTECCIÓN', C.rojo);
const PREG = ['Qué etapas y fechas registra GPME: propuesta, pleno, firma y grabación en AME',
  'Si el programa de urgencia pasa por el pleno o solo se firma',
  'Cómo y cuándo se comunica a Infancia un cese o un cambio de menores'];
PREG.forEach((q, i) => {
  const x = 3.8 + i * 2.98;
  s.addShape(S.ellipse, { x, y: 3.1, w: 0.3, h: 0.3, fill: { color: C.rojo }, line: { type: 'none' } });
  txt(x, 3.1, 0.3, 0.3, [['?', { bold: true, size: 11, color: C.blanco }]]);
  txt(x + 0.4, 3.04, 2.45, 0.44, [[q, { size: 8, color: '333333' }]], { align: 'left' });
});

/* ── pie ── */
txt(6.2, 7.06, 6.6, 0.16, [['Protección: resumen para validar · Prestación: revisada con el servicio (14/08) · Decreto 44/2022', { italic: true, size: 7, color: C.grisClaro }]], { align: 'right' });

pres.writeFile({ fileName: OUT }).then(f => console.log('escrito', f));
