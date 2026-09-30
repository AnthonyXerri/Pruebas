#!/usr/bin/env python3
"""
Añade el bloque de Discapacidad al deck de pain points, con el mismo
formato de tarjetas que el bloque de Dependencia.
Las cifras salen de los paneles de Celonis (PROD · Discapacidad),
vista ejecutiva —tablas por centro base— y vista directiva.
"""
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, PP_PLACEHOLDER

GRANATE = RGBColor(0x96, 0x16, 0x28)
ROJO    = RGBColor(0xC0, 0x00, 0x00)
GRIS    = RGBColor(0x76, 0x7C, 0x86)
BORDE   = RGBColor(0xE6, 0xE6, 0xE6)
NEGRO   = RGBColor(0x00, 0x00, 0x00)
BLANCO  = RGBColor(0xFF, 0xFF, 0xFF)
PREG    = RGBColor(0x2D, 0x2D, 0x2D)   # la pregunta, algo más marcada
FUENTE  = 'Century Gothic'

MX, GAP, COLS = 697841, 260000, 3
CARD_W = (12192000 - 2 * MX - GAP * (COLS - 1)) // COLS
CARD_H, TOP, PAD = 1930000, 1700000, 250000


def txt(cont, x, y, cx, cy, partes, align=PP_ALIGN.LEFT, interlineado=None):
    tb = cont.shapes.add_textbox(Emu(x), Emu(y), Emu(cx), Emu(cy))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    par = tf.paragraphs[0]
    par.alignment = align
    if interlineado:
        par.line_spacing = interlineado
    for t, nb, col, sz in partes:
        r = par.add_run()
        r.text = t
        r.font.name = FUENTE
        r.font.size = Pt(sz)
        r.font.bold = nb
        r.font.color.rgb = col
    return tb


def tarjeta(s, x, y, n, titulo, cifra, unidad, contexto, pregunta=False):
    card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                              Emu(x), Emu(y), Emu(CARD_W), Emu(CARD_H))
    card.adjustments[0] = 0.04
    card.fill.solid(); card.fill.fore_color.rgb = BLANCO
    card.line.color.rgb = BORDE; card.line.width = Pt(0.75)
    card.shadow.inherit = False
    card.text_frame.text = ''

    filete = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                Emu(x + 150000), Emu(y), Emu(320000), Emu(52000))
    filete.fill.solid(); filete.fill.fore_color.rgb = GRANATE
    filete.line.fill.background(); filete.shadow.inherit = False
    filete.text_frame.text = ''

    txt(s, x + PAD, y + 215000, 400000, 200000, [(f'{n:02d}', True, GRIS, 10)])
    txt(s, x + PAD, y + 450000, CARD_W - 2 * PAD, 480000,
        [(titulo, True, NEGRO, 12)], interlineado=1.15)
    txt(s, x + PAD, y + 940000, CARD_W - 2 * PAD, 400000,
        [(cifra, True, GRANATE, 28)])
    txt(s, x + PAD, y + 1320000, CARD_W - 2 * PAD, 200000,
        [(unidad, False, GRIS, 9)])
    if pregunta:
        ln = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(x + PAD), Emu(y + 1470000),
                                Emu(CARD_W - 2 * PAD), Emu(9525))
        ln.fill.solid(); ln.fill.fore_color.rgb = BORDE
        ln.line.fill.background(); ln.shadow.inherit = False
        ln.text_frame.text = ''
    txt(s, x + PAD, y + 1535000, CARD_W - 2 * PAD, 340000,
        [(contexto, False, PREG if pregunta else GRIS, 9)], interlineado=1.25)


