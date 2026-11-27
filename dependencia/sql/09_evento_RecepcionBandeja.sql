-- Evento RecepcionBandeja (27/11/2026): un registro de entrada llega a una bandeja de eReg.
-- Pegar sin punto y coma. Data Source: None (Global).
-- Relación SolicitudDependencia SOLO cuando ya existe una solicitud con el mismo NMREFERENCIA.
-- Las que no la tienen son justo las "registradas sin grabar" del CU1 (fase 1): el evento
-- existe igual, sin solicitud, y la View las cuenta aparte.
-- Si dos solicitudes compartieran referencia se coge la menor, para no duplicar el evento.
SELECT
    'BAN_' || b."NMREFERENCIA" || '_' || b."CD_BANDEJA"
           || '_' || CAST(COALESCE(b."FC_RECEPCION", b."FCALTA") AS VARCHAR) AS "ID",
    COALESCE(b."FC_RECEPCION", b."FCALTA")   AS "Time",
    s."IDSOLICITUD"                          AS "SolicitudDependencia",
    b."CD_BANDEJA"                           AS "CodigoBandeja",
    c."DS_BANDEJA"                           AS "Bandeja",
    b."DSORIGENDOC"                          AS "Origen",          -- ORVE / Presencial / Internet
    b."IT_ESTADO"                            AS "EstadoBandeja",
    b."NMREFERENCIA"                         AS "NumeroReferencia",
    b."FC_ENVIO_UNIDAD"                      AS "FechaEnvioUnidad",
    b."FCBAJA"                               AS "FechaBaja",
    b."IDALTA"                               AS "Usuario"
FROM "SIDM_BANDEJA_RECEPCIONADOS" b
LEFT JOIN "SIDM_CAT_BANDEJA_EREG" c
       ON c."CD_BANDEJA" = b."CD_BANDEJA"
LEFT JOIN (
    SELECT CAST(x."NMREFERENCIA" AS VARCHAR) AS "NMREFERENCIA",
           MIN(CAST(x."IDSOLICITUD" AS VARCHAR)) AS "IDSOLICITUD"
    FROM "SIDM_SOLICITUD" x
    WHERE x."NMREFERENCIA" IS NOT NULL
    GROUP BY CAST(x."NMREFERENCIA" AS VARCHAR)
) s
       ON s."NMREFERENCIA" = CAST(b."NMREFERENCIA" AS VARCHAR)
WHERE COALESCE(b."FC_RECEPCION", b."FCALTA") IS NOT NULL
