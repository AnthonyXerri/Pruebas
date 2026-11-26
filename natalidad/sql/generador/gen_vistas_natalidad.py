# Genera VistasNatalidadv1.sql (con comentarios) y VistasNatalidadv1_sin_comentarios.sql (26/11/2026).
# Fuente: respuesta de Soluciones «Nombre de tabla-campo de bd Natalidad» (24/11/2026), tablas D032_3163_*.
# Solo estructura: nombres de tablas y columnas. Ningún dato.
# Uso: python -I gen_vistas_natalidad.py <salida_con_comentarios.sql> <salida_sin_comentarios.sql>
import sys, re

ROL = '&&ROL_CELONIS'          # rol con el que lee Celonis en Atlantix: por confirmar con Madrid Digital
PRE = 'D032_V_NAT_'            # vista = D032_V_NAT_ + tabla sin el prefijo D032_3163_

# Vistas de datos: (tabla, uso, [(columna, comentario)], ojo {columna: motivo})
# Solo columnas que nombra el documento de Soluciones. Nada que identifique a la persona.
DATOS = [
 ('D032_3163_SOL_EXP', 'expediente: tipo de solicitud, hijos, propuesta favorable, importe, nacimiento del menor y baja', [
    ('ID_SOL_EXP',        'clave de la solicitud-expediente (une con hijos, denegaciones, modificaciones y solicitante)'),
    ('NUM_EXPEDIENTE',    'número de expediente de Atlantix (une con GSTA_V_CEL_EXPEDIENTE.CDEXPEDIENTE, por confirmar)'),
    ('ID_TIPO_SOL',       'tipo de solicitud (catálogo D032_3163_CAT_TIPOS_SOL)'),
    ('NUM_HIJOS',         'número de hijos'),
    ('FC_PRO_FAVORABLE',  'fecha de la propuesta favorable = inicio del pago'),
    ('NM_TOTAL_CUANTIA',  'importe total propuesto'),
    ('FC_NACIMIENTO',     'fecha de nacimiento del menor o de parto previsto'),
    ('FC_RESOL_BAJA',     'fecha de resolución de la baja'),
  ], {'FC_NACIMIENTO': 'fecha de nacimiento del menor (fin del derecho a los 2 años)'}),
 ('D032_3163_EXP_HIJOS', 'hijos del expediente y fin del pago', [
    ('ID_EXP_HIJO',       'clave del hijo (une con el calendario de pagos)'),
    ('ID_SOL_EXP',        'expediente'),
    ('FC_FIN_PAGO',       'fin del pago = última nómina'),
  ], {}),
 ('D032_3163_CALENDARIO_PAGOS', 'pagos por mes de cada hijo', [
    ('ID_EXP_HIJO',       'hijo (y por él, el expediente)'),
    ('NM_ANO',            'año'),
    ('NM_MES',            'mes'),
    ('NM_IMPORTE',        'importe mensual'),
    ('FC_PAGO',           'fecha de pago'),
  ], {}),
 ('D032_3163_EXP_DES_DEN', 'motivos de denegación o desistimiento del expediente', [
    ('ID_SOL_EXP',        'expediente'),
    ('ID_DES_DEN',        'motivo (catálogo D032_3163_CAT_DES_DEN)'),
  ], {}),
 ('D032_3163_PROPUESTA_MOD_EXP', 'modificaciones del expediente; las bajas son los tipos 8, 9, 10, 11 y 14', [
    ('ID_SOL_EXP',        'expediente'),
    ('ID_MOD_EXP_ACTIVA', 'tipo de modificación (catálogo D032_3163_CAT_TIPOS_MOD_EXP.ID_PARAM_MOD_EXP)'),
    ('FC_BAJA',           'fecha de efecto de la baja'),
    ('BL_DESHECHA',       'modificación deshecha (para una baja válida: N)'),
    ('BL_MODI_TERMINADA', 'modificación terminada (para una baja válida: S)'),
    ('BL_RECEPCIONADO',   'recepcionada (para una baja válida: S)'),
  ], {}),
 ('D032_3163_EXP_SOLICIT_BENEFIC', 'datos de la solicitante para la composición', [
    ('ID_SOL_EXP',             'expediente'),
    ('CD_NACIONALIDAD',        'nacionalidad (SUCA_PAIS)'),
    ('CD_NACIONALIDAD_ORIGEN', 'nacionalidad de origen (SUCA_PAIS)'),
    ('CD_PROVINCIA_RESI',      'provincia de residencia (SUCA_PROVINCIA)'),
    ('CD_MUNICIPIO_RESI',      'municipio de residencia (SUCA_MUNICIPIO)'),
    ('CD_PAIS_RESI',           'país de residencia (SUCA_PAIS)'),
    ('FC_NACIMIENTO',          'fecha de nacimiento de la solicitante (para la edad en tramos)'),
  ], {'CD_NACIONALIDAD': 'nacionalidad', 'CD_NACIONALIDAD_ORIGEN': 'nacionalidad',
      'FC_NACIMIENTO': 'fecha de nacimiento (solo para la edad en tramos)'}),
]
# Fuera a propósito (texto libre que puede llevar datos personales; el motivo sale del tipo de modificación):
FUERA = {'D032_3163_PROPUESTA_MOD_EXP': 'DS_OBSERVACIONES y DS_MOTIVO_BAJA (texto libre): el motivo de la baja '
                                         'sale del tipo de modificación (catálogo). Se pueden añadir si la unidad lo pide.'}

