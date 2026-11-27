-- Evento TrasladoSalida (27/11/2026): el beneficiario pide trasladar el expediente a otra comunidad.
-- Pegar sin punto y coma. Data Source: None (Global).
-- Pendiente de datos: 0 filas en la muestra del 27/11.
SELECT
    'TOUT_' || CAST(t."ID_SOLICITUD" AS VARCHAR) || '_' || CAST(t."NM_TRASLADO" AS VARCHAR) AS "ID",
    t."FC_SOLICITUD"                  AS "Time",
    CAST(t."ID_SOLICITUD" AS VARCHAR) AS "SolicitudDependencia",
    t."CD_COMU"                       AS "ComunidadDestino",
    t."IT_ESTADO"                     AS "EstadoTraslado"
FROM "SIDM_RI_TRASLADO_OUT" t
WHERE t."FC_SOLICITUD" IS NOT NULL
