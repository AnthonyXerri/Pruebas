# Genera VistasSIDMPRODv3.sql (24/11/2026).
# Parte de las 26 tablas de gen_vistas_v2.py (columnas leídas en Celonis y comprobadas contra SIDEMA)
# y aplica los cambios de v3. Solo estructura: nombres de tablas y columnas. Ningún dato.
# Uso: python -I gen_vistas_v3.py <v1.sql> <salida1.sql> [<salida2.sql> ...]
import sys, re, pathlib

AQUI = pathlib.Path(__file__).parent
V1 = pathlib.Path(sys.argv[1])
OUT = [pathlib.Path(p) for p in sys.argv[2:]]

# 1. Tablas de v2 (orden de columnas de la tabla y motivo de exclusión) -------------------------
src = (AQUI / 'gen_vistas_v2.py').read_text(encoding='utf-8')
ns = {}
exec(src[src.index('MOTIVO = {'):src.index('# Comprobaciones')], ns)
MOTIVO = ns['MOTIVO']
MOTIVO['R'] = 'repetido en otra columna que sí va'
T = [(tabla, uso, cols, dict(fuera)) for tabla, uso, cols, fuera in ns['T']]
NCOLS = dict(re.findall(r"'(S(?:IDM|UCA)_[A-Z_]+)': (\d+)", src[src.index('NCOLS'):src.index('for tabla')]))

# 2. Cambios de v3 ------------------------------------------------------------------------------
# 2a. Columnas que vuelven a entrar porque explican el proceso (segmentar, variantes, causas).
ENTRAN = {
    'SIDM_SOLICITANTE': 'CDNACION CDNACION_DOS CDECIVIL ITSSOCIAL ITTIBE ITAUT_CONS_DATOS ITOTROS '
                        'NMREGISTRO_CENTRO FCACT_FALLEC_INE',
    'SIDM_MR_RESOLUCIONES': 'IT_ELA',
    'SIDM_DICTAMEN': 'DSPUNTUACION NMBAREMO_MAYOR',
    'SIDM_DICTAMEN_TECNICO': 'NMBAREMO',
    'SIDM_VALORACION_BVD': 'NMBAREMO_COGNITIVO NMBAREMO_FISICO',
    'SIDM_VALORACION_EVE': 'NMPUNT_DESARROLLO NMPUNT_SALUD',
    'SIDM_RI_CE_GENERAL': 'IT_TP_DECLARACION IT_TP_CONTRIBUYENTE NM_CAPECON_RES_CONJ',
    'SIDM_RI_TRASLADO_IN': 'DS_MOT_RECHAZO DS_MUNI_ORIGEN CODIGOEXT_TRASLADO CODIGOEXT_EXP CODIGOEXT_CV '
                           'CODIGO_EXPEDIENTE',
    'SIDM_RI_TRASLADO_OUT': 'DS_MOTIVO DS_MOT_RECHAZO CD_MUNI DS_MUNI',
    'SIDM_DATOS_VALORADOR': 'NOMBRE_VALORADOR',
}
# 2b. El nombre del valorador va entero en NOMBRE_VALORADOR: las partes sueltas sobran.
REPETIDAS = {'SIDM_DATOS_VALORADOR': 'DSNOMBRE DSAPELLIDO1 DSAPELLIDO2'}

