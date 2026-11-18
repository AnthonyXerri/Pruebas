-- Objeto NatEtapas · atributos
-- Adaptado de PnCEtapas (18/11/2026). Una fila por cada etapa por la que pasa cada expediente de Natalidad.
-- Patrón de Roberto: CTE con los expedientes de Natalidad + INNER JOIN (solo quedan las etapas de esos expedientes).
-- La columna "NatExpedientes" es la relación con el objeto NatExpedientes (FK; relación 1 — N creada antes).
-- Data Source: OCPM DataPool IMPLEMENTACION _Conexión Producción PRATLX_RO.
-- IDETAPA cambia cada convocatoria/año: para agrupar se usa DSETAPA. "Fase" = fases del mockup v31 (const FASES).
WITH Expedientes AS (
    SELECT DISTINCT CDEXPEDIENTE
    FROM "GSTA_V_CEL_EXPEDIENTE"
    WHERE CDAPLICACION = 'D032'
      AND CDPROCEDIMIENTO = '3163'
)
SELECT DISTINCT
    'Etapa_' || CAST("IDETAPA" AS VARCHAR) || '_' || "GSTA_V_CEL_ETAPA"."CDEXPEDIENTE" AS "ID",
    CAST("IDETAPA" AS VARCHAR)            AS "IDEtapa",
    "DSETAPA"                             AS "DescripcionEtapa",
    "CONFISCALIZACION"                    AS "Confiscalizacion",
    CASE   -- fases del mockup v31 (FASES): 1. Entrada no es etapa de Atlantix (sale de las fechas del expediente)
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
    END                                   AS "Fase",
    "GSTA_V_CEL_ETAPA"."CDEXPEDIENTE"     AS "NatExpedientes"
FROM "GSTA_V_CEL_ETAPA"
INNER JOIN Expedientes
        ON "GSTA_V_CEL_ETAPA".CDEXPEDIENTE = Expedientes.CDEXPEDIENTE
WHERE "IDETAPA" IS NOT NULL
