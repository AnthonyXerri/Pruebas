-- Evento de inicio: registro de entrada (el plazo legal de 180 días cuenta desde aquí)
-- Validada el 04/11/2026: 99 de 100 (la 41 no tiene FCREGENTRADA).
SELECT
    'REG_' || CAST(s."IDSOLICITUD" AS VARCHAR) AS "ID",
    s."FCREGENTRADA"                           AS "Time",
    CAST(s."IDSOLICITUD" AS VARCHAR)           AS "SolicitudDependencia"
FROM "SIDM_SOLICITUD" s
WHERE s."FCREGENTRADA" IS NOT NULL;
