import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

out = sys.argv[1]
F = 'Arial'
NAVY = '0A1F44'
thin = Side(style='thin', color='C9CCD8')
B = Border(left=thin, right=thin, top=thin, bottom=thin)
HDR = PatternFill('solid', fgColor=NAVY)
GRP = PatternFill('solid', fgColor='E4E7F0')
FILL = PatternFill('solid', fgColor='FFF7CC')   # celdas a rellenar
PRI = {'Alta': PatternFill('solid', fgColor='F8D7D7'),
       'Media': PatternFill('solid', fgColor='FCE9CF'),
       'Baja': PatternFill('solid', fgColor='E3F1E3')}
wrap = Alignment(wrap_text=True, vertical='top')

def title(ws, text, sub):
    ws['A1'] = text
    ws['A1'].font = Font(name=F, size=14, bold=True, color=NAVY)
    ws['A2'] = sub
    ws['A2'].font = Font(name=F, size=10, italic=True, color='555555')

def header(ws, row, cols):
    for i, c in enumerate(cols, 1):
        cell = ws.cell(row=row, column=i, value=c)
        cell.font = Font(name=F, size=10, bold=True, color='FFFFFF')
        cell.fill = HDR
        cell.alignment = Alignment(wrap_text=True, vertical='center')
        cell.border = B

