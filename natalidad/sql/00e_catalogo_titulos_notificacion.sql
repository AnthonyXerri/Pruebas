-- Comprobación (no guardar): títulos de las notificaciones de Natalidad, sin el número de expediente del principio.
-- POSITION busca dónde está el primer ' - '; SUBSTRING corta a partir de ahí. Si no hay ' - ', se deja el título entero.
SELECT
    UPPER(CASE WHEN POSITION(' - ' IN N."TITULO") > 0
               THEN SUBSTRING(N."TITULO", POSITION(' - ' IN N."TITULO") + 3)
               ELSE N."TITULO" END)
    || ' | ' || CAST(COUNT(*) AS VARCHAR) || ' notif'
    || ' | con acuse ' || CAST(SUM(CASE WHEN N."FCACUSE" IS NOT NULL THEN 1 ELSE 0 END) AS VARCHAR) AS "ID"
FROM "GSTA_V_CEL_NOTIFICACION" N
WHERE N."CDEXPEDIENTE" IN (
    SELECT "CDEXPEDIENTE"
    FROM "GSTA_V_CEL_EXPEDIENTE"
    WHERE "CDAPLICACION" = 'D032' AND "CDPROCEDIMIENTO" = '3163'
)
GROUP BY UPPER(CASE WHEN POSITION(' - ' IN N."TITULO") > 0
                    THEN SUBSTRING(N."TITULO", POSITION(' - ' IN N."TITULO") + 3)
                    ELSE N."TITULO" END)
ORDER BY COUNT(*) DESC
LIMIT 60