# 2c. Datos sensibles que SÍ se dejan: van señalados en la vista para que el DBA los vea.
OJO = {
    'SIDM_SOLICITANTE': {'FCNACIMIENTO': 'edad', 'FCFALLEC_INE': 'fallecidos durante la tramitación',
                         'FCACT_FALLEC_INE': 'fallecidos durante la tramitación', 'CDNACION': 'nacionalidad',
                         'CDNACION_DOS': 'nacionalidad', 'CDECIVIL': 'estado civil'},
    'SIDM_DATOS_VALORADOR': {'NOMBRE_VALORADOR': 'nombre del empleado (el mockup lo muestra)',
                             'LOGIN': 'login del empleado'},
    'SIDM_SUBSANACION_DOCUMENTACION': {'DSTEXTO_LIBRE': 'texto libre (motivo de la subsanación)'},
    'SIDM_RI_PIA': {'DS_MOT_ESTADO_WEB_EL': 'texto libre (motivo de la baja en la web de EELL)'},
    'SIDM_RI_TRASLADO_IN': {'DS_MOT_RECHAZO': 'texto libre (motivo del rechazo)'},
    'SIDM_RI_TRASLADO_OUT': {'DS_MOTIVO': 'texto libre (motivo del traslado)',
                             'DS_MOT_RECHAZO': 'texto libre (motivo del rechazo)'},
    'SIDM_MR_RESOLUCIONES': {'IT_ELA': 'salud (vía rápida ELA)'},
    'SIDM_DICTAMEN': {'DSPUNTUACION': 'salud (puntuación)', 'NMBAREMO_MAYOR': 'salud (puntuación)'},
    'SIDM_DICTAMEN_TECNICO': {'NMBAREMO': 'salud (puntuación)'},
    'SIDM_VALORACION_BVD': {'NMBAREMO_COGNITIVO': 'salud (puntuación)', 'NMBAREMO_FISICO': 'salud (puntuación)'},
    'SIDM_VALORACION_EVE': {'NMPUNT_DESARROLLO': 'salud (puntuación)', 'NMPUNT_SALUD': 'salud (puntuación)'},
    'SIDM_RI_CE_GENERAL': {'NM_CAPACIDAD_ECON': 'económico (prelación del CU2)',
                           'NM_CAPACIDAD_ECON_RES': 'económico', 'NM_CAPECON_RES_CONJ': 'económico'},
}
USO_V3 = {
    'SIDM_SOLICITANTE': 'CU1 y CU2: edad, sexo, nacionalidad, estado civil y territorio (CDPROV + CDMUNI con SUCA, '
                        'distrito y zona); fallecimiento.',
    'SIDM_RI_TRASLADO_OUT': 'CU1 y CU2: traslados a otra comunidad (bandeja TRASOUT): destino y motivo.',
    'SIDM_DATOS_VALORADOR': 'CU1 fase 2: valoradores (nombre, perfil, turno, profesión, zona, encomienda) y LOGIN '
                            'para cruzar con IDMODI.',
}

T3 = []
for tabla, uso, cols, fuera in T:
    for c in ENTRAN.get(tabla, '').split():
        assert c in fuera, f'{tabla}.{c} no estaba fuera'
        del fuera[c]
    for c in REPETIDAS.get(tabla, '').split():
        assert c in fuera, f'{tabla}.{c} no estaba fuera'
        fuera[c] = 'R'
    ojo = OJO.get(tabla, {})
    assert not set(ojo) - set(cols), f'{tabla}: ojo con columnas que no existen'
    assert not set(ojo) & set(fuera), f'{tabla}: ojo con columnas que van fuera'
    assert len(cols) == len(set(cols)) == int(NCOLS[tabla]), tabla
    T3.append((tabla, USO_V3.get(tabla, uso), cols, fuera, ojo))

