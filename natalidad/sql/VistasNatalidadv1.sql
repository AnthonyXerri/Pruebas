----------------------------------------------------------------------------
-- Vistas de Atlantix para Celonis · Minería de procesos de Natalidad (D032 · 3163)
-- VistasNatalidadv1 · 26/11/2026
--
-- Tablas y campos indicados por Soluciones el 24/11/2026 («Nombre de tabla-campo
-- de bd Natalidad»). Todas las tablas D032_3163_* son solo del procedimiento 3163.
--
-- El script tiene 4 bloques:
--   0. Comprobación previa: columnas de las tablas (solo nombres y tipos).
--   1. 6 vistas de datos, con lista de columnas.
--   2. 3 vistas de catálogos (código y descripción).
--   3. Comprobación final: vistas compiladas y permisos.
--
-- Criterio: solo las columnas que pide el cuadro y las claves para unir las
-- tablas. Nada que identifique a la persona (nombre, documento, contacto,
-- dirección, cuenta) ni texto libre. Lo sensible que se deja va marcado «Ojo».
--
-- Antes de ejecutar:
--   * Ejecutar como script (F5 en SQL Developer) con el usuario propietario de
--     las tablas D032_3163_*.
--   * Poner en DEFINE el rol con el que lee Celonis en Atlantix (el mismo que
--     tiene permiso sobre las vistas GSTA_V_CEL_*). Por confirmar.
--
-- En Celonis: añadir las vistas a la extracción de la conexión de Atlantix
-- (PRATLX_RO).
----------------------------------------------------------------------------

DEFINE ROL_CELONIS = 'ROL_POR_CONFIRMAR'

----------------------------------------------------------------------------
-- BLOQUE 0 · Comprobación previa (solo estructura, ningún dato)
----------------------------------------------------------------------------

-- Si alguna columna de las vistas no aparece aquí, avisar antes de crear nada.
SELECT owner, table_name, column_id, column_name, data_type, data_length
FROM all_tab_columns
WHERE table_name IN (
    'D032_3163_SOL_EXP',
    'D032_3163_EXP_HIJOS',
    'D032_3163_CALENDARIO_PAGOS',
    'D032_3163_EXP_DES_DEN',
    'D032_3163_PROPUESTA_MOD_EXP',
    'D032_3163_EXP_SOLICIT_BENEFIC',
    'D032_3163_CAT_TIPOS_SOL',
    'D032_3163_CAT_DES_DEN',
    'D032_3163_CAT_TIPOS_MOD_EXP'
)
ORDER BY table_name, column_id;

----------------------------------------------------------------------------
-- BLOQUE 1 · 6 vistas de datos, con lista de columnas
----------------------------------------------------------------------------

--D032_3163_SOL_EXP
-- Uso: expediente: tipo de solicitud, hijos, propuesta favorable, importe, nacimiento del menor y baja.

CREATE OR REPLACE VIEW D032_V_NAT_SOL_EXP AS
SELECT
    ID_SOL_EXP,        -- clave de la solicitud-expediente (une con hijos, denegaciones, modificaciones y solicitante)
    NUM_EXPEDIENTE,    -- número de expediente de Atlantix (une con GSTA_V_CEL_EXPEDIENTE.CDEXPEDIENTE, por confirmar)
    ID_TIPO_SOL,       -- tipo de solicitud (catálogo D032_3163_CAT_TIPOS_SOL)
    NUM_HIJOS,         -- número de hijos
    FC_PRO_FAVORABLE,  -- fecha de la propuesta favorable = inicio del pago
    NM_TOTAL_CUANTIA,  -- importe total propuesto
    FC_NACIMIENTO,     -- Ojo: fecha de nacimiento del menor (fin del derecho a los 2 años)
    FC_RESOL_BAJA      -- fecha de resolución de la baja
FROM D032_3163_SOL_EXP;

GRANT SELECT ON D032_V_NAT_SOL_EXP TO &&ROL_CELONIS;
CREATE OR REPLACE PUBLIC SYNONYM D032_V_NAT_SOL_EXP FOR D032_V_NAT_SOL_EXP;

--D032_3163_EXP_HIJOS
-- Uso: hijos del expediente y fin del pago.

