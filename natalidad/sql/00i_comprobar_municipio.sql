-- Comprobación (no guardar): cuántas solicitantes del 3163 tienen informado el municipio de residencia, por año de alta.
-- Solo recuentos, sin datos personales. Se ejecuta con «Execute query selection».
SELECT
    CAST(YEAR(E."FCINICIO") AS VARCHAR)
    || ' | solicitantes ' || CAST(COUNT(*) AS VARCHAR)
    || ' | con municipio ' || CAST(SUM(CASE WHEN I."DSMUNI_RESID" IS NOT NULL AND I."DSMUNI_RESID" <> '' THEN 1 ELSE 0 END) AS VARCHAR)
    || ' | con provincia ' || CAST(SUM(CASE WHEN I."DSPROV_RESID" IS NOT NULL AND I."DSPROV_RESID" <> '' THEN 1 ELSE 0 END) AS VARCHAR) AS "ID"
FROM "GSTA_V_INTERESADOS" I
JOIN "GSTA_V_CEL_EXPEDIENTE" E ON E."CDEXPEDIENTE" = I."CD_EXPEDIENTE"
WHERE E."CDAPLICACION" = 'D032' AND E."CDPROCEDIMIENTO" = '3163'
  AND I."TIPO" = 'Interesado' AND I."IT_PRINCIPAL" = 'S'
GROUP BY YEAR(E."FCINICIO")
ORDER BY YEAR(E."FCINICIO")