# 3. Catálogos encontrados el 24/11 en el origen (sin ver sus columnas: SELECT *) ---------------
# (tabla, qué código explica)
CATALOGOS = [
    ('SIDM_ESTADO_CITA', 'estados de la citación de la valoración (fase 2).'),
    ('SIDM_ESTADO_ENVIO', 'CDESTADOENVIOFINAL de SIDM_RI_TRASLADO_OUT (por confirmar).'),
    ('SIDM_ESTADO_GEST_VAL', 'CDESTADO_GEST_VAL de SIDM_ESTADO_SOLICITUD.'),
    ('SIDM_ESTADO_SUBSANACION', 'CDESTADO_DOCUMENTACION de SIDM_SUBSANACION_DOCUMENTACION (por confirmar).'),
    ('SIDM_GRUPO_PIA', 'CD_GRUPO de SIDM_RI_PIA y SIDM_RI_TRAMITES (por confirmar; ver también SIDM_RI_GRUPO).'),
    ('SIDM_LE_ESTADOINC', 'CU2: estados de las incidencias de la lista de espera.'),
    ('SIDM_LE_TP_INC', 'CU2: tipos de incidencia de la lista de espera (demora atribuible al usuario...).'),
    ('SIDM_MANCOMUNIDAD', 'CD_MANCO de SIDM_RI_URGENCIA; filtro de territorio (por confirmar).'),
    ('SIDM_PERFIL_VALORADOR', 'CDPERFIL_VALORADOR de SIDM_DATOS_VALORADOR.'),
    ('SIDM_RE_DEMAR_ZONADEP', 'CDZONADEP de SIDM_SOLICITANTE y SIDM_DATOS_VALORADOR (por confirmar).'),
    ('SIDM_RI_CE_MOTREVISION', 'CD_MOT_REVISION de SIDM_RI_CE_GENERAL.'),
    ('SIDM_RI_CE_TPMOTREVISION', 'CD_TPMOTREVISION de SIDM_RI_CE_GENERAL.'),
    ('SIDM_RI_ESTADOS_CE', 'CD_ESTADO_CE de SIDM_RI_CE_GENERAL.'),
    ('SIDM_RI_ESTADOS_SERV', 'CU2: estados del servicio (SAD y Teleasistencia) (por confirmar).'),
    ('SIDM_RI_GRUPO', 'CD_GRUPO del PIA (por confirmar; ver también SIDM_GRUPO_PIA).'),
    ('SIDM_RI_MOT_APROB_REV', 'CD_MOT_APROB_REV de SIDM_RI_SOL_REVISION_PIA.'),
    ('SIDM_RI_MOT_APROB_URGENCIA', 'CD_MOT_APROBACION de SIDM_RI_URGENCIA.'),
    ('SIDM_RI_MOT_BAJA_SERV', 'CU2: motivos de baja del servicio (motivos de exclusión del mockup).'),
    ('SIDM_RI_MOT_NOADJUDICA', 'CU2: motivos de no adjudicación del servicio.'),
    ('SIDM_RI_MOT_RECHAZ_REV', 'CD_MOT_RECHAZ_REV de SIDM_RI_SOL_REVISION_PIA.'),
    ('SIDM_RI_MOT_RECHAZO_URGENCIA', 'CD_MOT_RECHAZO de SIDM_RI_URGENCIA.'),
    ('SIDM_RI_MOT_RESOLUCION', 'CD_MOT_RESOL de SIDM_RI_PIA (por confirmar).'),
    ('SIDM_RI_MOT_REVISION', 'CD_MOT_REVISION de SIDM_RI_SOL_REVISION_PIA.'),
    ('SIDM_RI_TPOFICIOS', 'CU2: CD_TPOFICIO de SIDM_RI_DOC_GENERADO (notificación de la resolución del PIA).'),
    ('SUCA_AREA_SER_SOC', 'áreas de servicios sociales (filtro de territorio).'),
    ('SUCA_DISTRITO', 'CDDISTRITO de SIDM_SOLICITANTE (distritos de Madrid capital) (por confirmar).'),
    ('SUCA_DISTRITO_SER_SOC', 'distritos de servicios sociales (filtro de territorio).'),
    ('SUCA_ZONA_SER_SOC', 'zonas de servicios sociales (filtro de territorio).'),
]

