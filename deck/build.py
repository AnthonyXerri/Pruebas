#!/usr/bin/env python3
"""
Bloque de Dependencia del deck de pain points.
Reutiliza plantilla, tipografía y paleta del PowerPoint original de Madrid Digital.
Formato de tarjetas: un dolor por tarjeta, una cifra y una línea de contexto.
"""
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, PP_PLACEHOLDER

# ── paleta tomada del fichero original ──────────────────────────────────
GRANATE = RGBColor(0x96, 0x16, 0x28)
ROJO    = RGBColor(0xC0, 0x00, 0x00)
GRIS    = RGBColor(0x76, 0x7C, 0x86)
BORDE   = RGBColor(0xE6, 0xE6, 0xE6)
FONDO   = RGBColor(0xF5, 0xF5, 0xF5)
NEGRO   = RGBColor(0x00, 0x00, 0x00)
BLANCO  = RGBColor(0xFF, 0xFF, 0xFF)
FUENTE  = 'Century Gothic'

# ── rejilla de tarjetas ─────────────────────────────────────────────────
MX      = 697841                      # margen lateral
GAP     = 260000
COLS    = 3
CARD_W  = (12192000 - 2 * MX - GAP * (COLS - 1)) // COLS
CARD_H  = 1930000
TOP     = 1700000


def txt(cont, x, y, cx, cy, partes, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
        interlineado=None):
    tb = cont.shapes.add_textbox(Emu(x), Emu(y), Emu(cx), Emu(cy))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
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


def tarjeta(s, x, y, n, titulo, cifra, unidad, contexto):
    """Tarjeta blanca con filete superior granate, número, cifra y una línea."""
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

    pad = 250000
    # número de orden
    txt(s, x + pad, y + 215000, 400000, 200000,
        [(f'{n:02d}', True, GRIS, 10)])
    # título del dolor
    txt(s, x + pad, y + 450000, CARD_W - 2 * pad, 480000,
        [(titulo, True, NEGRO, 12)], interlineado=1.15)
    # cifra grande + unidad
    txt(s, x + pad, y + 940000, CARD_W - 2 * pad, 400000,
        [(cifra, True, GRANATE, 28)])
    txt(s, x + pad, y + 1320000, CARD_W - 2 * pad, 200000,
        [(unidad, False, GRIS, 9)])
    # una sola línea de contexto
    txt(s, x + pad, y + 1520000, CARD_W - 2 * pad, 340000,
        [(contexto, False, GRIS, 9)], interlineado=1.25)


def slide_dolores(prs, layout, titulo, subtitulo, dolores, pie=None):
    s = prs.slides.add_slide(layout)
    for ph in list(s.placeholders):
        if ph.placeholder_format.type != PP_PLACEHOLDER.SLIDE_NUMBER:
            ph._element.getparent().remove(ph._element)

    txt(s, 518160, 360664, 9253637, 400000, [(titulo, True, NEGRO, 20)])
    txt(s, 521838, 900000, 10500000, 380000, [(subtitulo, False, GRIS, 11)])

    for i, (t, c, u, ctx) in enumerate(dolores):
        col, fila = i % COLS, i // COLS
        tarjeta(s, MX + col * (CARD_W + GAP), TOP + fila * (CARD_H + GAP),
                i + 1, t, c, u, ctx)

    if pie:
        y = TOP + 2 * (CARD_H + GAP) + 60000
        txt(s, MX, y, 12192000 - 2 * MX, 300000, [(pie, False, GRIS, 9)])
    return s


