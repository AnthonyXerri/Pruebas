-- Evento NatNotificaciones · una fila por notificación de un expediente de Natalidad (GSTA_V_CEL_NOTIFICACION)
-- Adaptado de PnCNotificaciones (18/11/2026). Cambios respecto a PnC:
--   * Filtro D032 + 3163, relación NatExpedientes.
--   * PnC solo crea el acuse (Time = FCACUSE, y descarta las que no tienen acuse). Aquí Time = FCNOTIFICACION
--     (envío / puesta a disposición) y se guardan TODAS, con la fecha de acuse como atributo: así se puede calcular el
--     plazo de aportación del requerimiento y ver las que no tienen acuse. El acuse como actividad ya está en
--     NatActividadRealizada («Acuse de Recibo»).
--   * TipoNotificacion a partir del título (catálogo del 18/11): Requerimiento / Resolución favorable / desistimiento /
--     denegación / Resolución (sin sentido en el título: «RESOLUCIÓN», «RESOLUCIÓN 2022», «AEN RESOLUCIÓN MARZO 2023»…) / …
--     El sentido de esas resoluciones genéricas sale de NatExpedienteResuelto.
-- Relación (crear antes): involves one NatExpedientes ("NatExpedientes"). Data Source: PRATLX_RO.
WITH NOTIF AS (
    SELECT N."CDEXPEDIENTE", N."CDNOTIFICACION", N."TITULO", N."FCNOTIFICACION", N."FCACUSE",
           ROW_NUMBER() OVER (PARTITION BY N."CDEXPEDIENTE", N."CDNOTIFICACION"
                              ORDER BY CASE WHEN N."FCACUSE" IS NULL THEN 1 ELSE 0 END,
                                       N."FCACUSE" DESC) AS rn
    FROM "GSTA_V_CEL_NOTIFICACION" AS N
    INNER JOIN (
        SELECT DISTINCT "CDEXPEDIENTE"
        FROM "GSTA_V_CEL_EXPEDIENTE"
        WHERE "CDAPLICACION" = 'D032'
          AND "CDPROCEDIMIENTO" = '3163'
    ) AS E
        ON N."CDEXPEDIENTE" = E."CDEXPEDIENTE"
    WHERE N."FCNOTIFICACION" IS NOT NULL
),
TIPO AS (
    SELECT NOTIF.*,
           CASE
               WHEN UPPER("TITULO") LIKE '%REQUERIMIENTO%'   THEN 'Requerimiento'
               WHEN UPPER("TITULO") LIKE '%DES_STIMIENTO%'   THEN 'Resolución desistimiento'
               WHEN UPPER("TITULO") LIKE '%DENEGA%'          THEN 'Resolución denegación'
               WHEN UPPER("TITULO") LIKE '%FAVORABLE%'
                 OR UPPER("TITULO") LIKE '%RESOLUCI% FAV %'
                 OR UPPER("TITULO") LIKE '%APROBA%'          THEN 'Resolución favorable'
               WHEN UPPER("TITULO") LIKE '%RESOLUCI%'        THEN 'Resolución (sin sentido en el título)'
               WHEN UPPER("TITULO") LIKE '%MODIFICACI%'      THEN 'Modificación'
               WHEN UPPER("TITULO") LIKE '%BAJA%'            THEN 'Baja'
               WHEN UPPER("TITULO") LIKE '%REINTEGRO%'       THEN 'Reintegro'
               ELSE 'Otra'
           END AS "TipoNotificacion"
    FROM NOTIF
    WHERE rn = 1
)
SELECT
    'Notificacion-' || "CDEXPEDIENTE" || '-' || CAST("CDNOTIFICACION" AS VARCHAR) AS "ID",
    CAST("FCNOTIFICACION" AS TIMESTAMP)                       AS "Time",
    "CDEXPEDIENTE"                                            AS "NatExpedientes",
    'Notificación - ' || "TipoNotificacion"                   AS "Actividad",
    "TipoNotificacion"                                        AS "TipoNotificacion",
    CAST("FCNOTIFICACION" AS TIMESTAMP)                       AS "Fecha Notificacion",
    CAST("FCACUSE" AS TIMESTAMP)                              AS "Fecha Acuse",
    CASE WHEN "FCACUSE" IS NOT NULL THEN 'S' ELSE 'N' END     AS "ConAcuse",
    "TITULO"                                                  AS "Titulo"
FROM TIPO
