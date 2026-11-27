-- Evento ValoracionRealizada (27/11/2026): la visita de valoración (hito de la fase 2).
-- Pegar sin punto y coma. Data Source: None (Global).
-- Relaciones: SolicitudDependencia y ValoracionDependencia (mismo ID que el objeto, sin prefijo de evento).
SELECT
    'VR_BVD_' || CAST(b."IDSOLICITUD" AS VARCHAR) || '_' || CAST(b."NMVALORACION" AS VARCHAR) AS "ID",
    b."FCVALORACION"                 AS "Time",
    CAST(b."IDSOLICITUD" AS VARCHAR) AS "SolicitudDependencia",
    'BVD_' || CAST(b."IDSOLICITUD" AS VARCHAR) || '_' || CAST(b."NMVALORACION" AS VARCHAR) AS "ValoracionDependencia",
    'BVD'                            AS "TipoBaremo",
    b."CDVALORADOR"                  AS "Valorador",
    b."IT_VALORACION_ONLINE"         AS "Telematica"
FROM "SIDM_VALORACION_BVD" b
WHERE b."FCVALORACION" IS NOT NULL
UNION ALL
SELECT
    'VR_EVE_' || CAST(v."IDSOLICITUD" AS VARCHAR) || '_' || CAST(v."NMVALORACION" AS VARCHAR),
    v."FCVALORACION",
    CAST(v."IDSOLICITUD" AS VARCHAR),
    'EVE_' || CAST(v."IDSOLICITUD" AS VARCHAR) || '_' || CAST(v."NMVALORACION" AS VARCHAR),
    'EVE',
    v."CDVALORADOR",
    CAST(NULL AS VARCHAR)
FROM "SIDM_VALORACION_EVE" v
WHERE v."FCVALORACION" IS NOT NULL