def slide_dolores(prs, layout, titulo, subtitulo, dolores, pie=None, preguntas=False):
    s = prs.slides.add_slide(layout)
    for ph in list(s.placeholders):
        if ph.placeholder_format.type != PP_PLACEHOLDER.SLIDE_NUMBER:
            ph._element.getparent().remove(ph._element)
    txt(s, 518160, 360664, 9253637, 400000, [(titulo, True, NEGRO, 20)])
    txt(s, 521838, 900000, 10500000, 380000, [(subtitulo, False, GRIS, 11)])
    for i, (t, c, u, ctx) in enumerate(dolores):
        col, fila = i % COLS, i // COLS
        tarjeta(s, MX + col * (CARD_W + GAP), TOP + fila * (CARD_H + GAP),
                i + 1, t, c, u, ctx, pregunta=preguntas)
    if pie:
        txt(s, MX, TOP + 2 * (CARD_H + GAP) + 60000, 12192000 - 2 * MX, 300000,
            [(pie, False, GRIS, 9)])
    return s


# ════════════════════════════════════════════════════════════════════════
#  DISCAPACIDAD · Panel de Entradas — reconocimiento del grado
#  Cifras leídas de los paneles de Celonis (PROD), periodo 01/01–30/04/2026.
# ════════════════════════════════════════════════════════════════════════
DISCA = [
    ('Sin una foto única de la demanda',
     '23.412', 'solicitudes en cuatro meses',
     'El panel reúne en una pantalla diez centros base y cuatro tipos de solicitud.'),
    ('El plazo no decía dónde se iba',
     '44 de 77 d', 'en un solo tramo',
     'Por eso el panel parte el plazo en cuatro: uno se lleva más de la mitad.'),
    ('Retrabajo de las reclamaciones previas',
     '1.249', 'el 5,3 % de las entradas',
     'Llevan columna propia: vuelven a entrar y consumen capacidad sin generar altas.'),
    ('La ola de revisiones del RD 888/2022',
     '984', 'revisiones por el nuevo baremo',
     'Van en fila aparte para separarlas de la demanda ordinaria; 415 en un solo centro.'),
    ('Qué equipo de valoración hace falta',
     '58,8 %', 'de las calificaciones con despistaje',
     'Físico, psicológico o mixto y el tramo de edad deciden el circuito y la agenda.'),
    ('Centros base que no son comparables',
     '1.466', 'solicitudes del Centro Base 10',
     'El panel separa los subtotales 01-09 y 01-10: el 10 atiende solo a menores.'),
]
PIE = ('Lectura inversa de los paneles: qué problema resuelve cada cosa que han decidido medir · '
       'Volúmenes sobre centros 01-09 salvo la fila del RD 888/2022 y el Centro Base 10 · '
       'Fuente: Celonis · Discapacidad (PROD) · Panel de Entradas · 01/01/2026 – 30/04/2026.')

prs = Presentation('entrada.pptx')
layout = prs.slide_masters[0].slide_layouts[3]

# ── índice: corregir el salto de numeración ─────────────────────────────
ph = [x for x in prs.slides[1].placeholders
      if x.placeholder_format.type == PP_PLACEHOLDER.OBJECT][0]
for par in ph.text_frame.paragraphs:
    t = ''.join(r.text for r in par.runs)
    if t.strip().startswith('4. Próximos pasos'):
        par.runs[0].text = '3. Próximos pasos'
    if t.strip().startswith('2. Pain points · Discapacidad'):
        par.runs[0].text = '2. Pain points · Discapacidad'
        for r in par.runs[1:]:
            r.text = ''

slide_dolores(prs, layout,
              'Pain points · Discapacidad',
              'Reconocimiento del grado de discapacidad · los problemas que resuelven los paneles ya construidos',
              DISCA, PIE, preguntas=True)

# ── orden: portada, índice, CU1, CU2, Discapacidad, cierre ──────────────
lst = prs.slides._sldIdLst
ids = list(lst)
orden = [ids[0], ids[1], ids[2], ids[3], ids[5], ids[4]]
for e in ids:
    lst.remove(e)
for e in orden:
    lst.append(e)

prs.save('PainPoints_Dependencia_Discapacidad.pptx')
print('OK ·', len(list(lst)), 'diapositivas')
