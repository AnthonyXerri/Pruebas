#!/usr/bin/env python3
"""
Genera el bloque de Dependencia (CU1 y CU2) del deck de pain points,
reutilizando la plantilla, la tipografía y el formato de tabla del
PowerPoint original de Madrid Digital.
"""
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import copy

# ── paleta y tipografía tomadas del fichero original ────────────────────
GRANATE = RGBColor(0x96, 0x16, 0x28)   # cifra de beneficio
ROJO    = RGBColor(0xC0, 0x00, 0x00)   # dato clave dentro del texto
GRIS    = RGBColor(0x76, 0x7C, 0x86)   # texto secundario
BORDE   = RGBColor(0xE6, 0xE6, 0xE6)
NEGRO   = RGBColor(0x00, 0x00, 0x00)
BLANCO  = RGBColor(0xFF, 0xFF, 0xFF)
FUENTE  = 'Century Gothic'

# ── geometría de la tabla, calcada de la diapositiva 4 ──────────────────
TX, TY   = 697841, 1547480
COLS     = [1861532, 3780000, 1908000, 1908000, 1620000]
H_CAB    = 252000
H_FILA   = 684000
NUM_X    = 852310
NUM_D    = 250000
INSET_L0 = 430000          # hueco en la 1ª columna para el número


def celda(tc, partes, size, bold=False, color=NEGRO, inset_izq=None):
    """Escribe una celda. `partes` es [(texto, negrita, color, tamaño|None), ...]."""
    tc.fill.solid(); tc.fill.fore_color.rgb = BLANCO
    tc.margin_top = Emu(54000); tc.margin_bottom = Emu(54000)
    tc.margin_left = Emu(inset_izq if inset_izq is not None else 91440)
    tc.margin_right = Emu(91440)
    tc.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf = tc.text_frame; tf.word_wrap = True
    par = tf.paragraphs[0]; par.alignment = PP_ALIGN.LEFT
    for txt, nb, col, sz in partes:
        r = par.add_run(); r.text = txt
        r.font.name = FUENTE
        r.font.size = Pt(sz if sz else size)
        r.font.bold = nb if nb is not None else bold
        r.font.color.rgb = col if col else color


def bordes(tc):
    """La plantilla usa rejilla gris clara en las cuatro caras."""
    from pptx.oxml.ns import qn
    tcPr = tc._tc.get_or_add_tcPr()
    for tag in ('a:lnL', 'a:lnR', 'a:lnT', 'a:lnB'):
        ln = tcPr.makeelement(qn(tag), {'w': '12700', 'cap': 'flat',
                                        'cmpd': 'sng', 'algn': 'ctr'})
        fill = ln.makeelement(qn('a:solidFill'), {})
        clr = fill.makeelement(qn('a:srgbClr'), {'val': 'E6E6E6'})
        fill.append(clr); ln.append(fill)
        tcPr.append(ln)


def texto(slide, x, y, cx, cy, partes, align=PP_ALIGN.LEFT):
    tb = slide.shapes.add_textbox(Emu(x), Emu(y), Emu(cx), Emu(cy))
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    par = tf.paragraphs[0]; par.alignment = align
    for txt, nb, col, sz in partes:
        r = par.add_run(); r.text = txt
        r.font.name = FUENTE; r.font.size = Pt(sz)
        r.font.bold = nb; r.font.color.rgb = col
    return tb


def disco(slide, x, y, n):
    """Número de orden: círculo granate con el dígito dentro."""
    sh = slide.shapes.add_shape(MSO_SHAPE.OVAL, Emu(x), Emu(y), Emu(NUM_D), Emu(NUM_D))
    sh.fill.solid(); sh.fill.fore_color.rgb = BLANCO
    sh.line.color.rgb = ROJO; sh.line.width = Pt(1)
    sh.shadow.inherit = False
    tf = sh.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    par = tf.paragraphs[0]; par.alignment = PP_ALIGN.CENTER
    r = par.add_run(); r.text = str(n)
    r.font.name = FUENTE; r.font.size = Pt(10); r.font.bold = True
    r.font.color.rgb = ROJO