# 4. Tablas del CU2 y de la citación: existen en el origen, pero hay que ver sus columnas antes ---
PEND_COLUMNAS = [
    ('SIDM_RI_SAD', 'CU2: servicio de ayuda a domicilio por PIA (alta en la lista: FC_INCLUSION_LAU).'),
    ('SIDM_RI_SAD_HIST', 'CU2: histórico del SAD (eventos de la lista de espera).'),
    ('SIDM_RI_TA', 'CU2: teleasistencia por PIA (alta en la lista: FC_INCLUSION_LAU).'),
    ('SIDM_RI_TA_HIST', 'CU2: histórico de la teleasistencia.'),
    ('SIDM_RI_DOC_GENERADO', 'CU2: documentos del PIA (notificación de la resolución: FC_ENV_NOTIFICACION).'),
    ('SIDM_V_RI_WEBEL_ALTAS_SAD', 'CU2: lista de espera de SAD (web de entidades locales).'),
    ('SIDM_V_RI_WEBEL_ALTAS_TA', 'CU2: lista de espera de teleasistencia.'),
    ('SIDM_V_RI_WEBEL_BAJAS_SAD', 'CU2: bajas del SAD (origen y fecha de efectos).'),
    ('SIDM_V_RI_WEBEL_BAJAS_TA', 'CU2: bajas de la teleasistencia.'),
    ('SIDM_V_RI_WEBEL_MODI_SAD', 'CU2: modificaciones del SAD.'),
    ('SIDM_V_RI_WEBEL_MODI_TA', 'CU2: modificaciones de la teleasistencia.'),
    ('SIDM_LE_INCIDENCIAS', 'CU2: incidencias de la lista de espera (hospitalización, ausencia...).'),
    ('SIDM_LE_RENUNCIA', 'CU2: renuncias a la lista de espera.'),
    ('SIDM_LE_BAJA_ACEPTADA_SAD', 'CU2: bajas aceptadas de la lista de SAD.'),
    ('SIDM_LE_BAJA_ACEPTADA_TEL', 'CU2: bajas aceptadas de la lista de teleasistencia.'),
    ('SIDM_CITAS', 'CU1 fase 2: citaciones de valoración (fecha de cita).'),
    ('SIDM_CITA_VALORADOR', 'CU1 fase 2: asignación de la cita al valorador («sin asignar»).'),
]

# 5. Texto del script ---------------------------------------------------------------------------
def vista(tabla):
    return 'SIDM_V_DEP_' + (tabla[5:] if tabla.startswith('SIDM_') else tabla)

def partir(linea, sangria='--     '):
    out = []
    while len(linea) > 110:
        corte = linea.rfind(', ', 0, 110)
        if corte < 0:
            corte = linea.rfind(' ', 0, 110) - 1
        out.append(linea[:corte + 1])
        linea = sangria + linea[corte + 2:]
    return out + [linea]

def cola(v):
    return [f'GRANT SELECT ON {v} TO ROLE_SIDM_EXT_PMCP;', f'CREATE OR REPLACE PUBLIC SYNONYM {v} FOR {v};']

def bloque(tabla, uso, cols, fuera, ojo):
    dentro = [c for c in cols if c not in fuera]
    v = vista(tabla)
    L = [f'--{tabla}'] + partir(f'-- Uso: {uso}', '--      ') + [f'-- Columnas: {len(dentro)} de {len(cols)}.']
    if fuera:
        grupos = {}
        for c in cols:
            if c in fuera:
                grupos.setdefault(fuera[c], []).append(c)
        L.append('-- Fuera:')
        for m, cs in grupos.items():
            L += partir(f"--   {MOTIVO[m]}: {', '.join(cs)}")
    if ojo:
        L.append('-- Ojo, se dejan estos datos sensibles:')
        for c in dentro:
            if c in ojo:
                L.append(f'--   {c}: {ojo[c]}')
    if tabla.startswith('SUCA_'):
        L.append('-- Nota DBA: tabla del esquema SUCA; el propietario de la vista necesita SELECT WITH GRANT OPTION sobre ella.')
    L += [f'CREATE OR REPLACE VIEW {v} AS', 'SELECT']
    L += [f'    {c}{"," if i < len(dentro) - 1 else ""}' for i, c in enumerate(dentro)]
    L.append(f'FROM {tabla};')
    return '\n'.join(L + cola(v)), len(dentro), len(cols)

def bloque_catalogo(tabla, uso):
    v = vista(tabla)
    L = [f'--{tabla}'] + partir(f'-- Catálogo: {uso}', '--           ')
    if tabla.startswith('SUCA_'):
        L.append('-- Nota DBA: tabla del esquema SUCA; el propietario de la vista necesita SELECT WITH GRANT OPTION sobre ella.')
    L += [f'CREATE OR REPLACE VIEW {v} AS', f'SELECT * FROM {tabla};']
    return '\n'.join(L + cola(v))

