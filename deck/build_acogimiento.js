// Diapositiva «Flujo de proceso y Pain Points» de la prestación por acogimiento familiar,
// corregida con lo que contó el servicio en la sesión del 14/08. Formas nativas y editables.
// Uso: node build_acogimiento.js <salida.pptx>
const pptxgen = require('pptxgenjs');

const OUT = process.argv[2] || 'FlujoPainPoints_Acogimiento.pptx';
const C = {
  rosa: 'F4A7AF', rosaBorde: 'F0C5CA', rojo: 'C00000', rojoOsc: '8B0000',
  azul: '2C4BD9', azulOsc: '1F2A5C', lila: 'EEF1FC', lilaBorde: 'C9D0F2', lilaTxt: '6B74A8',
  morado: '6C3FD1', fucsia: 'E2336B', naranja: 'E39B2F', naranjaTxt: 'B86A00',
  gris: '595959', grisClaro: '8C8C8C', gBadge: 'D4D4D4', gBadgeBorde: 'A6A6A6',
  negro: '1A1A1A', blanco: 'FFFFFF', fondo: 'FAFAFA', linea: 'BDBDBD', sep: 'E4E4E4',
};
const F = 'Calibri', FT = 'Century Gothic', FM = 'Courier New';

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';                       // 13,33 × 7,5 in
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
  objectName: o.nombre,
});
const txt = (x, y, w, h, partes, o = {}) => s.addText(
  (Array.isArray(partes) ? partes : [[partes, {}]]).map(([t, p], i, a) => ({
    text: t, options: { fontFace: p.font || F, fontSize: p.size || o.size || 8, bold: !!p.bold, italic: !!p.italic,
      color: p.color || o.color || C.negro, charSpacing: p.cs, breakLine: p.br ?? (i < a.length - 1) } })),
  { x, y, w, h, isTextBox: true, margin: o.m ?? 0, align: o.align || 'left', valign: o.valign || 'top',
    lineSpacingMultiple: o.ls || 1.0, paraSpaceAfter: o.psa || 0, objectName: o.nombre });
const linea = (x1, y1, x2, y2, o = {}) => s.addShape(S.line, {
  x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1),
  flipH: x2 < x1, flipV: y2 < y1,
  line: { color: o.color || C.azul, width: o.w ?? 1.25, dashType: o.dash || 'solid', endArrowType: o.flecha ? 'triangle' : undefined } });
const badge = (cx, cy, n, d = 0.27) => {
  s.addShape(S.ellipse, { x: cx - d / 2, y: cy - d / 2, w: d, h: d, fill: { color: C.gBadge }, line: { color: C.gBadgeBorde, width: 1 }, objectName: 'Marca ' + n });
  txt(cx - d / 2, cy - d / 2, d, d, [[String(n), { bold: true, size: 10, color: C.blanco }]], { align: 'center', valign: 'middle' });
};

/* ── marco de la diapositiva, como el resto del deck ── */
rect(0.38, 0.3, 12.55, 0.95, { fill: C.rosa, r: 0.2, nombre: 'Banda del título' });
txt(0.78, 0.38, 11.8, 0.55, [['2. Flujo de proceso y Pain Points (puntos de dolor)', { font: FT, bold: true, size: 25 }]], { valign: 'middle', nombre: 'Título' });
rect(0.33, 0.98, 12.7, 6.35, { fill: C.blanco, line: 'E3E3E3', r: 0.15, sombra: true, nombre: 'Tarjeta' });
rect(0.72, 1.18, 11.95, 6.0, { fill: C.fondo, line: C.rosaBorde, lw: 0.75, r: 0.45, nombre: 'Panel' });

/* ════════════════ IZQUIERDA · el proceso ════════════════ */
const X1 = 1.12, W1 = 2.75, CX = X1 + W1 / 2, X2 = 4.05, W2 = 2.7;
rect(1.0, 1.55, 5.9, 5.5, { fill: C.lila, line: C.lilaBorde, r: 0.12, nombre: 'Panel del proceso' });
rect(1.15, 1.33, 3.75, 0.36, { fill: C.azul, r: 0.18, nombre: 'Etiqueta del proceso' });
txt(1.15, 1.33, 3.75, 0.36, [['PRESTACIÓN ECONÓMICA · PROCESO', { font: FM, bold: true, size: 11.5, color: C.blanco, cs: 1 }]], { align: 'center', valign: 'middle' });

