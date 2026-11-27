-- Objeto ValoracionDependencia (27/11/2026): una fila por valoración, BVD y EVE juntas.
-- Pegar sin punto y coma. Data Source: None (Global).
-- Relaciones (columnas con el nombre del tipo destino):
--   SolicitudDependencia -> la solicitud valorada (n valoraciones : 1 solicitud)
--   ValoradorDependencia -> quien valora (n : 1)
-- El ID lleva el baremo delante porque BVD y EVE numeran sus valoraciones por separado.
SELECT
    'BVD_' || CAST(b."IDSOLICITUD" AS VARCHAR) || '_' || CAST(b."NMVALORACION" AS VARCHAR) AS "ID",
    'BVD'                      AS "TipoBaremo",
    b."NMVALORACION"           AS "NumeroValoracion",
    b."FCVALORACION"           AS "FechaValoracion",        -- la visita
    b."FCINICIO"               AS "FechaInicio",
    b."FCFIN"                  AS "FechaFin",
    b."FCINICIO_SISTEMA"       AS "FechaInicioGrabacion",
    b."FCFIN_SISTEMA"          AS "FechaFinGrabacion",
    b."ITCOMPLETA"             AS "Completa",
    b."IT_VALORACION_ONLINE"   AS "Telematica",
    b."NMBAREMO_COGNITIVO"     AS "BaremoCognitivo",
    b."NMBAREMO_FISICO"        AS "BaremoFisico",
    CAST(NULL AS INTEGER)      AS "GradoEVE",
    CAST(b."IDSOLICITUD" AS VARCHAR) AS "SolicitudDependencia",
    b."CDVALORADOR"            AS "ValoradorDependencia"
FROM "SIDM_VALORACION_BVD" b
UNION ALL
SELECT
    'EVE_' || CAST(v."IDSOLICITUD" AS VARCHAR) || '_' || CAST(v."NMVALORACION" AS VARCHAR),
    'EVE',
    v."NMVALORACION",
    v."FCVALORACION",
    v."FCINICIO",
    v."FCFIN",
    v."FCINICIO_SISTEMA",
    v."FCFIN_SISTEMA",
    v."ITCOMPLETA",
    CAST(NULL AS VARCHAR),                                  -- la EVE no tiene telemática
    CAST(NULL AS FLOAT),
    CAST(NULL AS FLOAT),
    v."NMGRADO_DEPENDENCIA",
    CAST(v."IDSOLICITUD" AS VARCHAR),
    v."CDVALORADOR"
FROM "SIDM_VALORACION_EVE" v
