-- Evento CambioEstadoPIA (27/11/2026): cada trámite del histórico del PIA (fase 3).
-- Pegar sin punto y coma. Data Source: None (Global).
-- Relaciones: PIADependencia y SolicitudDependencia (la del PIA). La fecha es FCALTA porque
-- FC_ESTADO_PIA viene vacía en la muestra; si llega rellena, manda ella.
SELECT
    'CEP_' || CAST(t."ID_PIA" AS VARCHAR) || '_' || CAST(t."NM_TRAMITE" AS VARCHAR) AS "ID",
    COALESCE(t."FC_ESTADO_PIA", t."FCALTA")   AS "Time",
    CAST(t."ID_PIA" AS VARCHAR)               AS "PIADependencia",
    CAST(p."ID_SOLICITUD" AS VARCHAR)         AS "SolicitudDependencia",
    t."CD_ESTADO_PIA"                         AS "CodigoEstadoPIA",
    e."DS_ESTADO_PIA"                         AS "EstadoPIA",
    t."CD_GRUPO"                              AS "Grupo",
    t."CD_ESTADO_UDAI"                        AS "EstadoUDAI",
    t."IDALTA"                                AS "Usuario"          -- técnico que hace el trámite
FROM "SIDM_RI_TRAMITES" t
LEFT JOIN "SIDM_RI_PIA" p         ON CAST(p."ID_PIA" AS VARCHAR) = CAST(t."ID_PIA" AS VARCHAR)
LEFT JOIN "SIDM_RI_ESTADOS_PIA" e ON e."CD_ESTADO_PIA" = t."CD_ESTADO_PIA"
WHERE COALESCE(t."FC_ESTADO_PIA", t."FCALTA") IS NOT NULL
