-- Evento RequerimientoPIA (27/11/2026): se pide documentación durante el PIA ("% con requerimiento").
-- Pegar sin punto y coma. Data Source: None (Global).
-- Pendiente de datos: 0 filas para los PIA de la muestra del 27/11.
SELECT
    'REQP_' || CAST(r."ID_PIA" AS VARCHAR) || '_' || CAST(r."NM_SUBSANACION" AS VARCHAR) AS "ID",
    r."FCALTA"                        AS "Time",
    CAST(r."ID_PIA" AS VARCHAR)       AS "PIADependencia",
    CAST(p."ID_SOLICITUD" AS VARCHAR) AS "SolicitudDependencia",
    r."CD_TRAMITE"                    AS "CodigoTramite",
    r."IDALTA"                        AS "Usuario"
FROM "SIDM_RI_SUBS_PIA" r
LEFT JOIN "SIDM_RI_PIA" p ON CAST(p."ID_PIA" AS VARCHAR) = CAST(r."ID_PIA" AS VARCHAR)
WHERE r."FCALTA" IS NOT NULL
