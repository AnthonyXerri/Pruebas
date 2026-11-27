-- Evento SolicitudUrgencia (27/11/2026): se pide tramitar el expediente por urgencia.
-- Pegar sin punto y coma. Data Source: None (Global).
-- Pendiente de datos: ninguna de las 100 solicitudes de la muestra tiene urgencia (0 filas).
SELECT
    'URG_' || CAST(u."ID_URGENCIA" AS VARCHAR) AS "ID",
    u."FC_SOLICITUD"                  AS "Time",
    CAST(u."ID_SOLICITUD" AS VARCHAR) AS "SolicitudDependencia",
    u."IT_ESTADO"                     AS "EstadoUrgencia",
    u."CD_MANCO"                      AS "Mancomunidad",
    u."CD_CENTRO_SS"                  AS "CentroServiciosSociales",
    u."FC_APROBACION"                 AS "FechaAprobacion",
    u."FC_RECHAZO"                    AS "FechaRechazo",
    u."CD_LOGIN_TECNICO"              AS "Tecnico"
FROM "SIDM_RI_URGENCIA" u
WHERE u."FC_SOLICITUD" IS NOT NULL
