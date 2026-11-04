-- Evento AltaSolicitudDependencia: grabación de la solicitud en SIDEMA (FCALTA)
-- El mockup mide la fase 1 como fecha de solicitud -> fecha de grabación (objetivo de 30 días)
-- y el ciclo de vida tiene «Registro» y «Alta (SIDEMA)» como hitos separados.
SELECT
    'ALTA_' || CAST(s."IDSOLICITUD" AS VARCHAR) AS "ID",
    s."FCALTA"                                  AS "Time",
    CAST(s."IDSOLICITUD" AS VARCHAR)            AS "SolicitudDependencia",
    s."IDALTA"                                  AS "Usuario"
FROM "SIDM_SOLICITUD" s
WHERE s."FCALTA" IS NOT NULL;
