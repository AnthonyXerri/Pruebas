-- Evento NatExpedienteAbierto · alta del expediente en Atlantix (fin de la fase 1, inicio de la tramitación)
-- Adaptado de PnCExpedienteAbierto (18/11/2026). Cambios: filtro D032 + 3163, relación NatExpedientes,
-- actividad «Alta del expediente» (nombre del mockup v31).
-- Relación (crear antes): involves one NatExpedientes ("NatExpedientes"). Data Source: PRATLX_RO.
SELECT
    'ExpedienteAbierto_' || "CDEXPEDIENTE"    AS "ID",
    CAST(MIN("FCINICIO") AS TIMESTAMP)        AS "Time",
    'Alta del expediente'                     AS "Actividad",
    "CDEXPEDIENTE"                            AS "NatExpedientes"
FROM "GSTA_V_CEL_EXPEDIENTE"
WHERE "CDAPLICACION" = 'D032'
  AND "CDPROCEDIMIENTO" = '3163'
  AND "FCINICIO" IS NOT NULL
GROUP BY "CDEXPEDIENTE"
