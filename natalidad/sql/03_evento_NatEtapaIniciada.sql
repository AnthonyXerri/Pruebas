-- Evento NatEtapaIniciada · una fila por cada vez que un expediente de Natalidad entra en una etapa
-- Adaptado de PnCEtapaIniciada (18/11/2026). Cambios: filtro D032 + 3163, relaciones Nat*, "Fase" = fases del mockup v31.
-- Relaciones (crear antes en Related objects): involves one NatEtapas ("NatEtapas"), involves one NatExpedientes ("NatExpedientes").
-- Data Source: OCPM DataPool IMPLEMENTACION _Conexión Producción PRATLX_RO.
-- El ID lleva la fecha de inicio y un número de secuencia: si un expediente vuelve a una etapa, cada entrada es un evento (reprocesos).
WITH ETAPAS AS (
    SELECT DISTINCT
        E."CDEXPEDIENTE", E."IDETAPA", E."DSETAPA",
        E."FCINICIO", E."FCFIN", E."FCINICIO_SISTEMA", E."FCFIN_SISTEMA"
    FROM "GSTA_V_CEL_ETAPA" AS E
    INNER JOIN "GSTA_V_CEL_EXPEDIENTE" AS X
        ON E."CDEXPEDIENTE" = X."CDEXPEDIENTE"
       AND X."CDAPLICACION" = 'D032'
       AND X."CDPROCEDIMIENTO" = '3163'
    WHERE E."IDETAPA" IS NOT NULL
      AND E."FCINICIO" IS NOT NULL
),
SEC AS (
    SELECT ETAPAS.*,
           ROW_NUMBER() OVER (PARTITION BY "CDEXPEDIENTE", "IDETAPA", "FCINICIO"
                              ORDER BY "FCFIN" NULLS LAST, "FCINICIO_SISTEMA" NULLS LAST) AS rn
    FROM ETAPAS
)
SELECT
    'EtapaIniciada_' || "CDEXPEDIENTE" || '_' || CAST("IDETAPA" AS VARCHAR)
        || '_' || CAST("FCINICIO" AS VARCHAR) || '_' || CAST(rn AS VARCHAR)        AS "ID",
    CASE
        WHEN HOUR(CAST("FCINICIO" AS TIMESTAMP)) = 0
         AND MINUTE(CAST("FCINICIO" AS TIMESTAMP)) = 0
         AND SECOND(CAST("FCINICIO" AS TIMESTAMP)) = 0
         AND "FCINICIO_SISTEMA" IS NOT NULL
         AND CAST("FCINICIO_SISTEMA" AS DATE) = CAST("FCINICIO" AS DATE)
        THEN CAST("FCINICIO_SISTEMA" AS TIMESTAMP)
        ELSE CAST("FCINICIO" AS TIMESTAMP)
    END                                                                             AS "Time",
    'Inicio de la Etapa - ' || "DSETAPA"                                            AS "Actividad",
    "DSETAPA"                                                                       AS "Etapas",
    CAST("FCINICIO" AS TIMESTAMP)                                                   AS "Fecha Inicio Etapa",
    CAST("FCFIN" AS TIMESTAMP)                                                      AS "Fecha Fin Etapa",
    'Etapa_' || CAST("IDETAPA" AS VARCHAR) || '_' || "CDEXPEDIENTE"                 AS "NatEtapas",
    "CDEXPEDIENTE"                                                                  AS "NatExpedientes",
    CASE
        WHEN "DSETAPA" IN ('GESTIÓN EXPEDIENTE', 'REQUERIMIENTO')
            THEN '2. Gestión del expediente'
        WHEN "DSETAPA" IN ('PROPUESTA FAVORABLE', 'VALIDACIÓN TERCERO')
            THEN '3. Validación de terceros'
        WHEN "DSETAPA" IN ('PTE. ENVÍO INTERVENCIÓN', 'INTERVENCIÓN CONCESIÓN',
                           'ACTUACIÓN INTERESADA CONCESIÓN', 'DEV A INSTANCIA PROMO CONCESIÓN')
            THEN '4. Intervención'
        WHEN "DSETAPA" IN ('FAVORABLE CONCESIÓN', 'FAVORABLE CON OBS CONCESIÓN', 'RESOLUCIÓN FAVORABLE')
            THEN '5. Resolución y pago'
        WHEN "DSETAPA" IN ('RESOLUCIÓN DENEGACIÓN', 'RESOLUCIÓN DESESTIMIENTO')
            THEN 'Fin sin concesión'
        WHEN "DSETAPA" IN ('PTE. ENVIO INTERV. PAGO UNICO', 'INTERVENCION PAGO UNICO')
            THEN 'Pago único'
        WHEN "DSETAPA" IS NOT NULL
            THEN 'Mantenimiento'
    END                                                                             AS "Fase"
FROM SEC