# ════════════════════════════════════════════════════════════════════════
#  CU1 · Solicitud y reconocimiento de la dependencia, grado y PIA
# ════════════════════════════════════════════════════════════════════════
CU1 = [
    ('Subsanación documental',
     '54 d', 'bloqueado de media',
     'El expediente se detiene esperando documentación que no se validó en el alta.'),
    ('Citación manual',
     '13 %', 'requiere una segunda cita',
     'Sin agenda integrada ni recordatorios: incomparecencias y recitaciones.'),
    ('Valoración en papel',
     '91 %', 'de las valoraciones',
     'Se recoge fuera de sistema y se transcribe después, con riesgo de error.'),
    ('Reparto desigual de la carga',
     '62–128 %', 'carga por técnico',
     'Del técnico infrautilizado al saturado, sin reglas de asignación.'),
    ('Resolución de Grado y PIA',
     '62 d', 'de media tras la valoración',
     'Dictamen, comisión y resolución encadenados y manuales.'),
    ('Documentación inicial incompleta',
     '+65 d', 'adicionales',
     'Los expedientes sin informe médico se desvían del flujo estándar.'),
]
PIE_CU1 = ('Beneficio estimado en la PoC: entre −25 % y −60 % del plazo según la oportunidad · '
           'Fuente: SIDEMA · cuadro de mando de gestión de equipo.')

# ════════════════════════════════════════════════════════════════════════
#  CU2 · Adjudicación de servicios comunitarios (EELL)
# ════════════════════════════════════════════════════════════════════════
CU2 = [
    ('Espera hasta el servicio',
     '67 d', 'frente a 45 de objetivo',
     'Desde que se resuelve el PIA hasta que la prestación se activa.'),
    ('Prelación por grado',
     '89', 'Grado III fuera de umbral',
     'La gran dependencia no se atiende antes que la moderada.'),
    ('Personas no localizadas',
     '34 %', 'de las exclusiones',
     'Se excluye a quien no responde al teléfono, sin registro del intento.'),
    ('Reingresos sin antigüedad',
     '34', 'personas reincorporadas',
     'Al volver ocupan nueva posición y empiezan la espera de cero.'),
    ('Desigualdad territorial',
     '34–112 d', 'según el municipio',
     'El plazo depende del lote: la Sierra Norte espera el triple.'),
    ('Lista de espera creciente',
     '312', 'expedientes por encima de 90 d',
     'Las entradas superan a las activaciones de forma sostenida desde marzo.'),
]
PIE_CU2 = ('Beneficio pendiente de cuantificar: este caso de uso no cuenta todavía con PoC de ahorro · '
           'Fuente: SIDEMA y SAP · cuadro de mando de lista de espera.')

# ════════════════════════════════════════════════════════════════════════
prs = Presentation('base.pptx')
layout = prs.slide_masters[0].slide_layouts[3]

# ── índice actualizado ──────────────────────────────────────────────────
INDICE = ['1. Validación del proceso: visión inicial y dudas abiertas',
          '2. Pain points · Dependencia',
          '3. Pain points · Discapacidad',
          '4. Próximos pasos']
ph = [x for x in prs.slides[1].placeholders
      if x.placeholder_format.type == PP_PLACEHOLDER.OBJECT][0]
llenos = [p for p in ph.text_frame.paragraphs if ''.join(r.text for r in p.runs).strip()]
for par, nuevo in zip(llenos, INDICE):
    par.runs[0].text = nuevo
    for r in par.runs[1:]:
        r.text = ''

slide_dolores(prs, layout,
              'Pain points · Dependencia — CU1',
              'Solicitud y reconocimiento de la dependencia, grado y PIA',
              CU1, PIE_CU1)
slide_dolores(prs, layout,
              'Pain points · Dependencia — CU2',
              'Adjudicación de servicios comunitarios (EELL)',
              CU2, PIE_CU2)

# ── orden final: portada, índice, validación, CU1, CU2, cierre ──────────
lst = prs.slides._sldIdLst
ids = list(lst)
orden = [ids[0], ids[1], ids[2], ids[5], ids[6], ids[4]]   # ids[3] = tabla antigua
for e in ids:
    lst.remove(e)
for e in orden:
    lst.append(e)

prs.save('PainPoints_Dependencia.pptx')
print('OK ·', len(list(lst)), 'diapositivas')
