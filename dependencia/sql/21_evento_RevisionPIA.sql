-- Evento RevisionPIA (27/11/2026): se pide revisar un PIA (de parte o de oficio).
-- Pegar sin punto y coma. Data Source: None (Global).
-- Relaciones: PIADependencia = el PIA revisado; SolicitudDependencia = la solicitud de la revisión.
SELECT
    'REVP_' || CAST(r."ID_PIA_REVISADO" AS VARCHAR) || '_' || CAST(r."NM_SOLICITUD" AS VARCHAR) AS "ID",
    COALESCE(r."FC_SOLICITUD_PARTE", r."FC_1ER_REGISTRO", r."FCALTA") AS "Time",
    CAST(r."ID_PIA_REVISADO" AS VARCHAR) AS "PIADependencia",
    CAST(r."ID_SOLICITUD" AS VARCHAR)    AS "SolicitudDependencia",
    r."IT_TIPO"                          AS "TipoRevision",      -- de parte / de oficio
    r."IT_ESTADO"                        AS "EstadoRevision",    -- aprobada / rechazada
    r."CD_MOT_REVISION"                  AS "MotivoRevision",
    r."DS_TP_PIA"                        AS "Prestacion"
FROM "SIDM_RI_SOL_REVISION_PIA" r
WHERE COALESCE(r."FC_SOLICITUD_PARTE", r."FC_1ER_REGISTRO", r."FCALTA") IS NOT NULL
