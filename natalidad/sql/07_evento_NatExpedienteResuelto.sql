-- Evento NatExpedienteResuelto · resolución del expediente (fin de la tramitación)
-- Adaptado de PnCExpedienteResuelto (18/11/2026). Cambios:
--   * Filtro D032 + 3163, relación NatExpedientes.
--   * Plantillas de Natalidad por NOMBRE (sus códigos cambian cada convocatoria): resolución/notificación favorable,
--     denegatoria y desistimiento; se excluyen los «Informe RR» (recursos).
--   * Time = firma del documento (si está firmado, ITESTADO = 'F') > generación del documento > FCRESOLUCION
--     (FCRESOLUCION viene a las 00:00 y por lotes; la firma lleva hora real).
-- Relación (crear antes): involves one NatExpedientes ("NatExpedientes"). Data Source: PRATLX_RO.
-- DES_STIMIENTO: el guion bajo vale por una letra cualquiera (DESESTIMIENTO y DESISTIMIENTO).
WITH EXP AS (
    SELECT "CDEXPEDIENTE",
           MIN("FCRESOLUCION") AS "FCRESOLUCION"
    FROM "GSTA_V_CEL_EXPEDIENTE"
    WHERE "CDAPLICACION" = 'D032'
      AND "CDPROCEDIMIENTO" = '3163'
    GROUP BY "CDEXPEDIENTE"
),
DOC AS (
    SELECT * FROM (
        SELECT D."CDEXPEDIENTE", D."FCGENERACION", D."FCFIRMARECHAZO",
               D."CDPLANTILLA", D."DSPLANTILLA", D."ITESTADO",
               CASE
                   WHEN UPPER(D."DSPLANTILLA") LIKE '%DENEGATORIA%'   THEN 'Denegación'
                   WHEN UPPER(D."DSPLANTILLA") LIKE '%DES_STIMIENTO%' THEN 'Desistimiento'
                   ELSE 'Favorable'
               END AS "Sentido",
               ROW_NUMBER() OVER (PARTITION BY D."CDEXPEDIENTE"
                                  ORDER BY D."FCGENERACION", D."CDPLANTILLA") AS rn
        FROM "GSTA_V_CEL_DOC_ELABORADA" AS D
        WHERE D."FCGENERACION" IS NOT NULL
          AND UPPER(D."DSPLANTILLA") NOT LIKE '%INFORME%'
          AND (   UPPER(D."DSPLANTILLA") LIKE '%RESOLUCI%FAVORABLE%'
               OR UPPER(D."DSPLANTILLA") LIKE '%DENEGATORIA%'
               OR UPPER(D."DSPLANTILLA") LIKE '%DES_STIMIENTO%')
    ) AS X
    WHERE X.rn = 1
)
SELECT
    'ExpedienteResuelto_' || E."CDEXPEDIENTE"                         AS "ID",
    CAST(COALESCE(CASE WHEN D."ITESTADO" = 'F' THEN D."FCFIRMARECHAZO" END,
                  D."FCGENERACION",
                  E."FCRESOLUCION") AS TIMESTAMP)                     AS "Time",
    'Expediente resuelto'                                              AS "Actividad",
    CAST(E."FCRESOLUCION"   AS TIMESTAMP)                              AS "FechaResolucionExpediente",
    CAST(D."FCGENERACION"   AS TIMESTAMP)                              AS "FechaGeneracionResolucion",
    CAST(D."FCFIRMARECHAZO" AS TIMESTAMP)                              AS "FechaFirmaRechazoResolucion",
    CASE WHEN D."ITESTADO" = 'F' AND D."FCFIRMARECHAZO" IS NOT NULL THEN 'Firma del documento'
         WHEN D."FCGENERACION" IS NOT NULL                            THEN 'Generación del documento'
         ELSE 'FCRESOLUCION' END                                       AS "OrigenFecha",
    COALESCE(D."Sentido", 'Sin documento')                             AS "SentidoResolucion",
    CAST(D."CDPLANTILLA" AS VARCHAR)                                   AS "CodigoPlantilla",
    D."DSPLANTILLA"                                                    AS "DescripcionPlantilla",
    D."ITESTADO"                                                       AS "EstadoDocumento",
    E."CDEXPEDIENTE"                                                   AS "NatExpedientes"
FROM EXP AS E
LEFT JOIN DOC AS D
  ON E."CDEXPEDIENTE" = D."CDEXPEDIENTE"
WHERE E."FCRESOLUCION" IS NOT NULL
   OR D."CDEXPEDIENTE" IS NOT NULL
