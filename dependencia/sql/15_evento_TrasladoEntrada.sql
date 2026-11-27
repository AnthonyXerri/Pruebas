-- Evento TrasladoEntrada (27/11/2026): llega un expediente de otra comunidad.
-- Pegar sin punto y coma. Data Source: None (Global).
-- Pendiente de datos: 0 filas en la muestra del 27/11.
SELECT
    'TIN_' || CAST(t."ID_TRASLADO_IN" AS VARCHAR) AS "ID",
    t."FC_REGISTRO_SOL"               AS "Time",
    CAST(t."ID_SOLICITUD" AS VARCHAR) AS "SolicitudDependencia",
    t."CD_COMU_ORIGEN"                AS "ComunidadOrigen",
    t."IT_ESTADO"                     AS "EstadoTraslado",
    t."FC_CONSOLIDACION"              AS "FechaConsolidacion"
FROM "SIDM_RI_TRASLADO_IN" t
WHERE t."FC_REGISTRO_SOL" IS NOT NULL
