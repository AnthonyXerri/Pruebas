-- Evento NatEtapaFinalizada · una fila por cada vez que un expediente de Natalidad sale de una etapa
-- Adaptado de PnCEtapaFinalizada (18/11/2026). Cambios: filtro D032 + 3163, relaciones Nat*, "Fase" = fases del mockup v31.
-- Relaciones (crear antes en Related objects): involves one NatEtapas ("NatEtapas"), involves one NatExpedientes ("NatExpedientes").
-- Data Source: OCPM DataPool IMPLEMENTACION _Conexión Producción PRATLX_RO.
-- Mismo ID que NatEtapaIniciada (con la fecha de INICIO) para emparejar entrada y salida. Solo etapas ya cerradas (FCFIN no nulo).
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
    'EtapaFinalizada_' || "CDEXPEDIENTE" || '_' || CAST("IDETAPA" AS VARCHAR)
        || '_' || CAST("FCINICIO" AS VARCHAR) || '_' || CAST(rn AS VARCHAR)        AS "ID",
    CASE
        WHEN HOUR(CAST("FCFIN" AS TIMESTAMP)) = 0
         AND MINUTE(CAST("FCFIN" AS TIMESTAMP)) = 0
         AND SECOND(CAST("FCFIN" AS TIMESTAMP)) = 0
         AND "FCFIN_SISTEMA" IS NOT NULL
         AND CAST("FCFIN_SISTEMA" AS DATE) = CAST("FCFIN" AS DATE)
        THEN CAST("FCFIN_SISTEMA" AS TIMESTAMP)
        ELSE CAST("FCFIN" AS TIMESTAMP)
    END                                                                             AS "Time",
    'Finalización de la Etapa - ' || "DSETAPA"                                            AS "Actividad",
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
        WHEN "DSETAPA" IN ('MODIFICACIÓN CONCESIÓN', 'RESOLUCIÓN MODIFICACIÓN', 'RESOLUCIÓN BAJA',
                           'PTE.ENVÍO MODIFICACIÓN ECONÓM. NEGATIVA', 'PTE.ENVÍO MODIFICACIÓN ECONÓM. POSITIVA',
                           'PTE.ENVÍO MODIFICACIÓN SIN REPERC. ECONÓM.', 'PTE.ENVÍO BAJA DE LA AYUDA',
                           'INTERV INCIDEND. NEGATIVA', 'INTERV INCIDEND. POSITIVA', 'INTERV INCIDEND. BAJA AYUDA',
                           'INTERV SIN VARIAC. IMP. AYUDA', 'FAVORABLE INCIDENCIA', 'FAVORABLE CON OBS INCIDENCIA',
                           'DEV A INSTANCIA PROMO INCIDENCIA', 'ACTUACIÓN INTERESADA INCIDENCIA')
            THEN 'Mantenimiento'
        WHEN "DSETAPA" IN ('PTE. ENVIO INTERV. PAGO UNICO', 'INTERVENCION PAGO UNICO')
            THEN 'Pago único'
        ELSE 'Sin clasificar'
    END                                                                             AS "Fase"
FROM SEC
WHERE "FCFIN" IS NOT NULL
