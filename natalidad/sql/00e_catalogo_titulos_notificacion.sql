-- Comprobación (no guardar): títulos de las notificaciones de Natalidad, sin el número de expediente del principio.
-- El motor de validación NO admite POSITION. Los títulos de Natalidad empiezan por el expediente con formato fijo
-- «08-AFN1-00012.2/2022 - » (23 caracteres): si el título encaja, se toma desde el carácter 24 con SUBSTRING(... FROM 24).
-- CHAR_LENGTH tampoco está admitido.
SELECT
    UPPER(CASE WHEN N."TITULO" LIKE '08-AFN%/20__ - %'
               THEN SUBSTRING(N."TITULO" FROM 24)
               ELSE N."TITULO" END)
    || ' | ' || CAST(COUNT(*) AS VARCHAR) || ' notif'
    || ' | con acuse ' || CAST(SUM(CASE WHEN N."FCACUSE" IS NOT NULL THEN 1 ELSE 0 END) AS VARCHAR) AS "ID"
FROM "GSTA_V_CEL_NOTIFICACION" N
WHERE N."CDEXPEDIENTE" IN (
    SELECT "CDEXPEDIENTE"
    FROM "GSTA_V_CEL_EXPEDIENTE"
    WHERE "CDAPLICACION" = 'D032' AND "CDPROCEDIMIENTO" = '3163'
)
GROUP BY UPPER(CASE WHEN N."TITULO" LIKE '08-AFN%/20__ - %'
                    THEN SUBSTRING(N."TITULO" FROM 24)
                    ELSE N."TITULO" END)
ORDER BY COUNT(*) DESC
LIMIT 60
