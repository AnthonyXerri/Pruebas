import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

out = sys.argv[1]
F = 'Arial'
NAVY = '0A1F44'
thin = Side(style='thin', color='BFC3D1')
B = Border(left=thin, right=thin, top=thin, bottom=thin)
AMAR = PatternFill('solid', fgColor='FFF7CC')

ROWS = [
 ('eReg · registro de entrada', None),
 ('Asientos de registro de la ayuda (solicitudes y aportaciones), con nº de registro, fecha y hora', ('', '', '')),
 ('Tipo de documento registrado (solicitud o aportación)', ('', '', '')),
 ('Canal de entrada (sede electrónica, oficina de registro, ORVE)', ('', '', '')),
 ('Marca de duplicado o de anulado', ('', '', '')),
 ('Atlantix · expediente y tramitación', None),
 ('Expediente, convocatoria, fecha de alta y fecha de resolución', ('GSTA_V_CEL_EXPEDIENTE; GSTA_V_EXPEDIENTE', 'CDEXPEDIENTE; FCINICIO; FCRESOLUCION; DS_CONVOCATORIA', '—')),
 ('Histórico de etapas, con su fecha', ('GSTA_V_CEL_ETAPA', 'DSETAPA; FCINICIO; FCFIN', '—')),
 ('Bitácora, requerimientos y notificaciones', ('GSTA_V_CEL_ACTIVIDAD; GSTA_V_CEL_NOTIFICACION', 'FCACTIVIDAD; FCNOTIFICACION; FCACUSE', '—')),
 ('Resolución firmada y su sentido', ('GSTA_V_CEL_DOC_ELABORADA', 'DSPLANTILLA; FCFIRMARECHAZO', '—')),
 ('Municipio de residencia de la solicitante', ('GSTA_V_INTERESADOS', 'DSMUNI_RESID', '—')),
 ('Tipo de solicitud (nacimiento, gestación, adopción, otros)', ('', '', '')),
 ('Número de hijos de la solicitud (o cuantía mensual)', ('', '', '')),
 ('Fecha de nacimiento del menor o de parto previsto', ('', '', '')),
 ('Nacionalidad, país de nacimiento y edad de la solicitante', ('', '', '')),
 ('Revisión de conformidad (marca y fecha)', ('', '', '')),
 ('Propuesta a nómina: mes de nómina propuesto e importe por anualidad', ('', '', '')),
 ('Nómina por expediente: primera y última nómina y pagos previstos por mes', ('', '', '')),
 ('Motivo de denegación (requisito incumplido)', ('', '', '')),
 ('Bajas y modificaciones: fecha de efecto y motivo', ('', '', '')),
 ('Bandeja de registros: entrada, alta y descarte (fecha y motivo)', ('', '', '')),
 ('Envío del fichero de terceros a gestión económica (fecha)', ('', '', '')),
 ('Nexus · contabilidad y terceros', None),
 ('Alta y rechazo del tercero (fecha y motivo)', ('', '', '')),
 ('Pagos por expediente y mes (primer pago, nómina, pagos únicos)', ('', '', '')),
 ('Línea presupuestaria del expediente', ('', '', '')),
 ('Autorizado (A), dispuesto (D) y ejecutado (OK) por línea y anualidad', ('', '', '')),
 ('Documento D de cada expediente, con su fecha', ('', '', '')),
 ('Unidad · fuera de los sistemas', None),
 ('Calendario mensual de nómina (envío a la Intervención y pago)', ('Lo aporta la unidad', '—', '—')),
 ('Plazo de tramitación y plazo para aportar lo requerido', ('Lo aporta la unidad', '—', '—')),
 ('Unión entre sistemas', None),
 ('Campo con el que se unen eReg y Nexus con el expediente', ('', 'eReg: REF_SOLICITUD (nº de registro, por confirmar). Nexus: ', '—')),
]

wb = Workbook()
ws = wb.active
ws.title = 'Datos que necesitamos'
ws['A1'] = 'Ayudas por gestación, nacimiento o adopción · Datos que necesitamos para el cuadro'
ws['A1'].font = Font(name=F, size=13, bold=True, color=NAVY)
ws['A2'] = 'Lo que está en blanco es lo que nos falta: os pedimos indicar la tabla, la columna y, si lleva códigos, su catálogo. Histórico desde enero de 2022, sin datos personales.'
ws['A2'].font = Font(name=F, size=9, italic=True, color='555555')
ws.merge_cells('A2:D2')
ws['A2'].alignment = Alignment(wrap_text=True)
ws.row_dimensions[2].height = 26

r = 4
for i, h in enumerate(['Campo', 'Tabla', 'Columna', 'Catálogo'], 1):
    c = ws.cell(row=r, column=i, value=h)
    c.font = Font(name=F, size=10, bold=True, color='FFFFFF')
    c.fill = PatternFill('solid', fgColor=NAVY)
    c.border = B
r += 1
for campo, vals in ROWS:
    if vals is None:
        ws.cell(row=r, column=1, value=campo)
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
        c = ws.cell(row=r, column=1)
        c.font = Font(name=F, size=10, bold=True, color=NAVY)
        c.fill = PatternFill('solid', fgColor='E4E7F0')
        c.border = B
    else:
        c = ws.cell(row=r, column=1, value=campo)
        c.font = Font(name=F, size=10)
        c.alignment = Alignment(wrap_text=True, vertical='top')
        c.border = B
        for j, v in enumerate(vals, 2):
            cc = ws.cell(row=r, column=j, value=v if v else None)
            cc.font = Font(name=F, size=9)
            cc.alignment = Alignment(wrap_text=True, vertical='top')
            cc.border = B
            if not v or v.endswith('Nexus: '):
                cc.fill = AMAR
    r += 1
for col, w in zip('ABCD', [58, 34, 40, 18]):
    ws.column_dimensions[col].width = w
ws.freeze_panes = 'A5'
ws.page_setup.orientation = 'landscape'
ws.sheet_properties.pageSetUpPr.fitToPage = True
ws.page_setup.fitToWidth = 1
ws.page_setup.fitToHeight = 0
wb.save(out)
print('ok', sum(1 for _, v in ROWS if v is not None), 'campos')
