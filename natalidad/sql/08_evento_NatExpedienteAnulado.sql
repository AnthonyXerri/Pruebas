-- Evento NatExpedienteAnulado · anulación del expediente en Atlantix
-- Adaptado de PnCExpedienteAnulado (18/11/2026). Cambios: filtro D032 + 3163, relación NatExpedientes.
-- Relación (crear antes): involves one NatExpedientes ("NatExpedientes"). Data Source: PRATLX_RO.
SELECT
    'ExpedienteAnulado_' || "CDEXPEDIENTE"    AS "ID",
    CAST(MIN("FCANULACION") AS TIMESTAMP)     AS "Time",
    'Expediente anulado'                      AS "Actividad",
    "CDEXPEDIENTE"                            AS "NatExpedientes"
FROM "GSTA_V_CEL_EXPEDIENTE"
WHERE "CDAPLICACION" = 'D032'
  AND "CDPROCEDIMIENTO" = '3163'
  AND "FCANULACION" IS NOT NULL
GROUP BY "CDEXPEDIENTE"