// formalización (Protección)
rect(X1, 1.84, W1, 0.52, { fill: C.blanco, line: C.fucsia, lw: 1.75, r: 0.2, nombre: 'Formalización' });
txt(X1, 1.84, W1, 0.52, [['Formalización del acogimiento', { bold: true, size: 10 }],
  ['Pleno de la Comisión de Tutela · los miércoles', { size: 7.5, color: C.gris }]], { align: 'center', valign: 'middle' });

// frontera Protección | Infancia
linea(1.08, 2.56, 6.82, 2.56, { color: '9AA3D6', w: 1, dash: 'dash' });
txt(X2, 2.37, 2.4, 0.16, [['PROTECCIÓN · GPME', { font: FM, bold: true, size: 7, color: C.lilaTxt }]]);
txt(X2, 2.61, 2.4, 0.16, [['INFANCIA · AME + NEXUS', { font: FM, bold: true, size: 7, color: C.lilaTxt }]]);
badge(6.6, 2.56, 5);
linea(CX, 2.36, CX, 2.76, { flecha: true });
txt(CX + 0.22, 2.42, 1.3, 0.14, [['aviso por correo', { italic: true, size: 7, color: C.gris }]]);
badge(CX, 2.56, 1);

// reconocimiento en AME, en el orden que dio el servicio
const Y_AME = 2.76, H_AME = 2.04;
rect(X1, Y_AME, W1, H_AME, { fill: C.blanco, line: '3F4FB8', lw: 1.25, r: 0.06, nombre: 'Reconocimiento en AME' });
txt(X1, Y_AME + 0.05, W1, 0.22, [['Reconocimiento de la prestación (AME)', { bold: true, size: 9 }]], { align: 'center' });
const PASOS = ['Alta en AME + acuerdo del pleno (Protección)', 'Acuerdo de inicio (pide la cuenta corriente)', 'Notificación + 10 días de alegaciones',
  'Borrador de resolución', 'Terceros (carga masiva en Nexus)', 'Documento contable (D) en la propuesta', 'Fiscalización (Intervención)',
  'Resolución (firma de la directora)', 'Pago en la nómina'];
const yPaso = i => Y_AME + 0.32 + i * 0.188;
PASOS.forEach((p, i) => {
  const y = yPaso(i), ult = i === PASOS.length - 1;
  s.addShape(S.ellipse, { x: X1 + 0.12, y: y + 0.005, w: 0.15, h: 0.15, fill: { color: ult ? C.morado : C.blanco }, line: { color: C.morado, width: 1 } });
  txt(X1 + 0.12, y + 0.005, 0.15, 0.15, [[String(i + 1), { size: 6.5, bold: true, color: ult ? C.blanco : C.morado }]], { align: 'center', valign: 'middle' });
  rect(X1 + 0.34, y, W1 - 0.46, 0.16, { fill: ult ? 'E6E1FA' : 'F7F8FE', line: 'E1E4F5', lw: 0.5, r: 0.05 });
  txt(X1 + 0.42, y, W1 - 0.55, 0.16, [[p, { size: 7, bold: ult, color: '2B2B4A' }]], { valign: 'middle' });
});

// requisito bloqueante
rect(X2, 2.92, W2, 0.68, { fill: C.blanco, line: C.naranja, lw: 1.25, r: 0.08, nombre: 'Requisito bloqueante' });
txt(X2 + 0.12, 2.98, W2 - 0.22, 0.6, [['REQUISITO BLOQUEANTE', { font: FM, bold: true, size: 7, color: C.naranjaTxt }],
  ['Cuenta corriente del beneficiario', { bold: true, size: 9 }],
  ['Se pide en el acuerdo de inicio. Si no llega antes de cargar terceros (día 3), el alta cobra un mes después.', { size: 7, color: '404040' }]]);
linea(X1 + W1, yPaso(1) + 0.08, X2, yPaso(1) + 0.08, { color: C.naranja, w: 1, dash: 'dash' });
badge(X2 - 0.02, 2.92, 2);

// prestación activa
linea(CX, Y_AME + H_AME, CX, 5.0, { flecha: true });
rect(X1, 5.0, W1, 0.55, { fill: C.azul, r: 0.08, sombra: true, nombre: 'Prestación activa' });
txt(X1, 5.0, W1, 0.55, [['Prestación activa', { bold: true, size: 12, color: C.blanco }],
  ['Pago mensual por menor acogido', { size: 7.5, color: 'DDE3FF' }]], { align: 'center', valign: 'middle' });
