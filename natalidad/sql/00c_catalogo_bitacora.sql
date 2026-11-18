-- Comprobación (no guardar): catálogo de la bitácora de Atlantix (GSTA_REGISTRO_ACTIVIDAD) para Natalidad.
-- Qué actividades se graban, si son automáticas y cuántas veces / en cuántos expedientes. Sin usuarios ni expedientes.
SELECT
    COALESCE(R."DS_REGISTRO", '-')
    || ' | auto ' || COALESCE(CAST(R."IT_AUTOMATICO" AS VARCHAR), '-')
    || ' | ' || CAST(COUNT(*) AS VARCHAR) || ' veces'
    || ' | ' || CAST(COUNT(DISTINCT R."CD_EXPEDIENTE") AS VARCHAR) || ' exp' AS "ID"
FROM "GSTA_REGISTRO_ACTIVIDAD" R
WHERE R."CD_EXPEDIENTE" IN (
    SELECT "CDEXPEDIENTE"
    FROM "GSTA_V_CEL_EXPEDIENTE"
    WHERE "CDAPLICACION" = 'D032' AND "CDPROCEDIMIENTO" = '3163'
)
GROUP BY R."DS_REGISTRO", R."IT_AUTOMATICO"
ORDER BY COUNT(*) DESC
LIMIT 80
