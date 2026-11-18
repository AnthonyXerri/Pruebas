-- Evento NatSolicitudPresentada · cuándo presenta la solicitud la interesada (inicio del E2E y de la fase 1)
-- Adaptado de PnCSolicitudPresentada (18/11/2026). Cambios: filtro D032 + 3163, relación NatExpedientes.
-- Relación (crear antes): involves one NatExpedientes ("NatExpedientes"). Data Source: PRATLX_RO.
-- La vista tiene varias filas por expediente: GROUP BY + MIN se queda con la primera fecha.
SELECT
    'SolicitudPresentada_' || E."CDEXPEDIENTE"          AS "ID",
    CAST(MIN(E."FC_SOL_INTERESADO") AS TIMESTAMP)       AS "Time",
    'Solicitud presentada por la interesada'            AS "Actividad",
    E."CDEXPEDIENTE"                                    AS "NatExpedientes"
FROM "GSTA_V_CEL_EXPEDIENTE" AS E
WHERE E."CDAPLICACION" = 'D032'
  AND E."CDPROCEDIMIENTO" = '3163'
  AND E."FC_SOL_INTERESADO" IS NOT NULL
GROUP BY E."CDEXPEDIENTE"
