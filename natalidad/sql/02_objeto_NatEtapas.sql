-- Objeto NatEtapas · atributos
-- Adaptado de PnCEtapas (18/11/2026). Una fila por cada etapa por la que pasa cada expediente de Natalidad.
-- Patrón de Roberto: CTE con los expedientes de Natalidad + INNER JOIN (solo quedan las etapas de esos expedientes).
-- La columna "NatExpedientes" es la relación con el objeto NatExpedientes (crear antes la relación en Related objects).
WITH Expedientes AS (
    SELECT DISTINCT CDEXPEDIENTE
    FROM "GSTA_V_CEL_EXPEDIENTE"
    WHERE CDAPLICACION = 'D032'
      AND CDPROCEDIMIENTO = '3163'
)
SELECT DISTINCT
    'Etapa_' || CAST("IDETAPA" AS VARCHAR) || '_' || "GSTA_V_CEL_ETAPA"."CDEXPEDIENTE" AS "ID",
    CAST("IDETAPA" AS VARCHAR)            AS "IDEtapa",
    "DSETAPA"                             AS "DescripcionEtapa",
    "CONFISCALIZACION"                    AS "Confiscalizacion",
    "GSTA_V_CEL_ETAPA"."CDEXPEDIENTE"     AS "NatExpedientes"
FROM "GSTA_V_CEL_ETAPA"
INNER JOIN Expedientes
        ON "GSTA_V_CEL_ETAPA".CDEXPEDIENTE = Expedientes.CDEXPEDIENTE
WHERE "IDETAPA" IS NOT NULL
