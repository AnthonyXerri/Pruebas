"""Tabla sencilla de datos que faltan para el cuadro de Natalidad (para enviar a la Comunidad).

Uso: python3 natalidad/gen_tabla_peticion.py mockups/Datos_que_faltan_Natalidad.xlsx
"""
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

out = sys.argv[1]
F = 'Arial'
NAVY = '0A1F44'
thin = Side(style='thin', color='BFC3D1')
B = Border(left=thin, right=thin, top=thin, bottom=thin)
AMAR = PatternFill('solid', fgColor='FFF7CC')
GRIS = PatternFill('solid', fgColor='E4E7F0')
wrap = Alignment(wrap_text=True, vertical='top')

# (qué necesitamos, para qué lo usamos en el cuadro, prioridad)
GRUPOS = [
 ('eReg · registro de entrada', [
  ('Solicitudes y aportaciones registradas de esta ayuda, con nº de registro, fecha y hora',
   'Ver lo que entra antes de que exista expediente y las solicitudes pendientes de dar de alta', 'Alta'),
  ('Tipo de documento (solicitud o aportación) y canal de entrada (sede electrónica, oficina, ORVE)',
   'Separar solicitudes de aportaciones y filtrar por canal', 'Alta'),
  ('Marca de duplicado o de anulado',
   'No contar como pendientes las solicitudes duplicadas', 'Media'),
 ]),
 ('Atlantix · datos propios de la ayuda (no están en las vistas que tenemos)', [
  ('Tipo de solicitud (nacimiento, gestación, adopción)',
   'Filtro de toda la pantalla y composición', 'Alta'),
  ('Número de hijos o cuantía mensual de cada expediente',
   'Composición, atrasos e importes', 'Alta'),
  ('Revisión de conformidad (marca y fecha)',
   'Expedientes revisados sin proponer', 'Alta'),
  ('Propuesta a nómina: mes de nómina propuesto e importe',
   'Quién se queda fuera de cada propuesta y crédito propuesto', 'Alta'),
  ('Nómina de cada expediente: primera y última nómina',
   'Altas en nómina, beneficiarias activas y las que dejan de cobrar', 'Alta'),
  ('Motivo de denegación (requisito incumplido)',
   'Composición de las denegaciones', 'Media'),
  ('Bajas y modificaciones: fecha de efecto y motivo',
   'Beneficiarias que dejan de cobrar y mantenimiento', 'Media'),
  ('Fecha de nacimiento del menor o de parto previsto',
   'Fin del derecho a los 2 años', 'Media'),
  ('Nacionalidad, país de nacimiento y fecha de nacimiento de la solicitante',
   'Composición (la edad se muestra en tramos)', 'Media'),
  ('Bandeja de registros: alta y descarte, con fecha y motivo',
   'Pendientes de alta y solicitudes descartadas', 'Media'),
  ('Envío del fichero de terceros a gestión económica (fecha)',
   'Saber en qué punto está la validación de terceros', 'Media'),
 ]),
 ('Nexus · gestión económica', [
  ('Pagos por expediente y mes (nóminas y pagos únicos), con importe',
   'Gestión económica e importe ejecutado', 'Alta'),
  ('Crédito: autorizado (A), dispuesto (D) y ejecutado (OK) por línea y anualidad, y línea de cada expediente',
   'Tabla de crédito por línea y anualidad', 'Alta'),
  ('Documento D de cada expediente, con su fecha',
   'Crédito propuesto que aún no tiene D', 'Media'),
  ('Tercero: fecha de alta, fecha de rechazo y motivo',
   'Saber en qué punto está la validación de terceros', 'Media'),
 ]),
 ('Para unir los sistemas', [
  ('Campo que une eReg y Nexus con el expediente de Atlantix (en eReg creemos que es el nº de registro)',
   'Sin él no se pueden cruzar los datos', 'Alta'),
 ]),
 ('Unidad · no está en los sistemas (nos vale un Excel)', [
  ('Calendario mensual de nómina: cierre de la propuesta, envío a la Intervención y pago',
   'Tiempos del circuito mensual y atrasos', 'Alta'),
  ('Plazos: de tramitación y para aportar lo requerido (días y desde qué fecha cuentan)',
   'Expedientes fuera de plazo', 'Alta'),
 ]),
]

COLS = ['Nº', 'Qué necesitamos', 'Para qué lo usamos', 'Prioridad', '¿Dónde está? (tabla y columna)']
WID = [5, 52, 44, 10, 38]

wb = Workbook()
ws = wb.active
ws.title = 'Datos que faltan'
ws['A1'] = 'Ayudas por gestación, nacimiento o adopción · Datos que nos faltan para el cuadro'
ws['A1'].font = Font(name=F, size=13, bold=True, color=NAVY)
notas = [
    'De Atlantix ya tenemos los expedientes, las etapas, la bitácora, las notificaciones, las resoluciones y el municipio de la solicitante.',
    'Os pedimos rellenar la última columna: en qué tabla y columna está cada dato y, si lleva códigos, su catálogo. Si un dato no se graba en ningún sistema, indicadlo.',
    'Histórico desde enero de 2022. No hace falta enviar datos: solo saber dónde están para cargarlos en Celonis.',
]
for i, t in enumerate(notas, 2):
    c = ws.cell(row=i, column=1, value=t)
    c.font = Font(name=F, size=9, color='444444')
    ws.merge_cells(start_row=i, start_column=1, end_row=i, end_column=len(COLS))

r = 6
for i, h in enumerate(COLS, 1):
    c = ws.cell(row=r, column=i, value=h)
    c.font = Font(name=F, size=10, bold=True, color='FFFFFF')
    c.fill = PatternFill('solid', fgColor=NAVY)
    c.alignment = Alignment(wrap_text=True, vertical='center')
    c.border = B
r += 1
n = 0
for grupo, filas in GRUPOS:
    ws.cell(row=r, column=1, value=grupo)
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=len(COLS))
    c = ws.cell(row=r, column=1)
    c.font = Font(name=F, size=10, bold=True, color=NAVY)
    c.fill = GRIS
    for j in range(1, len(COLS) + 1):
        ws.cell(row=r, column=j).border = B
    r += 1
    for que, para, pri in filas:
        n += 1
        vals = [n, que, para, pri, None]
        for j, v in enumerate(vals, 1):
            c = ws.cell(row=r, column=j, value=v)
            c.font = Font(name=F, size=10 if j == 2 else 9,
                          bold=(j == 4 and pri == 'Alta'),
                          color=('9B1C1C' if (j == 4 and pri == 'Alta') else None))
            c.alignment = Alignment(wrap_text=True, vertical='top',
                                    horizontal='center' if j in (1, 4) else None)
            c.border = B
            if j == 5:
                c.fill = AMAR
        r += 1

for j, w in enumerate(WID, 1):
    ws.column_dimensions['ABCDE'[j - 1]].width = w
ws.freeze_panes = 'A7'
ws.print_title_rows = '6:6'
ws.page_setup.orientation = 'landscape'
ws.sheet_properties.pageSetUpPr.fitToPage = True
ws.page_setup.fitToWidth = 1
ws.page_setup.fitToHeight = 0
wb.save(out)
print('ok', n, 'datos')
