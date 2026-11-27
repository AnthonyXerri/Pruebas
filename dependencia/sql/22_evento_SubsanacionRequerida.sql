-- Evento SubsanacionRequerida (27/11/2026): se pide al solicitante que subsane la solicitud (fase 1).
-- Pegar sin punto y coma. Data Source: None (Global).
-- En la muestra de 2025 FCINICIOSUBSANACION viene rellena (en la antigua estaba vacía): sirve de Time.
-- El motivo: CDESTADO_DOCUMENTACION es un código; su catálogo (SIDM_ESTADO_SUBSANACION) llega con el
-- bloque 2 del script de vistas. DSTEXTO_LIBRE viene vacío en la muestra.
-- CDESTADO_EXPEDIENTE usa los códigos de SIDM_ESTADO_SOLICITUD (mismo cruce por los 2 últimos dígitos que
-- el objeto). Sale "Expediente Resuelto": parece el estado ACTUAL, no el del momento de la subsanación.
-- Por confirmar con Andrés: FCDESISTIMIENTO viene en todas las filas: ¿es la fecha límite para subsanar
-- o la del desistimiento real? Y si CDESTADO_EXPEDIENTE se actualiza o es una foto.
SELECT
    'SUB_' || CAST(s."IDSOLICITUD" AS VARCHAR) || '_' || CAST(s."NMSUBSANACION" AS VARCHAR) AS "ID",
    s."FCINICIOSUBSANACION"            AS "Time",
    CAST(s."IDSOLICITUD" AS VARCHAR)   AS "SolicitudDependencia",
    s."NMSUBSANACION"                  AS "NumeroSubsanacion",          -- BIGINT: Integer en el tipo
    s."CDESTADO_DOCUMENTACION"         AS "CodigoEstadoDocumentacion",  -- el motivo (código)
    s."CDESTADO_EXPEDIENTE"            AS "CodigoEstadoExpediente",
    e."DSESTADO"                       AS "EstadoExpediente",
    s."ITDOC_ADICIONAL_REQUERIDA"      AS "DocumentacionAdicional",     -- S / N
    s."DSTEXTO_LIBRE"                  AS "TextoMotivo",
    s."FCDESISTIMIENTO"                AS "FechaDesistimiento"          -- TIMESTAMP: Datetime
FROM "SIDM_SUBSANACION_DOCUMENTACION" s
LEFT JOIN "SIDM_ESTADO_SOLICITUD" e
       ON RIGHT(e."CDESTADO", 2) = RIGHT(s."CDESTADO_EXPEDIENTE", 2)
WHERE s."FCINICIOSUBSANACION" IS NOT NULL