# Las 3 vistas de v1 con lista de columnas: mismas columnas; solo cambia DROP + CREATE por CREATE OR REPLACE
v1 = V1.read_text(encoding='utf-8').replace('\r\n', '\n')
cabeza = v1[:v1.index('--SIDM_BANDEJA_RECEPCIONADOS')].rstrip()
cabeza = re.sub(r'^-{20,}\s*\n', '', cabeza)
cabeza = re.sub(r'DROP VIEW (\w+);?\s*\n\s*\n?CREATE VIEW \1 AS *', r'CREATE OR REPLACE VIEW \1 AS', cabeza)
cabeza = re.sub(r' +\n', '\n', cabeza).replace('PUBLIC SYNONYM  ', 'PUBLIC SYNONYM ').replace('SELECT \n', 'SELECT\n')
assert cabeza.count('CREATE OR REPLACE VIEW') == 3 and 'DROP VIEW' not in cabeza
USO_V1 = {
    '--SIDM_ESTADO_SOLICITUD\n': '-- Uso: CU1, catálogo de estados de la solicitud. Igual que en v1.\n',
    '--SIDM_HIST_ESTADO\n': '-- Uso: CU1, histórico de estados de la solicitud (eventos). Igual que en v1.\n',
    '--SIDM_SOLICITUD\n': '-- Uso: CU1 y CU2, la solicitud (objeto del proceso). Igual que en v1.\n',
}
for k, u in USO_V1.items():
    assert k in cabeza
    cabeza = cabeza.replace(k, k + u, 1)
cabeza = re.sub(r'\n{3,}', '\n\n', cabeza)

CABECERA = """----------------------------------------------------------------------------
-- Vistas de SIDEMA para Celonis · Minería de procesos de Dependencia (CU1 y CU2)
-- VistasSIDMPRODv3 · 24/11/2026 · sobre VistasSIDMPRODv1
--
-- El script tiene 4 bloques:
--   1. Las 29 vistas de v1 (mismas tablas), con lista de columnas.
--   2. 28 catálogos nuevos que existen en SIDEMA y explican códigos de las
--      tablas del bloque 1 o del CU2.
--   3. Consulta al diccionario (solo nombres y tipos de columna) de las tablas
--      del CU2 y de la citación, para preparar sus vistas en la v4.
--   4. Comprobación final: las vistas compiladas y sus permisos.
--
-- Cambios frente a v1:
--  * CREATE OR REPLACE VIEW en lugar de DROP VIEW + CREATE VIEW: la primera
--    vez no da error por no existir la vista y se conservan sus permisos.
--  * Cada vista lleva su lista de columnas: se deja todo lo que sirve para el
--    proceso (claves, códigos, fechas, indicadores, logins, motivos,
--    puntuaciones, nacionalidad, estado civil...).
--  * Se quita solo lo que identifica a la persona o no aporta al análisis:
--    nombre, documento, teléfono, correo, dirección completa, cuenta bancaria,
--    observaciones libres, cuestionario de salud EVE, renta y patrimonio, y
--    los ficheros guardados dentro de las tablas (PDF, plantillas, LOB), que
--    además hacen muy lenta la extracción.
--  * Lo sensible que se deja va marcado con «Ojo» en cada vista.
--  * Las 3 primeras vistas (estado, histórico y solicitud) tienen las mismas
--    columnas que en v1.
--
-- Columnas comprobadas el 24/11/2026 contra DBA_SIDM y DBA_SUCA en el entorno
-- de validación (VASOCIAL), desde la extracción «Extraccion Dependencia».
--
-- En Celonis: al cambiar la extracción a estas vistas, marcar «Rename target
-- table» con el nombre de siempre (SIDM_SOLICITUD...), para que no cambien
-- las tablas de Objects & Events.
----------------------------------------------------------------------------
"""

SEP = '\n\n----------------------------------------------------------------------------\n-- {}\n----------------------------------------------------------------------------'