def widths(ws, ws_w):
    for i, w in enumerate(ws_w, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

wb = Workbook()

# ───────────────────────── Hoja 1: Qué pedir
ws = wb.active
ws.title = 'Qué pedir'
title(ws, 'Ayudas por gestación, nacimiento o adopción · Datos que faltan para el cuadro',
      'Revisión del 18/11/2026 frente al mockup v31 y al documento funcional. Lo que ya está en Atlantix va en la hoja «Ya disponible». Sin datos personales identificativos; histórico desde enero de 2022.')
ws['A3'] = ('Cómo rellenar: las columnas amarillas (Tabla, Columna, ¿Guarda histórico?, Observaciones) son para quien conozca el sistema. '
            'Ejemplo de formato: Tabla «NOMBRE_TABLA» · Columna «NOMBRE_COLUMNA» · ¿Histórico? «Sí, una fila por cambio» / «No, solo el valor actual».')
ws['A3'].font = Font(name=F, size=9, color='555555')
ws.merge_cells('A3:K3')
ws['A3'].alignment = Alignment(wrap_text=True, vertical='top')
ws.row_dimensions[3].height = 28
cols = ['Nº', 'Dato que falta', 'Para qué en el cuadro', 'Qué hemos encontrado en Atlantix',
        'Qué pedimos', 'Estado', 'Prioridad', 'Tabla', 'Columna', '¿Guarda histórico?', 'Observaciones']
header(ws, 5, cols)

ITEMS = [
 ('eReg · registro de entrada (equipo de eReg, vía Madrid Digital)', [
  ('E1', 'Asientos de registro de la ayuda: solicitudes y aportaciones, con nº de registro, fecha y hora',
   'Fase previa: entradas en registro, aportaciones, solicitudes recibidas y pendientes de alta. Stock «sin abrir». Tiempo E2E desde el registro.',
   'Solo la fecha de eReg (FC_SOL_EREG) y el nº de registro (REF_SOLICITUD) de las solicitudes que YA tienen expediente. No vemos las pendientes de alta ni las aportaciones.',
   'Tabla o vista de asientos de eReg de esta ayuda desde 01/2022. Clave de unión: nº de registro (= REF_SOLICITUD de Atlantix).',
   'Falta', 'Alta'),
  ('E2', 'Tipo de documento o modelo de formulario del asiento (solicitud, aportación, comunicación, genérica)',
   'Separar solicitudes de aportaciones (la clasificación es por modelo de formulario, sesión del 12/11).',
   'Nada.', 'Columna del asiento con el modelo o tipo de documento y su catálogo.', 'Falta', 'Alta'),
  ('E3', 'Canal de entrada (sede electrónica, oficina de registro, ORVE)',
   'Filtro «Canal» de toda la pantalla y dimensión de Composición.',
   'Nada (el medio de notificación de la interesada no es el canal de entrada).', 'Columna del canal del asiento y su catálogo.', 'Falta', 'Alta'),
  ('E4', 'Marca de duplicado y de anulado del asiento',
   'Pendientes de alta reales; solicitudes descartadas por duplicadas.',
   'Algunos expedientes anulados en Atlantix con la justificación «se abre expediente con otro registro» (texto libre).',
   'Marca o motivo de duplicado / anulación del asiento.', 'Falta', 'Media'),
  ('E5', 'Fecha de registro de la aportación a un requerimiento',
   'Plazo de aportación: «en plazo», «plazo vencido sin aportación», «valorar desistimiento».',
   'La bitácora tiene «Documento aportado» con la fecha en que se incorpora al expediente (no la de registro).',
   'Fecha de registro de cada aportación y su nº de registro (para unirla al expediente).', 'Parcial', 'Media'),
 ]),
 ('Atlantix · tablas propias de la ayuda (equivalentes a las PNCA_ de PnC; no están en el pool)', [
  ('A1', 'Tipo de solicitud (nacimiento, gestación, adopción, otros)',
   'Filtro «Tipo de solicitud» de toda la pantalla y dimensión de Composición.',
   'No está en las vistas GSTA_ (en PnC sale de PNCA_EXPEDIENTE.IT_TIPO_SOLICITUD).', 'Tabla y columna del tipo de solicitud y su catálogo.', 'Falta', 'Alta'),
  ('A2', 'Número de hijos de la solicitud (o cuantía mensual: 500 € por hijo)',
   'Composición (hijos por solicitud). Atrasos e importes: meses × 500 € por hijo.',
   'Nada (en PnC, PNCA_EXPEDIENTE.NM_CUANTIA_MES).', 'Columna con el nº de hijos o la cuantía mensual por expediente, con su histórico.', 'Falta', 'Alta'),
  ('A3', 'Fecha de nacimiento del menor o de parto previsto',
   'Fin del derecho (extinciones a los 2 años) y pagos únicos.', 'Nada.', 'Columna con la fecha (no hace falta ningún otro dato del menor).', 'Falta', 'Media'),
  ('A4', 'Revisión de conformidad (marca y fecha)',
   'Cabecera: «revisados sin proponer». Atrasos (vista «Revisados sin proponer»). Expedientes sin actividad.',
   'No es una etapa ni aparece en la bitácora. Solo existe el hito «Instrucción» en Gestión Expediente (2.651 expedientes).',
   'Dónde se marca que un expediente está revisado de conformidad y con qué fecha. Si no se graba, decirlo.', 'Falta', 'Alta'),
  ('A5', 'Propuesta a nómina: mes de nómina propuesto',
   'Revisados que se quedaron fuera de la última propuesta. Atrasos por remesa. Situación «esperando la nómina».',
   'Fecha de la etapa PROPUESTA FAVORABLE (sí). El mes de nómina propuesto no (en PnC, CD_MES/CD_ANO_PRIM_NOMINA).',
   'Columna con el mes y año de la nómina propuesta, con su histórico.', 'Parcial', 'Alta'),
  ('A6', 'Importe propuesto por anualidad (atrasos y mensualidades)',
   'Crédito: «propuesto, sin D». Coste de proponer a los revisados. Atrasos.', 'Nada.', 'Importe propuesto por expediente y anualidad.', 'Falta', 'Media'),
  ('A7', 'Nómina en Atlantix: primera y última nómina, cuantía y pagos previstos por expediente y mes',
   'Gestión económica: nuevas altas en nómina, beneficiarias activas, que dejan de cobrar. Atrasos por remesa.',
   'Nada (en PnC, PNCA_EXPEDIENTE: CD_MES_PRIM_NOMINA, CD_MES_ULT_NOMINA, NM_CUANTIA_MES).', 'Tabla de nómina o de pagos previstos por expediente y mes.', 'Falta', 'Alta'),
  ('A8', 'Motivo de denegación (requisito incumplido)',
   'Dimensión de Composición «Requisito incumplido».',
   'Solo la plantilla genérica «Resolución denegatoria por incumplimiento de requisitos».', 'Columna con el motivo o causa de denegación y su catálogo.', 'Falta', 'Media'),
  ('A9', 'Bajas y extinciones: fecha de efecto y motivo',
   'Beneficiarias que dejan de cobrar (extinciones, bajas).',
   'Etapa RESOLUCIÓN BAJA y notificación de baja (fechas de trámite). Sin fecha de efecto ni motivo.', 'Fecha de efecto y motivo de la baja o extinción.', 'Parcial', 'Media'),
  ('A10', 'Modificaciones en mantenimiento: tipo y fecha de efecto',
   'Mantenimiento y nómina.',
   'Etapas de modificación (positiva, negativa, sin variación, baja) con su fecha de trámite.', 'Fecha de efecto de cada modificación.', 'Parcial', 'Baja'),
  ('A11', 'Bandeja de registros de Atlantix: entrada, alta y descarte (fecha y motivo)',
   'Fase previa: pendientes de alta y descartadas por duplicadas.', 'No está en el pool.', 'Tabla de la bandeja de registros.', 'Falta', 'Media'),
  ('A12', 'Datos de la solicitante: nacionalidad, país de nacimiento y edad',
   'Composición: edad (en tramos), nacionalidad, país de nacimiento.',
   'Municipio de residencia: sí. Edad: solo el 21 % tiene fecha de nacimiento (2022-23 menos del 10 %). Nacionalidad: no (aproximación por DNI / NIE). País de nacimiento: no.',
   'Nacionalidad y país de nacimiento (catálogo SUCA_PAIS u otro) y la edad o fecha de nacimiento completa (se mostrará solo en tramos).', 'Parcial', 'Media'),
  ('A13', 'Envío del fichero de terceros a gestión económica (fecha)',
   'Subestados de Validación de terceros («esperando el fichero mensual», «en gestión económica»).',
   'Solo la etapa VALIDACIÓN TERCERO completa (inicio y fin).', 'Fecha de envío del fichero de terceros por expediente.', 'Falta', 'Media'),
 ]),
 ('Nexus · contabilidad y terceros (gestión económica, vía Madrid Digital)', [
  ('N1', 'Alta del tercero (fecha) y rechazo (fecha y motivo)',
   'Subestados de Validación de terceros («tercero creado, sin cargar», «tercero rechazado»).', 'Nada.', 'Tabla de terceros con fechas de alta y rechazo y su motivo.', 'Falta', 'Media'),
  ('N2', 'Pagos (ADOK) por expediente y mes: primer pago, nóminas, pagos únicos y rectificaciones',
   'Gestión económica: nuevas altas, beneficiarias activas, pagos únicos, que dejan de cobrar, importe ejecutado. Situación «esperando la nómina».',
   'Nada.', 'Pagos por expediente con mes de nómina, fecha, importe, concepto y tipo de pago.', 'Falta', 'Alta'),
  ('N3', 'Autorizado (A), dispuesto (D) y ejecutado (OK) por línea y anualidad',
   'Tabla «Crédito por línea y anualidad»; importe ejecutado y comprometido.', 'Nada.', 'Importes A, D y OK por línea presupuestaria y anualidad.', 'Falta', 'Alta'),
  ('N4', 'Línea presupuestaria del expediente', 'Crédito por línea.', 'Nada.', 'Línea a la que se imputa cada expediente.', 'Falta', 'Alta'),
  ('N5', 'Documento D de cada expediente y de cada modificación, con su fecha', 'Crédito: «propuesto, sin D».', 'Nada.', 'Documentos D con fecha e importe.', 'Falta', 'Media'),
  ('N6', 'Tipo de documento contable del pago único (con nº de expediente o solo DNI)', 'Pagos únicos.', 'Nada.', 'Tipo de documento contable y cómo se identifica el expediente.', 'Falta', 'Baja'),
  ('N7', 'Clave de unión entre Nexus y Atlantix', 'Unir pagos y crédito con los expedientes.', 'Nada.', 'Campo de Nexus que identifica el expediente de Atlantix (nº de expediente u otro).', 'Falta', 'Alta'),
 ]),
 ('Unidad · fuera de los sistemas', [
  ('U1', 'Calendario mensual de nómina (fichero de terceros, cierre de propuesta, envío a la Intervención y pago)',
   'Selector «Días de» → calendario mensual. Remesas y atrasos.', 'La Intervención responde por lotes, pero el calendario no está en los sistemas.', 'Calendario de cada mes desde 2022 (Excel).', 'Falta', 'Alta'),
  ('U2', 'Plazo de tramitación según la normativa (días)', 'Incumplimiento de plazo (el mockup usa 90 días por defecto).',
   'DIAS_TRAM de Atlantix son días transcurridos (0 a 600), no el plazo.', 'Plazo legal y desde qué fecha cuenta.', 'Falta', 'Alta'),
  ('U3', 'Plazo de aportación de los requerimientos (días hábiles)', '«En plazo de aportación» / «plazo vencido» / «valorar desistimiento».',
   'Fecha de notificación y de acuse de cada requerimiento: sí.', 'Nº de días y desde qué fecha cuentan (notificación o acceso).', 'Falta', 'Media'),
  ('U4', 'Responsable de cada situación («Depende de»)', 'Expedientes sin actividad y selector «Días de».', 'Propuesta en el mockup (unidad, solicitante, gestión económica, Intervención, calendario).', 'Validar el reparto.', 'Falta', 'Media'),
  ('U5', 'Efectivos de la unidad por mes', 'Productividad (anexo del documento funcional).', 'Nada.', 'Nº de personas tramitando cada mes.', 'Falta', 'Baja'),
 ]),
]

r = 6
for grp, rows in ITEMS:
    ws.cell(row=r, column=1, value=grp)
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=len(cols))
    c = ws.cell(row=r, column=1)
    c.font = Font(name=F, size=10, bold=True, color=NAVY)
    c.fill = GRP
    c.border = B
    r += 1
    for it in rows:
        vals = list(it) + ['', '', '', '']
        for ci, v in enumerate(vals, 1):
            cell = ws.cell(row=r, column=ci, value=v)
            cell.font = Font(name=F, size=9, bold=(ci == 2))
            cell.alignment = wrap
            cell.border = B
            if ci >= 8:
                cell.fill = FILL
        ws.cell(row=r, column=7).fill = PRI[it[6]]
        ws.cell(row=r, column=6).font = Font(name=F, size=9, bold=True,
                                             color=('B00020' if it[5] == 'Falta' else 'B26A00'))
        r += 1
