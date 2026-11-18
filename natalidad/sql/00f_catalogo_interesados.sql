-- Comprobación (no guardar): tipos de interesado y de documento en los expedientes de Natalidad. Solo recuentos.
SELECT
    COALESCE(CAST(I."TIPO" AS VARCHAR), '-')
    || ' | ' || COALESCE(I."DS_TIPO_DOCUMENTO", '-')
    || ' | grupo ' || COALESCE(CAST(I."GRUPO_INTE" AS VARCHAR), '-')
    || ' | principal ' || COALESCE(I."IT_PRINCIPAL", '-')
    || ' | ' || CAST(COUNT(*) AS VARCHAR) || ' interesados' AS "ID"
FROM "GSTA_V_INTERESADOS" I
WHERE I."CD_EXPEDIENTE" IN (
    SELECT "CDEXPEDIENTE"
    FROM "GSTA_V_CEL_EXPEDIENTE"
    WHERE "CDAPLICACION" = 'D032' AND "CDPROCEDIMIENTO" = '3163'
)
GROUP BY I."TIPO", I."DS_TIPO_DOCUMENTO", I."GRUPO_INTE", I."IT_PRINCIPAL"
ORDER BY COUNT(*) DESC
LIMIT 40
