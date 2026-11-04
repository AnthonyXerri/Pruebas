-- Objeto SolicitudDependencia · atributos (validada el 04/11/2026 con la muestra local)
-- Los alias son los nombres de los atributos: declararlos igual en Objects & Events.
SELECT
    CAST(s."IDSOLICITUD" AS VARCHAR) AS "ID",
    s."NMSOLICITUD"   AS "NumeroSolicitud",
    s."FCSOLICITUD"   AS "FechaSolicitud",
    s."FCREGENTRADA"  AS "FechaRegistroEntrada",
    s."FCALTA"        AS "FechaAlta",
    s."FC_FIN_PLAZO"  AS "FechaFinPlazo",
    s."FCBAJA"        AS "FechaBaja",
    s."CDESTADO"      AS "CodigoEstadoActual",
    e."DSESTADO"      AS "EstadoActual",
    s."CDTIPO"        AS "TipoSolicitud",
    s."IT_URGENTE"    AS "Urgente",
    s."IT_TRASLADO"   AS "Traslado",
    s."ITEXTINGUIDO"  AS "Extinguido",
    s."NMREVISION"    AS "NumeroRevision",
    CAST(s."IDSOLICITUD_ORIG_REVISION" AS VARCHAR) AS "IdSolicitudOriginal",
    s."IDALTA"        AS "UsuarioAlta",                          -- quien graba la solicitud (fase 1)
    CAST(s."IDSOLICITANTE" AS VARCHAR) AS "IdSolicitante"        -- para cruzar con la tabla de personas
FROM "SIDM_SOLICITUD" s
LEFT JOIN "SIDM_ESTADO_SOLICITUD" e
       ON RIGHT(e."CDESTADO", 2) = RIGHT(s."CDESTADO", 2);