nombres = ',\n'.join(f"    '{t}'" for t, _ in PEND_COLUMNAS)
lista_pend = '\n'.join(f'--   {t:<28} {u}' for t, u in PEND_COLUMNAS)
DICCIONARIO = f"""
-- Estas tablas existen en SIDEMA (aparecen como sinónimo público), pero el
-- usuario con el que se conecta Celonis no puede leerlas, así que no se ven
-- sus columnas. Pueden llevar datos personales, por eso no se crean con
-- SELECT *.
-- Esta consulta devuelve solo nombres y tipos de columna, ningún dato. Con el
-- resultado se preparan sus vistas en la v4, con el mismo criterio.
{lista_pend}
SELECT owner, table_name, column_id, column_name, data_type, data_length
FROM all_tab_columns
WHERE table_name IN (
{nombres}
)
ORDER BY table_name, column_id;"""

COMPROBACION = """
-- Todas las vistas deben salir con STATUS = VALID.
SELECT object_name, status
FROM user_objects
WHERE object_type = 'VIEW' AND object_name LIKE 'SIDM_V_DEP_%'
ORDER BY object_name;

-- Permisos de lectura del rol que usa Celonis.
SELECT table_name, privilege
FROM user_tab_privs_made
WHERE grantee = 'ROLE_SIDM_EXT_PMCP' AND table_name LIKE 'SIDM_V_DEP_%'
ORDER BY table_name;"""

PIE = """

----------------------------------------------------------------------------
-- SIGUE FALTANDO (no se ha encontrado en SIDEMA o hay que confirmarlo)
--   * Lote del servicio (SAD y teleasistencia): municipio -> lote del contrato.
--   * Usuarios: nombre, tipo (propio, subcontrata, empresa externa), equipo y
--     sede de quien graba, subsana y tramita el PIA (en las tablas solo hay
--     login). Candidatas por el nombre: SIDM_VM_HSTA_USU_PROFESIONALES,
--     SIDM_VM_HSTA_USUARIOS.
--   * Municipio -> mancomunidad: candidatas ECSS_MANCOMUNICIPIOS y
--     SIDM_V_MANCOMUNIDADL.
--   * Catálogos de CD_ESTADO_UDAI (PIA) y CDMOTBAJA (solicitud).
--   * Contacto, visita, firma del acuerdo e instalación del CU2: probablemente
--     en las empresas o en SAP, no en SIDEMA.
--   * Efectivos por fase: los da la unidad.
----------------------------------------------------------------------------
"""

partes = [CABECERA, SEP.format('BLOQUE 1 · Las 29 vistas de v1, con lista de columnas'), '', cabeza]
resumen = []
for tabla, uso, cols, fuera, ojo in T3:
    b, n, tot = bloque(tabla, uso, cols, fuera, ojo)
    partes.append('\n' + b)
    resumen.append(f'{vista(tabla)}: {n}/{tot}')
partes.append(SEP.format(f'BLOQUE 2 · {len(CATALOGOS)} catálogos nuevos (SELECT *: solo códigos y descripciones)'))
partes.append('\n-- Encontrados por el nombre el 24/11/2026 en el origen; sus columnas no se han podido ver.\n'
              '-- «Por confirmar» = el código que explican se deduce del nombre.\n'
              '-- Si alguna tabla no es de DBA_SIDM, el propietario de la vista necesita SELECT WITH GRANT OPTION.')
for tabla, uso in CATALOGOS:
    partes.append('\n' + bloque_catalogo(tabla, uso))
partes.append(SEP.format('BLOQUE 3 · Columnas de las tablas del CU2 y de la citación (solo estructura)'))
partes.append(DICCIONARIO)
partes.append(SEP.format('BLOQUE 4 · Comprobación'))
partes.append(COMPROBACION)
sql = '\n'.join(partes).rstrip() + PIE
sql = re.sub(r'\n{3,}', '\n\n', sql)
assert len(CATALOGOS) == len({t for t, _ in CATALOGOS}) == 28
codigo = [l for l in sql.split('\n') if not l.lstrip().startswith('--')]
assert not any('DROP VIEW' in l for l in codigo)
n_star = sum('SELECT *' in l for l in codigo)
assert n_star == len(CATALOGOS), f'SELECT * fuera de los catálogos: {n_star}'
for o in OUT:
    o.write_text(sql, encoding='utf-8')
print('\n'.join(resumen))
print('vistas bloque 1:', 3 + len(T3), '· catálogos:', len(CATALOGOS), '· líneas:', sql.count('\n') + 1)