CREATE OR REPLACE VIEW D032_V_NAT_EXP_HIJOS AS
SELECT
    ID_EXP_HIJO,  -- clave del hijo (une con el calendario de pagos)
    ID_SOL_EXP,   -- expediente
    FC_FIN_PAGO   -- fin del pago = última nómina
FROM D032_3163_EXP_HIJOS;

GRANT SELECT ON D032_V_NAT_EXP_HIJOS TO &&ROL_CELONIS;
CREATE OR REPLACE PUBLIC SYNONYM D032_V_NAT_EXP_HIJOS FOR D032_V_NAT_EXP_HIJOS;

--D032_3163_CALENDARIO_PAGOS
-- Uso: pagos por mes de cada hijo.

CREATE OR REPLACE VIEW D032_V_NAT_CALENDARIO_PAGOS AS
SELECT
    ID_EXP_HIJO,  -- hijo (y por él, el expediente)
    NM_ANO,       -- año
    NM_MES,       -- mes
    NM_IMPORTE,   -- importe mensual
    FC_PAGO       -- fecha de pago
FROM D032_3163_CALENDARIO_PAGOS;

GRANT SELECT ON D032_V_NAT_CALENDARIO_PAGOS TO &&ROL_CELONIS;
CREATE OR REPLACE PUBLIC SYNONYM D032_V_NAT_CALENDARIO_PAGOS FOR D032_V_NAT_CALENDARIO_PAGOS;

--D032_3163_EXP_DES_DEN
-- Uso: motivos de denegación o desistimiento del expediente.

CREATE OR REPLACE VIEW D032_V_NAT_EXP_DES_DEN AS
SELECT
    ID_SOL_EXP,  -- expediente
    ID_DES_DEN   -- motivo (catálogo D032_3163_CAT_DES_DEN)
FROM D032_3163_EXP_DES_DEN;

GRANT SELECT ON D032_V_NAT_EXP_DES_DEN TO &&ROL_CELONIS;
CREATE OR REPLACE PUBLIC SYNONYM D032_V_NAT_EXP_DES_DEN FOR D032_V_NAT_EXP_DES_DEN;

--D032_3163_PROPUESTA_MOD_EXP
-- Uso: modificaciones del expediente; las bajas son los tipos 8, 9, 10, 11 y 14.
-- Fuera: DS_OBSERVACIONES y DS_MOTIVO_BAJA (texto libre): el motivo de la baja sale del tipo de modificación (catálogo). Se pueden añadir si la unidad lo pide.

CREATE OR REPLACE VIEW D032_V_NAT_PROPUESTA_MOD_EXP AS
SELECT
    ID_SOL_EXP,         -- expediente
    ID_MOD_EXP_ACTIVA,  -- tipo de modificación (catálogo D032_3163_CAT_TIPOS_MOD_EXP.ID_PARAM_MOD_EXP)
    FC_BAJA,            -- fecha de efecto de la baja
    BL_DESHECHA,        -- modificación deshecha (para una baja válida: N)
    BL_MODI_TERMINADA,  -- modificación terminada (para una baja válida: S)
    BL_RECEPCIONADO     -- recepcionada (para una baja válida: S)
FROM D032_3163_PROPUESTA_MOD_EXP;

GRANT SELECT ON D032_V_NAT_PROPUESTA_MOD_EXP TO &&ROL_CELONIS;
CREATE OR REPLACE PUBLIC SYNONYM D032_V_NAT_PROPUESTA_MOD_EXP FOR D032_V_NAT_PROPUESTA_MOD_EXP;

--D032_3163_EXP_SOLICIT_BENEFIC
-- Uso: datos de la solicitante para la composición.

CREATE OR REPLACE VIEW D032_V_NAT_EXP_SOLICIT_BENEFIC AS
SELECT
    ID_SOL_EXP,              -- expediente
    CD_NACIONALIDAD,         -- Ojo: nacionalidad
    CD_NACIONALIDAD_ORIGEN,  -- Ojo: nacionalidad
    CD_PROVINCIA_RESI,       -- provincia de residencia (SUCA_PROVINCIA)
    CD_MUNICIPIO_RESI,       -- municipio de residencia (SUCA_MUNICIPIO)
    CD_PAIS_RESI,            -- país de residencia (SUCA_PAIS)
    FC_NACIMIENTO            -- Ojo: fecha de nacimiento (solo para la edad en tramos)
