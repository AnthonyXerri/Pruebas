-- Comprobación (no guardar): plantillas de documentos elaborados en los expedientes de Natalidad.
-- Para saber qué plantillas son resoluciones (favorable, denegatoria, desistimiento), requerimientos, etc.
SELECT
    CAST(D."CDPLANTILLA" AS VARCHAR) || ' | ' || COALESCE(D."DSPLANTILLA", '-')
    || ' | ' || CAST(COUNT(*) AS VARCHAR) || ' docs'
    || ' | ' || CAST(COUNT(DISTINCT D."CDEXPEDIENTE") AS VARCHAR) || ' exp'
    || ' | firmados ' || CAST(SUM(CASE WHEN D."FCFIRMARECHAZO" IS NOT NULL THEN 1 ELSE 0 END) AS VARCHAR) AS "ID"
FROM "GSTA_V_CEL_DOC_ELABORADA" D
WHERE D."CDEXPEDIENTE" IN (
    SELECT "CDEXPEDIENTE"
    FROM "GSTA_V_CEL_EXPEDIENTE"
    WHERE "CDAPLICACION" = 'D032' AND "CDPROCEDIMIENTO" = '3163'
)
GROUP BY D."CDPLANTILLA", D."DSPLANTILLA"
ORDER BY COUNT(*) DESC
LIMIT 80