badge(CX - 0.32, 4.9, 3);

// durante la vigencia
const item = (y, t, o = {}) => { rect(X2, y, W2, 0.22, { fill: C.blanco, line: C.lilaBorde, lw: 0.75, r: 0.05 });
  txt(X2, y, W2, 0.22, [[t, { size: 7.5, bold: true, color: o.color || '2B2B6B' }]], { align: 'center', valign: 'middle' }); };
txt(X2, 3.84, W2, 0.16, [['DURANTE LA VIGENCIA', { font: FM, bold: true, size: 7.5, color: C.azul }]]);
txt(X2, 4.0, W2, 0.14, [['Cambio de importe · procedimiento completo', { size: 6.5, italic: true, color: C.gris }]]);
item(4.15, 'Entra o sale un menor (acuerdo del pleno)');
item(4.41, 'Discapacidad del menor');
txt(X2, 4.68, W2, 0.14, [['Sin procedimiento', { size: 6.5, italic: true, color: C.gris }]]);
item(4.83, 'Cambio de cuenta bancaria o de domicilio');
item(5.09, 'Importes nuevos por Ley de Presupuestos');
const XB = X2 - 0.09;
linea(XB, 4.26, XB, 5.2, { w: 1 });
[4.26, 4.52, 4.94, 5.2].forEach(y => linea(XB, y, X2, y, { w: 1 }));
linea(X1 + W1, 5.275, XB, 5.275, { w: 1 });

// extinción
linea(CX, 5.55, CX, 5.73, { flecha: true });
rect(X1, 5.73, W1, 0.36, { fill: C.blanco, line: C.azul, lw: 1.75, r: 0.06, nombre: 'Evento de extinción' });
txt(X1, 5.73, W1, 0.36, [['Evento de extinción', { bold: true, size: 11, color: C.azulOsc }]], { align: 'center', valign: 'middle' });
txt(X2, 5.5, W2, 0.16, [['CAUSAS DE EXTINCIÓN', { font: FM, bold: true, size: 7.5, color: C.azul }]]);
item(5.68, 'Cese del acogimiento (acuerdo del pleno)');
item(5.94, 'Mayoría de edad del menor (18 años)');
txt(X2, 6.19, W2, 0.14, [['Renuncia e incumplimiento: en el decreto, sin casos', { size: 6.5, italic: true, color: C.gris }]], { align: 'center' });
linea(XB, 5.79, XB, 6.05, { w: 1 });
[5.79, 6.05].forEach(y => linea(XB, y, X2, y, { w: 1 }));
linea(X1 + W1, 5.91, XB, 5.91, { w: 1 });

// ¿pago indebido?
linea(CX, 6.09, CX, 6.2, { flecha: true });
const DW = 1.55, DH = 0.56, DY = 6.2;
s.addShape(S.diamond, { x: CX - DW / 2, y: DY, w: DW, h: DH, fill: { color: C.blanco }, line: { color: C.morado, width: 1.5 }, objectName: '¿Pago indebido?' });
txt(CX - DW / 2, DY, DW, DH, [['¿Pago indebido?', { bold: true, size: 8 }]], { align: 'center', valign: 'middle' });
// no → fin
linea(CX - DW / 2, DY + DH / 2, X1 + 0.5, DY + DH / 2, { w: 1.25, flecha: true });
txt(X1 + 0.52, DY + DH / 2 - 0.15, 0.3, 0.12, [['No', { size: 6.5, color: C.gris }]]);
rect(X1 - 0.02, DY + DH / 2 - 0.12, 0.52, 0.24, { fill: C.blanco, line: C.azul, lw: 1.25, r: 0.12 });
txt(X1 - 0.02, DY + DH / 2 - 0.12, 0.52, 0.24, [['FIN', { bold: true, size: 8, color: C.azulOsc }]], { align: 'center', valign: 'middle' });
// sí → reintegro → fin
const RY = 6.42, RW = 1.98;
linea(CX + DW / 2, DY + DH / 2, X2, DY + DH / 2, { w: 1.25, flecha: true });
txt(CX + DW / 2 + 0.04, DY + DH / 2 - 0.15, 0.3, 0.12, [['Sí', { size: 6.5, color: C.gris }]]);
rect(X2, RY, RW, 0.46, { fill: C.blanco, line: '7B3FBF', lw: 1.5, r: 0.06, nombre: 'Reintegro' });
txt(X2, RY, RW, 0.46, [['Procedimiento de reintegro', { bold: true, size: 8.5 }],
  ['empieza ~2 meses después del cese', { size: 6.5, color: C.gris }]], { align: 'center', valign: 'middle' });