# Catálogos: código y descripción, con lista de columnas (así no entran columnas de auditoría con logins).
CATALOGOS = [
 ('D032_3163_CAT_TIPOS_SOL',     'tipos de solicitud', ['ID_TIPO_SOL', 'DS_TIPO_SOL']),
 ('D032_3163_CAT_DES_DEN',       'motivos de denegación', ['ID_DES_DEN', 'DS_CASUISTICA']),
 ('D032_3163_CAT_TIPOS_MOD_EXP', 'tipos de modificación; las bajas son 8, 9, 10, 11 y 14', ['ID_PARAM_MOD_EXP', 'DS_NOMBRE_PARAM']),
]
# Los catálogos SUCA (PAIS, PROVINCIA, MUNICIPIO) no se crean aquí: SUCA_PAIS ya está en la conexión de Atlantix
# de Celonis, y una vista sobre tablas de otro propietario no se puede dar a otro rol sin WITH GRANT OPTION.

TABLAS = [t for t, *_ in DATOS] + [t for t, *_ in CATALOGOS]
vista = lambda t: PRE + (t[len('D032_3163_'):] if t.startswith('D032_3163_') else t)

# ── Comprobaciones antes de escribir nada ──
NOMBRES = [vista(t) for t in TABLAS]
assert len(set(NOMBRES)) == len(NOMBRES), 'nombres de vista repetidos'
for n in NOMBRES: assert len(n) <= 30, f'{n} pasa de 30 caracteres'
PERSONALES = re.compile(r'NOMBRE|APELL|DNI|NIF|NIE|CIF|DOCUMENTO|TELEF|MOVIL|EMAIL|CORREO|DOMICILIO|DIRECC|VIA$|IBAN|CUENTA|OBSERV|DS_MOTIVO')
for t, _, cols, ojo in DATOS:
    nombres = [c for c, _ in cols]
    assert len(set(nombres)) == len(nombres), f'columna repetida en {t}'
    for c in nombres: assert not PERSONALES.search(c), f'{t}.{c} parece un dato personal'
    for c in ojo: assert c in nombres, f'«Ojo» de {t}.{c} sin columna'
CLAVE = {'D032_3163_SOL_EXP': ['ID_SOL_EXP', 'NUM_EXPEDIENTE'], 'D032_3163_EXP_HIJOS': ['ID_EXP_HIJO', 'ID_SOL_EXP'],
         'D032_3163_CALENDARIO_PAGOS': ['ID_EXP_HIJO'], 'D032_3163_EXP_DES_DEN': ['ID_SOL_EXP', 'ID_DES_DEN'],
         'D032_3163_PROPUESTA_MOD_EXP': ['ID_SOL_EXP', 'ID_MOD_EXP_ACTIVA'], 'D032_3163_EXP_SOLICIT_BENEFIC': ['ID_SOL_EXP']}
for t, _, cols, _ in DATOS:
    for k in CLAVE[t]: assert k in [c for c, _ in cols], f'falta la clave {k} en {t}'

# ── Escritura ──
L = []
w = L.append
def bloque(titulo):
    w('-' * 76); w(f'-- {titulo}'); w('-' * 76); w('')

w('-' * 76)
w('-- Vistas de Atlantix para Celonis · Minería de procesos de Natalidad (D032 · 3163)')
w('-- VistasNatalidadv1 · 26/11/2026')
w('--')
w('-- Tablas y campos indicados por Soluciones el 24/11/2026 («Nombre de tabla-campo')
w('-- de bd Natalidad»). Todas las tablas D032_3163_* son solo del procedimiento 3163.')
w('--')
w('-- El script tiene 4 bloques:')
w('--   0. Comprobación previa: columnas de las tablas (solo nombres y tipos).')
w(f'--   1. {len(DATOS)} vistas de datos, con lista de columnas.')
w(f'--   2. {len(CATALOGOS)} vistas de catálogos (código y descripción).')
w('--   3. Comprobación final: vistas compiladas y permisos.')
w('--')
w('-- Criterio: solo las columnas que pide el cuadro y las claves para unir las')
w('-- tablas. Nada que identifique a la persona (nombre, documento, contacto,')
w('-- dirección, cuenta) ni texto libre. Lo sensible que se deja va marcado «Ojo».')
w('--')
w('-- Antes de ejecutar:')
w('--   * Ejecutar como script (F5 en SQL Developer) con el usuario propietario de')
w('--     las tablas D032_3163_*.')
w('--   * Poner en DEFINE el rol con el que lee Celonis en Atlantix (el mismo que')
w('--     tiene permiso sobre las vistas GSTA_V_CEL_*). Por confirmar.')
w('--')
w('-- En Celonis: añadir las vistas a la extracción de la conexión de Atlantix')
w('-- (PRATLX_RO).')
w('-' * 76)
w('')
w(f"DEFINE ROL_CELONIS = 'ROL_POR_CONFIRMAR'")
w('')

