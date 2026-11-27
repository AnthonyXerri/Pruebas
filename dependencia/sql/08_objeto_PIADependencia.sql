-- Objeto PIADependencia (27/11/2026): un registro por PIA (fase 3). Pegar sin punto y coma.
-- Data Source: None (Global). Relación: SolicitudDependencia (n PIA : 1 solicitud; las revisiones
-- del PIA crean PIA nuevos que apuntan al original con IdPIAOriginal).
SELECT
    CAST(p."ID_PIA" AS VARCHAR)      AS "ID",
    p."CD_ESTADO_PIA"                AS "CodigoEstadoPIA",
    e."DS_ESTADO_PIA"                AS "EstadoPIA",
    p."FC_ESTADO"                    AS "FechaEstado",
    p."CD_TPPIA"                     AS "CodigoPrestacion",
    t."DS_TPPIA"                     AS "Prestacion",
    t."CD_AGRUPACION"                AS "AgrupacionPrestacion",   -- SAD, TA, centro de día, PECEF...
    p."CD_GRUPO"                     AS "Grupo",
    p."NM_REVISION"                  AS "NumeroRevision",
    CAST(p."ID_PIA_ORIGINAL" AS VARCHAR) AS "IdPIAOriginal",
    p."FC_EFECTOS"                   AS "FechaEfectos",
    p."FCRESOLUCION_PIA"             AS "FechaResolucionPIA",
    p."IT_PIA_RESUELTO"              AS "Resuelto",
    p."CD_MOT_RESOL"                 AS "MotivoResolucion",
    p."FC_TRAMITE_CONS"              AS "FechaConsultaBeneficiario", -- inicio del plazo imputable
    p."FC_PROPUESTA_TEC"             AS "FechaPropuestaTecnica",
    p."FC_FIN_PLAZO"                 AS "FechaFinPlazo",
    p."IT_VIGENTE"                   AS "Vigente",
    p."FCBAJA"                       AS "FechaBaja",
    CAST(p."ID_SOLICITUD" AS VARCHAR) AS "SolicitudDependencia"
FROM "SIDM_RI_PIA" p
LEFT JOIN "SIDM_RI_ESTADOS_PIA" e ON e."CD_ESTADO_PIA" = p."CD_ESTADO_PIA"
LEFT JOIN "SIDM_RI_TPPIA" t       ON t."CD_TPPIA" = p."CD_TPPIA"