def slide_painpoints(prs, layout, titulo, subtitulo, filas, nota=None):
    """filas = [(oportunidad, [(txt,bold,color,sz)…] situación, causa, impacto,
                 (cifra, unidad)), …]"""
    s = prs.slides.add_slide(layout)
    from pptx.enum.shapes import PP_PLACEHOLDER
    for ph in list(s.placeholders):
        if ph.placeholder_format.type != PP_PLACEHOLDER.SLIDE_NUMBER:
            ph._element.getparent().remove(ph._element)

    texto(s, 518160, 360664, 9253637, 381945,
          [(titulo, True, NEGRO, 20)])
    texto(s, 513838, 954520, 11164324, 420000,
          [(subtitulo, False, GRIS, 11)])

    alto = H_CAB + H_FILA * len(filas)
    gf = s.shapes.add_table(len(filas) + 1, 5, Emu(TX), Emu(TY),
                            Emu(sum(COLS)), Emu(alto))
    tb = gf.table
    tb.first_row = False; tb.horz_banding = False
    for i, w in enumerate(COLS):
        tb.columns[i].width = Emu(w)
    tb.rows[0].height = Emu(H_CAB)
    for i in range(1, len(filas) + 1):
        tb.rows[i].height = Emu(H_FILA)

    cab = ['Oportunidad', 'Situación actual', 'Causa raíz',
           'Impacto en el proceso', 'Beneficio esperado']
    for c, t in enumerate(cab):
        tc = tb.cell(0, c)
        celda(tc, [(t, True, NEGRO, 11)], 11)
        bordes(tc)

    for r, (op, sit, causa, imp, ben) in enumerate(filas, start=1):
        celda(tb.cell(r, 0), [(op, True, NEGRO, 10.5)], 10.5, inset_izq=INSET_L0)
        celda(tb.cell(r, 1), sit, 9)
        celda(tb.cell(r, 2), [(causa, False, NEGRO, 9)], 9)
        celda(tb.cell(r, 3), [(imp, False, NEGRO, 9)], 9)
        celda(tb.cell(r, 4), [('', False, NEGRO, 9)], 9)
        for c in range(5):
            bordes(tb.cell(r, c))

        top = TY + H_CAB + (r - 1) * H_FILA
        disco(s, NUM_X, top + (H_FILA - NUM_D) // 2, r)

        bx = TX + sum(COLS[:4]) + 110000
        bw = COLS[4] - 220000
        cifra, unidad = ben
        numerico = cifra[0] in '+-−'
        col_cifra = GRANATE if numerico else GRIS
        texto(s, bx, top + (150000 if numerico else 190000), bw, 215444,
              [(cifra, True, col_cifra, 14 if numerico else 9.5)], PP_ALIGN.CENTER)
        texto(s, bx, top + 395000, bw, 200000,
              [(unidad, False, GRIS, 8)], PP_ALIGN.CENTER)

    if nota:
        texto(s, 697841, TY + alto + 90000, 11077532, 300000,
              [(nota, False, GRIS, 8)])
    return s


# ════════════════════════════════════════════════════════════════════════
#  CU1 · Solicitud y reconocimiento de la dependencia, grado y PIA
#  Cifras procedentes de la PoC y del mockup de Gestión de Equipo.
# ════════════════════════════════════════════════════════════════════════
CU1 = [
    ('Alertas inteligentes en revisión y subsanación documental.',
     [('Un ', False, NEGRO, 9),
      ('alto volumen de expedientes entra en subsanación y permanece bloqueado '
       '54 días de media', True, ROJO, 10),
      (' por documentación incompleta o incorrecta.', False, NEGRO, 9)],
     'Falta de validaciones previas, comunicación poco clara y ausencia de '
     'seguimiento proactivo.',
     'Bloqueo prolongado de expedientes, incremento del backlog y retraso en el flujo.',
     ('−30%', '3,7 días/exp.')),

    ('Optimización de citación y realización de valoración.',
     [('La ', False, NEGRO, 9),
      ('citación se gestiona de forma manual, sin integración de agendas ni '
       'recordatorios', True, ROJO, 10),
      (', lo que provoca incomparecencias: un ', False, NEGRO, 9),
      ('13% requiere una segunda cita', True, ROJO, 10),
      ('.', False, NEGRO, 9)],
     'Procesos manuales, falta de automatización y ausencia de priorización homogénea.',
     'Retrasos de planificación, más carga operativa y recitaciones que alargan el ciclo.',
     ('−40%', '11,4 días/exp.')),

    ('Digitalización e IA en la valoración.',
     [('El ', False, NEGRO, 9),
      ('91% de las valoraciones se realiza en papel o en sistemas no integrados',
       True, ROJO, 10),
      (', obligando a transcripción posterior.', False, NEGRO, 9)],
     'Recogida manual, sin herramientas digitales en campo y con sistemas no integrados.',
     'Demoras adicionales, riesgo de errores y falta de estandarización en los criterios.',
     ('−25%', '2,5 días/exp.')),

    ('Balanceo de cargas en valoración y en gestión del PIA.',
     [('Existe una ', False, NEGRO, 9),
      ('distribución desigual de expedientes y tramitaciones sin responsable claro',
       True, ROJO, 10),
      (', visible al medir por trabajador y por hito.', False, NEGRO, 9)],
     'Sin reglas automáticas de asignación, sin visibilidad en tiempo real ni trazabilidad.',
     'Sobrecarga en unos equipos, infrautilización en otros y retrasos innecesarios.',
     ('+30-40%', 'eficiencia')),

    ('Alertas en la resolución de Grado y PIA.',
     [('La ', False, NEGRO, 9),
      ('fase posterior a la valoración es manual y secuencial', True, ROJO, 10),
      (' —dictamen, comisión y resolución—, con una ', False, NEGRO, 9),
      ('media de 62 días', True, ROJO, 10),
      ('.', False, NEGRO, 9)],
     'Falta de automatización y dependencia de trámites administrativos encadenados.',
     'Cuello de botella en la fase final, colas de expedientes y retrasos en la resolución.',
     ('−60%', '37 días/exp.')),

    ('Control documental previo de informes médicos (AVC).',
     [('Parte de los expedientes ', False, NEGRO, 9),
      ('se desvía del flujo estándar por falta de documentación inicial',
       True, ROJO, 10),
      (', generando retrabajo y hasta ', False, NEGRO, 9),
      ('+65 días adicionales', True, ROJO, 10),
      ('.', False, NEGRO, 9)],
     'Ausencia de validaciones en el alta y falta de control documental previo.',
     'Desvíos, dobles citaciones, retrabajo y alta variabilidad en los tiempos '
     'de tramitación.',
     ('−45%', '37,5 días/exp.')),
]

# ════════════════════════════════════════════════════════════════════════
#  CU2 · Adjudicación de servicios comunitarios (EELL)
#  Magnitudes observadas en el mockup de Gestión de Lista de Espera.
#  El beneficio queda por cuantificar: no hay PoC de ahorro para este caso.
# ════════════════════════════════════════════════════════════════════════
CU2 = [
    ('Espera entre la resolución del PIA y el alta efectiva del servicio.',
     [('El plazo medio de notificación a prestación es de ', False, NEGRO, 9),
      ('67 días frente a un objetivo interno de 45', True, ROJO, 10),
      (' (+49%), con 312 solicitudes en lista de espera.', False, NEGRO, 9)],
     'Capacidad limitada de los lotes territoriales y gestión de contacto no priorizada.',
     'Derecho reconocido sin prestación efectiva y lista de espera creciente mes a mes.',
     ('Por cuantificar', '67 d · objetivo 45 d')),

    ('Garantía de prelación por grado de dependencia.',
     [('89 personas de Grado III superan el umbral de espera', True, ROJO, 10),
      (' y el Grado III tarda ', False, NEGRO, 9),
      ('91 días de media', True, ROJO, 10),
      (', más que los grados I y II.', False, NEGRO, 9)],
     'La asignación se resuelve por disponibilidad del lote, no por orden de prelación.',
     'La gran dependencia espera tanto o más que la moderada, incumpliendo la prelación.',
     ('Por cuantificar', '89 exp. Grado III')),

    ('Contacto trazable con la persona en lista de espera.',
     [('148 exclusiones (15,3%)', True, ROJO, 10),
      (', de las que un ', False, NEGRO, 9),
      ('34% son «no localizado tras 6 intentos»', True, ROJO, 10),
      (' y un 24% renuncia verbal sin registro.', False, NEGRO, 9)],
     'Contacto solo telefónico, datos desactualizados en SIDEMA y sin registro del intento.',
     'Personas excluidas sin verificación real y pérdida de derecho por un fallo de contacto.',
     ('Por cuantificar', '148 exclusiones')),

    ('Reingreso sin pérdida de antigüedad en la lista.',
     [('34 excluidos por «no localizado» han pedido reincorporación', True, ROJO, 10),
      (' —el 23% de ese motivo— y al reingresar ', False, NEGRO, 9),
      ('ocupan nueva posición, no la previa', True, ROJO, 10),
      ('.', False, NEGRO, 9)],
     'La exclusión no distingue entre causa real y fallo en la gestión del contacto.',
     'Penaliza a quien no fue localizado por un error propio y alarga su espera de nuevo.',
     ('Por cuantificar', '34 reingresos')),

    ('Equilibrio territorial entre lotes y municipios.',
     [('La espera va de 34 días en Las Rozas a 112 en Bustarviejo', True, ROJO, 10),
      ('; el lote 5 concentra la espera más larga y la mayor tasa de exclusión '
       '(21,4%).', False, NEGRO, 9)],
     'Capacidad desigual de los lotes y zonas de especial dificultad sin refuerzo.',
     'El plazo hasta recibir el servicio depende del municipio de residencia.',
     ('Por cuantificar', '34 d – 112 d')),

    ('Previsión de capacidad frente a la demanda entrante.',
     [('Las entradas superan a las activaciones desde marzo', True, ROJO, 10),
      (' y hay ', False, NEGRO, 9),
      ('312 solicitudes atascadas por encima de 90 días', True, ROJO, 10),
      (' (25,1%).', False, NEGRO, 9)],
     'Capacidad de activación plana frente a demanda creciente, sin previsión de carga.',
     'El backlog crece de forma sostenida y la espera media empeora cada mes.',
     ('Por cuantificar', '312 exp. > 90 d')),
]

NOTA_CU2 = ('Los beneficios de CU2 están pendientes de cuantificar: a diferencia de CU1, '
            'este caso de uso no cuenta todavía con una PoC de ahorro. Las cifras mostradas '
            'son la magnitud observada sobre datos de SIDEMA y SAP (ene–jun 2025).')

prs = Presentation('base.pptx')
layout = prs.slide_masters[0].slide_layouts[3]      # Diapositiva de contenido

s1 = slide_painpoints(
    prs, layout,
    '2. Pain points · Dependencia — CU1',
    'Caso 1: Solicitud y reconocimiento de la dependencia, grado y PIA · '
    'oportunidades priorizadas a partir de la PoC y del cuadro de mando de gestión de equipo',
    CU1)

s2 = slide_painpoints(
    prs, layout,
    '2. Pain points · Dependencia — CU2',
    'Caso 2: Adjudicación de servicios comunitarios (EELL) · '
    'oportunidades priorizadas a partir del cuadro de mando de gestión de lista de espera',
    CU2, nota=NOTA_CU2)

# reordenar: portada, índice, validación, CU1, CU2, cierre — y quitar la tabla antigua
xml = prs.slides._sldIdLst
ids = list(xml)
orden = [ids[0], ids[1], ids[2], ids[5], ids[6], ids[4]]   # ids[3] = tabla CU1 original
for e in ids:
    xml.remove(e)
for e in orden:
    xml.append(e)

prs.save('PainPoints_Dependencia.pptx')
print('OK ·', len(prs.slides.__iter__.__self__._sldIdLst), 'diapositivas')
