-- Evento LlamadaPIA (27/11/2026): llamada al beneficiario durante el PIA ("llamadas por expediente").
-- Pegar sin punto y coma. Data Source: None (Global).
-- Pendiente de datos: 0 filas para los PIA de la muestra del 27/11.
SELECT
    'LLA_' || CAST(l."ID_PIA" AS VARCHAR) || '_' || CAST(l."NM_LLAMADA" AS VARCHAR) AS "ID",
    COALESCE(l."FC_LLAMADA", l."FCALTA") AS "Time",
    CAST(l."ID_PIA" AS VARCHAR)          AS "PIADependencia",
    CAST(p."ID_SOLICITUD" AS VARCHAR)    AS "SolicitudDependencia",
    l."IDALTA"                           AS "Usuario"
FROM "SIDM_RI_LLAMADA" l
LEFT JOIN "SIDM_RI_PIA" p ON CAST(p."ID_PIA" AS VARCHAR) = CAST(l."ID_PIA" AS VARCHAR)
WHERE COALESCE(l."FC_LLAMADA", l."FCALTA") IS NOT NULL