widths(ws, [5, 34, 36, 40, 38, 9, 9, 18, 18, 16, 24])
ws.freeze_panes = 'C6'
ws.auto_filter.ref = f'A5:K{r-1}'

# ───────────────────────── Hoja 2: Dudas
ws2 = wb.create_sheet('Dudas a confirmar')
title(ws2, 'Dudas a confirmar con la unidad o con Roberto',
      'Salen de lo visto en Atlantix el 18/11/2026. Afectan a cómo se calculan los indicadores, no a qué datos faltan.')
header(ws2, 4, ['Nº', 'Duda', 'Qué hemos visto', 'Qué afecta', 'A quién', 'Respuesta'])
DUDAS = [
 ('Q1', '¿El cuadro es solo del procedimiento 3163 (Sección de Ayudas Económicas a la Natalidad)?',
  'La aplicación D032 tiene 12 procedimientos. Partos múltiples (3331, 3630) y el 1246 de la DG son de la misma DG.', 'Todo el cuadro (filtro).', 'Unidad / Roberto'),
 ('Q2', '¿Qué fecha cuenta como «resolución» para el plazo y el tiempo E2E?',
  'La favorable parece colectiva y mensual (FCRESOLUCION a las 00:00 y títulos «RESOLUCIÓN FAVORABLE MARZO 2026»); la notificación individual se firma ~1 mes después. En denegaciones, FCRESOLUCION va semanas o meses antes de la firma.',
  'Tiempo E2E, alta → resolución, incumplimiento de plazo.', 'Unidad'),
 ('Q3', '¿Un requerimiento normal se cierra «anulando» la etapa REQUERIMIENTO?',
  '25.400 expedientes con la etapa REQUERIMIENTO anulada en la bitácora frente a 6.001 en la vista de etapas.', 'Requerimientos, reprocesos, tiempos por fase.', 'Unidad / Roberto'),
 ('Q4', '¿Comparamos años por fecha de presentación o por convocatoria?',
  'Muchas solicitudes de 2025 están en la convocatoria 2026 («cambio de convocatoria» en ~4.500 expedientes). La convocatoria 2026 tiene casi el triple que la de 2025.', 'Filtro «Año de solicitud» y comparativa.', 'Unidad'),
 ('Q5', '¿Existen en esta ayuda las etapas «No Fiscalizable Concesión» y «Desfavorable Concesión»?',
  'Están en el mockup, pero no aparecen en los datos del 3163.', 'Fase Intervención y respuesta de la Intervención.', 'Unidad'),
 ('Q6', '¿ID_ENVIO de la bitácora es el nº de lote de envío a la Intervención?',
  'La bitácora graba «Envío a Intervención» con fecha; GSTA_REGISTRO_ACTIVIDAD tiene la columna ID_ENVIO.', 'Envío a la Intervención (nº de lote).', 'Roberto'),
 ('Q7', '¿Los acuses de recibo a las 00:00 son notificaciones en papel?', 'Parte de los acuses llevan hora 00:00:00.', 'Plazo de aportación del requerimiento.', 'Unidad'),
 ('Q8', '¿Vale la nacionalidad aproximada por tipo de documento hasta tener el dato real?', 'Solicitantes: 77 % con NIF, 23 % con NIE.', 'Composición: nacionalidad.', 'Unidad'),
 ('Q9', '¿El estado del expediente y las fechas de cierre y fin de tramitación no se usan en esta ayuda?',
  'DSESTADO es casi siempre «Iniciado» (o «Anulado»); FCCIERRE y FCFINTRAMITACION vacíos.', 'Se usarán las etapas y la resolución, no el estado.', 'Roberto'),
 ('Q10', '¿REF_SOLICITUD (formato de nº de registro de eReg) sirve como clave para unir con eReg?', 'Está en el 99 % de los expedientes.', 'Unión Atlantix ↔ eReg (fase previa).', 'Madrid Digital'),
]
r = 5
for d in DUDAS:
    for ci, v in enumerate(list(d) + [''], 1):
        cell = ws2.cell(row=r, column=ci, value=v)
        cell.font = Font(name=F, size=9, bold=(ci == 2))
        cell.alignment = wrap
        cell.border = B
        if ci == 6:
            cell.fill = FILL
    r += 1