FROM D032_3163_EXP_SOLICIT_BENEFIC;

GRANT SELECT ON D032_V_NAT_EXP_SOLICIT_BENEFIC TO &&ROL_CELONIS;
CREATE OR REPLACE PUBLIC SYNONYM D032_V_NAT_EXP_SOLICIT_BENEFIC FOR D032_V_NAT_EXP_SOLICIT_BENEFIC;

----------------------------------------------------------------------------
-- BLOQUE 2 · 3 vistas de catálogos (código y descripción)
----------------------------------------------------------------------------

--D032_3163_CAT_TIPOS_SOL
-- Uso: tipos de solicitud.

CREATE OR REPLACE VIEW D032_V_NAT_CAT_TIPOS_SOL AS
SELECT
    ID_TIPO_SOL,
    DS_TIPO_SOL
FROM D032_3163_CAT_TIPOS_SOL;

GRANT SELECT ON D032_V_NAT_CAT_TIPOS_SOL TO &&ROL_CELONIS;
CREATE OR REPLACE PUBLIC SYNONYM D032_V_NAT_CAT_TIPOS_SOL FOR D032_V_NAT_CAT_TIPOS_SOL;

--D032_3163_CAT_DES_DEN
-- Uso: motivos de denegación.

CREATE OR REPLACE VIEW D032_V_NAT_CAT_DES_DEN AS
SELECT
    ID_DES_DEN,
    DS_CASUISTICA
FROM D032_3163_CAT_DES_DEN;

GRANT SELECT ON D032_V_NAT_CAT_DES_DEN TO &&ROL_CELONIS;
CREATE OR REPLACE PUBLIC SYNONYM D032_V_NAT_CAT_DES_DEN FOR D032_V_NAT_CAT_DES_DEN;

--D032_3163_CAT_TIPOS_MOD_EXP
-- Uso: tipos de modificación; las bajas son 8, 9, 10, 11 y 14.

CREATE OR REPLACE VIEW D032_V_NAT_CAT_TIPOS_MOD_EXP AS
SELECT
    ID_PARAM_MOD_EXP,
    DS_NOMBRE_PARAM
FROM D032_3163_CAT_TIPOS_MOD_EXP;

GRANT SELECT ON D032_V_NAT_CAT_TIPOS_MOD_EXP TO &&ROL_CELONIS;
CREATE OR REPLACE PUBLIC SYNONYM D032_V_NAT_CAT_TIPOS_MOD_EXP FOR D032_V_NAT_CAT_TIPOS_MOD_EXP;

----------------------------------------------------------------------------
-- BLOQUE 3 · Comprobación final
----------------------------------------------------------------------------

-- Todas las vistas deben salir con STATUS = VALID (9).
SELECT object_name, status
FROM user_objects
WHERE object_type = 'VIEW' AND object_name LIKE 'D032\_V\_NAT\_%' ESCAPE '\'
ORDER BY object_name;

-- Permisos de lectura del rol que usa Celonis.
SELECT table_name, privilege
FROM user_tab_privs_made
WHERE grantee = '&&ROL_CELONIS' AND table_name LIKE 'D032\_V\_NAT\_%' ESCAPE '\'
ORDER BY table_name;

----------------------------------------------------------------------------
-- PENDIENTE
--   * Expediente revisado (marca y fecha): los campos aún no existen (petición
--     FARO del 24/11/2026). Se añaden a la vista de SOL_EXP cuando estén.
--   * Rol de Celonis en Atlantix (ROL_CELONIS): por confirmar.
--   * Clave de cada fila del calendario de pagos y de las modificaciones: si
--     tienen un identificador propio, añadirlo a sus vistas.
--   * EXP_SOLICIT_BENEFIC: confirmar si hay una fila por expediente (la
--     solicitante) o también otras personas; si hay columna de tipo, añadirla.
--   * Nombres de provincia y municipio: salen de GSTA_V_INTERESADOS o de
--     SUCA_PROVINCIA y SUCA_MUNICIPIO, si el rol de Celonis los puede leer.
----------------------------------------------------------------------------
