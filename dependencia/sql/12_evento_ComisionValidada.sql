-- Evento ComisionValidada (27/11/2026): la comisión valida el grado propuesto (hito 8).
-- Pegar sin punto y coma. Data Source: None (Global).
-- Baremo (NMBAREMO) es DOUBLE: en el tipo de evento va como Floating point (String no pasa la validación).
SELECT
    'COM_' || CAST(d."IDSOLICITUD" AS VARCHAR) || '_' || CAST(d."FCVALIDACION_COMISION" AS VARCHAR) AS "ID",
    d."FCVALIDACION_COMISION"        AS "Time",
    CAST(d."IDSOLICITUD" AS VARCHAR) AS "SolicitudDependencia",
    CAST(d."CDGRADO" AS VARCHAR)     AS "CodigoGradoPropuesto",
    d."DSGRADO_NIVEL"                AS "GradoPropuesto",
    d."NMBAREMO"                     AS "Baremo",
    d."ACTA_COMISION"                AS "Acta",
    d."CDVALORADOR"                  AS "Valorador"
FROM "SIDM_DICTAMEN_TECNICO" d
WHERE d."FCVALIDACION_COMISION" IS NOT NULL