widths(ws2, [5, 44, 56, 34, 16, 30])
ws2.freeze_panes = 'C5'

# ───────────────────────── Hoja 3: Ya disponible
ws3 = wb.create_sheet('Ya disponible')
title(ws3, 'Lo que ya sacamos de Atlantix (modelo de Celonis en borrador)',
      'Pool OCPM, conexión de producción de Atlantix (solo lectura). Filtro: aplicación D032, procedimiento 3163.')
header(ws3, 4, ['Dato', 'Origen en Atlantix', 'En Celonis', 'Para qué en el cuadro', 'Nota'])
YA = [
 ('Expediente, convocatoria (nombre y año), estado, unidad', 'GSTA_V_CEL_EXPEDIENTE, GSTA_V_EXPEDIENTE', 'Objeto NatExpedientes', 'Base de todo; filtros', ''),
 ('Presentación de la solicitud / entrada en eReg (fecha y hora)', 'GSTA_V_CEL_EXPEDIENTE.FC_SOL_INTERESADO (= FC_SOL_EREG en el 99,7 %)', 'Evento NatSolicitudPresentada', 'Tiempo E2E, registro → alta', 'Solo de las que ya tienen expediente'),
 ('Nº de registro de la solicitud', 'REF_SOLICITUD / CD_SOLICITUD', 'NatExpedientes', 'Clave futura con eReg', ''),
 ('Alta del expediente', 'FCINICIO', 'Evento NatExpedienteAbierto', 'Dados de alta, registro → alta', ''),
 ('Etapas con fecha de inicio y fin, y fase del mockup', 'GSTA_V_CEL_ETAPA', 'Objeto NatEtapas; eventos NatEtapaIniciada / NatEtapaFinalizada', 'Tiempo y stock por fase, entradas/salidas, explorador', 'La vista no trae las etapas anuladas'),
 ('Respuesta de la Intervención', 'Etapas FAVORABLE CONCESIÓN, FAVORABLE CON OBS, ACTUACIÓN INTERESADA, DEV. A INSTANCIA', 'NatEtapas / eventos de etapa', 'Composición; fase Intervención', ''),
 ('Bitácora: anulaciones de etapa, hitos, envío a la Intervención, cambios de unidad, documentos requeridos, consultas ICDA, cambio de convocatoria', 'GSTA_V_CEL_ACTIVIDAD', 'Evento NatActividadRealizada', 'Reprocesos, requerimientos, Intervención, expedientes sin actividad (última actuación)', 'La descripción puede llevar DNI: no mostrarla'),
 ('Notificaciones: envío y acuse, tipo (requerimiento, resolución…)', 'GSTA_V_CEL_NOTIFICACION', 'Evento NatNotificaciones', 'Requerimientos y plazo de aportación', ''),
 ('Resolución: sentido (favorable, denegación, desistimiento) y fecha de firma', 'GSTA_V_CEL_DOC_ELABORADA + FCRESOLUCION', 'Evento NatExpedienteResuelto', 'Resueltos, denegados o desistidos, favorables; Composición', 'Ver duda Q2 sobre la fecha'),
 ('Anulación del expediente', 'FCANULACION', 'Evento NatExpedienteAnulado', 'Limpieza del embudo', ''),
 ('Solicitante: municipio y provincia de residencia, representante, medio de notificación', 'GSTA_V_INTERESADOS', 'Objeto NatInteresados', 'Composición: municipio', 'Sin nombre, documento, contacto ni domicilio'),
]
r = 5
for y in YA:
    for ci, v in enumerate(y, 1):
        cell = ws3.cell(row=r, column=ci, value=v)
        cell.font = Font(name=F, size=9, bold=(ci == 1))
        cell.alignment = wrap
        cell.border = B
    r += 1
widths(ws3, [44, 44, 34, 38, 30])
ws3.freeze_panes = 'B5'

for w in (ws, ws2, ws3):
    w.sheet_view.zoomScale = 90
    w.page_setup.orientation = 'landscape'
    w.page_setup.fitToWidth = 1
    w.sheet_properties.pageSetUpPr.fitToPage = True
    w.page_setup.fitToHeight = 0

wb.save(out)
print('ok', sum(len(g[1]) for g in ITEMS), 'datos;', len(DUDAS), 'dudas;', len(YA), 'disponibles')