bloque('BLOQUE 0 · Comprobación previa (solo estructura, ningún dato)')
w('-- Si alguna columna de las vistas no aparece aquí, avisar antes de crear nada.')
w('SELECT owner, table_name, column_id, column_name, data_type, data_length')
w('FROM all_tab_columns')
w('WHERE table_name IN (')
w(',\n'.join(f"    '{t}'" for t in TABLAS))
w(')')
w('ORDER BY table_name, column_id;')
w('')

bloque(f'BLOQUE 1 · {len(DATOS)} vistas de datos, con lista de columnas')
for t, uso, cols, ojo in DATOS:
    v = vista(t)
    w(f'--{t}')
    w(f'-- Uso: {uso}.')
    if t in FUERA: w(f'-- Fuera: {FUERA[t]}')
    w('')
    w(f'CREATE OR REPLACE VIEW {v} AS')
    w('SELECT')
    ancho = max(len(c) for c, _ in cols) + 1
    for i, (c, com) in enumerate(cols):
        coma = ',' if i < len(cols) - 1 else ''
        nota = f'Ojo: {ojo[c]}' if c in ojo else com
        w(f'    {(c + coma).ljust(ancho)}  -- {nota}')
    w(f'FROM {t};')
    w('')
    w(f'GRANT SELECT ON {v} TO {ROL};')
    w(f'CREATE OR REPLACE PUBLIC SYNONYM {v} FOR {v};')
    w('')

bloque(f'BLOQUE 2 · {len(CATALOGOS)} vistas de catálogos (código y descripción)')
for t, uso, cols in CATALOGOS:
    v = vista(t)
    w(f'--{t}')
    w(f'-- Uso: {uso}.')
    w('')
    w(f'CREATE OR REPLACE VIEW {v} AS')
    w('SELECT')
    w(',\n'.join(f'    {c}' for c in cols))
    w(f'FROM {t};')
    w('')
    w(f'GRANT SELECT ON {v} TO {ROL};')
    w(f'CREATE OR REPLACE PUBLIC SYNONYM {v} FOR {v};')
    w('')

bloque('BLOQUE 3 · Comprobación final')
w(f'-- Todas las vistas deben salir con STATUS = VALID ({len(TABLAS)}).')
w('SELECT object_name, status')
w('FROM user_objects')
w(f"WHERE object_type = 'VIEW' AND object_name LIKE '{PRE.replace('_', chr(92) + '_')}%' ESCAPE '{chr(92)}'")
w('ORDER BY object_name;')
w('')
w('-- Permisos de lectura del rol que usa Celonis.')
w('SELECT table_name, privilege')
w('FROM user_tab_privs_made')
w(f"WHERE grantee = '{ROL}' AND table_name LIKE '{PRE.replace('_', chr(92) + '_')}%' ESCAPE '{chr(92)}'")
w('ORDER BY table_name;')
w('')
w('-' * 76)
w('-- PENDIENTE')
w('--   * Expediente revisado (marca y fecha): los campos aún no existen (petición')
w('--     FARO del 24/11/2026). Se añaden a la vista de SOL_EXP cuando estén.')
w('--   * Rol de Celonis en Atlantix (ROL_CELONIS): por confirmar.')
w('--   * Clave de cada fila del calendario de pagos y de las modificaciones: si')
w('--     tienen un identificador propio, añadirlo a sus vistas.')
w('--   * EXP_SOLICIT_BENEFIC: confirmar si hay una fila por expediente (la')
w('--     solicitante) o también otras personas; si hay columna de tipo, añadirla.')
w('--   * Nombres de provincia y municipio: salen de GSTA_V_INTERESADOS o de')
w('--     SUCA_PROVINCIA y SUCA_MUNICIPIO, si el rol de Celonis los puede leer.')
w('-' * 76)

con = '\n'.join(L) + '\n'

# versión sin comentarios: fuera todo lo que va tras «--» (fuera de comillas) y líneas vacías de más
def sin_comentarios(txt):
    out, blank = [], False
    for line in txt.split('\n'):
        res, q = [], False
        for i, ch in enumerate(line):
            if ch == "'": q = not q
            if not q and line.startswith('--', i): break
            res.append(ch)
        l = ''.join(res).rstrip()
        if not l:
            if out and not blank: out.append('')
            blank = True
        else:
            out.append(l); blank = False
    while out and not out[-1]: out.pop()
    return '\n'.join(out) + '\n'

sin = sin_comentarios(con)
assert '--' not in sin
for path, txt in zip(sys.argv[1:3], (con, sin)):
    open(path, 'w', encoding='utf-8', newline='\r\n').write(txt)
print('ok', len(DATOS), 'vistas de datos,', len(CATALOGOS), 'catálogos')
