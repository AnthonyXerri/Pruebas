-- Evento Cambio de estado, con nombre del estado, fase y usuario
-- Validada el 04/11/2026: 100 filas, todas con fase, sin IDs repetidos.
-- Fases: propuesta pendiente de validar con Andrés (AVC y RA por aclarar).
SELECT
    'CE_' || CAST(h."IDSOLICITUD" AS VARCHAR) || '_' || RIGHT(h."CDESTADO", 2)
          || '_' || TO_CHAR(h."FCMODI", 'YYYYMMDDHH24MISS')   AS "ID",
    h."FCMODI"                                                AS "Time",
    CAST(h."IDSOLICITUD" AS VARCHAR)                          AS "SolicitudDependencia",
    RIGHT(h."CDESTADO", 2)                                    AS "CodigoEstado",
    e."DSESTADO"                                              AS "Estado",
    CASE
        WHEN RIGHT(h."CDESTADO", 2) IN ('01','03','60','30','25','55','10','09')      THEN '1 · Grabación'
        WHEN RIGHT(h."CDESTADO", 2) IN ('00','40','39','99','98','06','41','42')      THEN '2a · Citación'
        WHEN RIGHT(h."CDESTADO", 2) IN ('43','07','11','44','45','48','32','47','33') THEN '2b · Valoración'
        WHEN RIGHT(h."CDESTADO", 2) IN ('50','51','35','04','70','71')                THEN '3 · Resolución'
        WHEN RIGHT(h."CDESTADO", 2) IN ('05','20','15')                               THEN 'AVC'
        WHEN RIGHT(h."CDESTADO", 2) IN ('90','02','34','36','95','08')                THEN '4 · Cierre'
        WHEN RIGHT(h."CDESTADO", 2) = '91'                                            THEN '5 · Recurso'
        ELSE 'Sin fase'
    END                                                       AS "Fase",
    h."IDMODI"                                                AS "Usuario"
FROM "SIDM_HIST_ESTADO" h
LEFT JOIN "SIDM_ESTADO_SOLICITUD" e
       ON RIGHT(e."CDESTADO", 2) = RIGHT(h."CDESTADO", 2)
WHERE h."FCMODI" IS NOT NULL;
