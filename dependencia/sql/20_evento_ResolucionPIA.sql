-- Evento ResolucionPIA (27/11/2026): se resuelve el PIA (fin de la fase 3).
-- Pegar sin punto y coma. Data Source: None (Global).
-- Fecha: FCRESOLUCION_PIA y, si falta, FCRESOLUCION (las dos existen en SIDEMA; por confirmar con Andrés).
SELECT
    'RP_' || CAST(p."ID_PIA" AS VARCHAR)       AS "ID",
    COALESCE(p."FCRESOLUCION_PIA", p."FCRESOLUCION") AS "Time",
    CAST(p."ID_PIA" AS VARCHAR)                AS "PIADependencia",
    CAST(p."ID_SOLICITUD" AS VARCHAR)          AS "SolicitudDependencia",
    t."DS_TPPIA"                               AS "Prestacion",
    p."CD_MOT_RESOL"                           AS "MotivoResolucion"
FROM "SIDM_RI_PIA" p
LEFT JOIN "SIDM_RI_TPPIA" t ON t."CD_TPPIA" = p."CD_TPPIA"
WHERE COALESCE(p."FCRESOLUCION_PIA", p."FCRESOLUCION") IS NOT NULL
