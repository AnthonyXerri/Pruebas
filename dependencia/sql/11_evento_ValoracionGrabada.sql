-- Evento ValoracionGrabada (27/11/2026): fin de la grabación de la valoración en el sistema.
-- Pegar sin punto y coma. Data Source: None (Global).
-- FCFIN_SISTEMA venía vacía en la muestra antigua (2007-2015) pero en la de 2025 sí viene (75 de 83).
SELECT
    'VG_BVD_' || CAST(b."IDSOLICITUD" AS VARCHAR) || '_' || CAST(b."NMVALORACION" AS VARCHAR) AS "ID",
    b."FCFIN_SISTEMA"                AS "Time",
    CAST(b."IDSOLICITUD" AS VARCHAR) AS "SolicitudDependencia",
    'BVD_' || CAST(b."IDSOLICITUD" AS VARCHAR) || '_' || CAST(b."NMVALORACION" AS VARCHAR) AS "ValoracionDependencia",
    'BVD'                            AS "TipoBaremo",
    b."FCINICIO_SISTEMA"             AS "InicioGrabacion"
FROM "SIDM_VALORACION_BVD" b
WHERE b."FCFIN_SISTEMA" IS NOT NULL
UNION ALL
SELECT
    'VG_EVE_' || CAST(v."IDSOLICITUD" AS VARCHAR) || '_' || CAST(v."NMVALORACION" AS VARCHAR),
    v."FCFIN_SISTEMA",
    CAST(v."IDSOLICITUD" AS VARCHAR),
    'EVE_' || CAST(v."IDSOLICITUD" AS VARCHAR) || '_' || CAST(v."NMVALORACION" AS VARCHAR),
    'EVE',
    v."FCINICIO_SISTEMA"
FROM "SIDM_VALORACION_EVE" v
WHERE v."FCFIN_SISTEMA" IS NOT NULL