badge(X2, RY, 4);
linea(X2 + RW, RY + 0.23, X2 + RW + 0.16, RY + 0.23, { w: 1.25, flecha: true });
rect(X2 + RW + 0.17, RY + 0.11, 0.52, 0.24, { fill: C.blanco, line: C.azul, lw: 1.25, r: 0.12 });
txt(X2 + RW + 0.17, RY + 0.11, 0.52, 0.24, [['FIN', { bold: true, size: 8, color: C.azulOsc }]], { align: 'center', valign: 'middle' });

/* ── flechas del centro ── */
['F2B3BA', 'E07A88', 'C0172E'].forEach((c, i) => s.addShape(S.chevron, { x: 7.0 + i * 0.29, y: 3.62, w: 0.42, h: 1.0, fill: { color: c }, line: { type: 'none' } }));

/* ════════════════ DERECHA · pain points ════════════════ */
rect(8.0, 1.62, 4.55, 5.33, { fill: C.blanco, line: C.linea, lw: 1, r: 0.55, nombre: 'Panel de pain points' });
rect(8.92, 1.38, 2.75, 0.46, { fill: C.rojo, line: C.rojoOsc, lw: 1, r: 0.05, nombre: 'Cabecera de pain points' });
txt(8.92, 1.38, 2.75, 0.46, [['Pain Points priorizados', { bold: true, size: 15, color: C.blanco }]], { align: 'center', valign: 'middle' });
const PP = [
  ['Formalización → alta en AME',
   'El pleno acuerda los miércoles; Protección graba el alta en AME y avisa por correo. Ha pasado de ~2 meses a ~1 semana, pero hay casos de meses que Infancia descubre cuando escribe la familia, porque no ve los plenos. Ese tiempo son atrasos.'],
  ['Reconocimiento → primer pago',
   'Para cobrar en un mes, el alta tiene que entrar en la propuesta (cierra los días 3–5) con el acuerdo notificado, los 10 días de alegaciones y la cuenta corriente. Si la cuenta llega tarde, cobra un mes después. Las resoluciones se hacen copiando y pegando.'],
  ['Prestación activa · cambios de importe',
   'Si entra o sale un menor o aparece una discapacidad, hay que abrir un procedimiento completo y gestión económica hace el DECOM a mano. La discapacidad no llega por un canal fijo. AME prorratea solo, pero falla en expedientes complejos y se recalcula para comprobar.'],
  ['Cese → pago indebido → reintegro',
   'Es el espejo del alta: si el cese tarda en llegar a AME, se siguen pagando nóminas desde la fecha de efectos. El reintegro no empieza hasta ~2 meses después (notificación y plazo de recurso) y las familias alegan el tiempo pasado para anularlo.'],
  ['Transversal · integración',
   'Dos subdirecciones y dos resoluciones: Protección (pleno, GPME) e Infancia (AME + Nexus), unidas por correo. Dentro de AME todo está conectado; lo que falta es el puente GPME → AME para medir del pleno al pago.'],
];
const PY0 = 2.0, PH = 0.97;
PP.forEach(([t, b], i) => {
  const y = PY0 + i * PH;
  badge(8.42, y + 0.42, i + 1, 0.36);
  txt(8.75, y + 0.02, 3.6, 0.22, [[t, { bold: true, size: 10.5 }]], { nombre: 'Pain point ' + (i + 1) });
  txt(8.75, y + 0.25, 3.6, 0.66, [[b, { size: 8, color: '3A3A3A' }]], { ls: 1.0 });
  if (i < PP.length - 1) linea(8.75, y + PH - 0.04, 12.2, y + PH - 0.04, { color: C.sep, w: 0.75 });
});

/* ── pie ── */
txt(8.0, 7.0, 4.6, 0.14, [['Revisado con el servicio (sesión del 14/08) · Decreto 44/2022: reconocimiento, modificación, extinción y reintegro', { size: 6.5, italic: true, color: C.grisClaro }]], { align: 'right' });
txt(12.75, 7.08, 0.4, 0.2, [['3', { size: 10, color: C.negro }]], { align: 'right' });

pres.writeFile({ fileName: OUT }).then(f => console.log('escrito', f));
