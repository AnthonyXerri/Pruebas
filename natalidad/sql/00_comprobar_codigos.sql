-- Comprobación: qué aplicaciones y procedimientos hay en la vista de expedientes de Atlantix
-- Ejecutar con "Execute query" (no guardar como transformación). Solo devuelve códigos y recuentos.
SELECT
    "CDAPLICACION",
    "CDPROCEDIMIENTO",
    COUNT(DISTINCT "CDEXPEDIENTE") AS "Expedientes"
FROM "GSTA_V_CEL_EXPEDIENTE"
GROUP BY "CDAPLICACION", "CDPROCEDIMIENTO"
ORDER BY "CDAPLICACION", "CDPROCEDIMIENTO"
