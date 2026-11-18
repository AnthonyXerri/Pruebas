-- Objeto NatInteresados · interesados de los expedientes de Natalidad (solicitante y representantes)
-- Adaptado de PnCInteresados (18/11/2026). Cambios:
--   * Filtro D032 + 3163; relación NatExpedientes (FK, NatExpedientes 1 — N NatInteresados).
--   * Sin datos que identifiquen: ni fecha de nacimiento (solo TramoEdad), ni nombre, documento, contacto o domicilio;
--     sin el municipio de notificación.
--   * Sin nacionalidad real (en PnC sale de PNCA_INTERESADO, propia de PnC): aproximación por tipo de documento
--     (NIF → española; NIE/pasaporte → extranjera). A confirmar con la unidad; la real hay que pedirla.
--   * EsSolicitante = TIPO 'Interesado' y principal 'S' (≈ 53.360, uno por expediente; catálogo del 18/11).
--   * Edad en la fecha de presentación (como PnC); válida entre 14 y 110, si no «No informado».
-- Data Source: PRATLX_RO.
WITH PRESENTACION AS (
    SELECT "CDEXPEDIENTE",
           CAST(MIN(COALESCE("FC_SOL_INTERESADO", "FCINICIO")) AS DATE) AS "FC_PRESENTACION"
    FROM "GSTA_V_CEL_EXPEDIENTE"
    WHERE "CDAPLICACION" = 'D032'
      AND "CDPROCEDIMIENTO" = '3163'
    GROUP BY "CDEXPEDIENTE"
),
BASE AS (
    SELECT
        I."CD_INTERESADO", I."CD_EXPEDIENTE", I."TIPO", I."DS_TIPO_DOCUMENTO", I."IT_PRINCIPAL",
        I."DS_MEDIO_NOTIF", I."CDPROV_RESID", I."DSPROV_RESID", I."CDMUNI_RESID", I."DSMUNI_RESID",
        CASE WHEN I."FC_NACIMIENTO" <= P."FC_PRESENTACION"
             THEN YEAR(P."FC_PRESENTACION") - YEAR(I."FC_NACIMIENTO")
                  - CASE WHEN MONTH(P."FC_PRESENTACION") < MONTH(I."FC_NACIMIENTO") THEN 1
                         WHEN MONTH(P."FC_PRESENTACION") = MONTH(I."FC_NACIMIENTO")
                          AND DAYOFMONTH(P."FC_PRESENTACION") < DAYOFMONTH(I."FC_NACIMIENTO") THEN 1
                         ELSE 0 END
        END AS "EDAD"
    FROM "GSTA_V_INTERESADOS" AS I
    INNER JOIN PRESENTACION AS P
        ON I."CD_EXPEDIENTE" = P."CDEXPEDIENTE"
)
SELECT DISTINCT
    'interesado_' || CAST("CD_INTERESADO" AS VARCHAR) || '_' || "CD_EXPEDIENTE"   AS "ID",
    "CD_EXPEDIENTE"                                                             AS "NatExpedientes",
    "TIPO"                                                                      AS "TipoInteresado",
    "IT_PRINCIPAL"                                                              AS "EsPrincipal",
    CASE WHEN "TIPO" = 'Interesado' AND "IT_PRINCIPAL" = 'S' THEN 'S' ELSE 'N' END AS "EsSolicitante",
    "DS_TIPO_DOCUMENTO"                                                         AS "TipoDocumento",
    CASE WHEN "DS_TIPO_DOCUMENTO" = 'NIF'                    THEN 'Española (DNI)'
         WHEN "DS_TIPO_DOCUMENTO" IN ('NIE', 'Pasaporte')    THEN 'Extranjera (NIE o pasaporte)'
         WHEN "DS_TIPO_DOCUMENTO" = 'CIF'                    THEN 'Persona jurídica'
         ELSE 'No informado' END                                                AS "NacionalidadAprox",
    CASE WHEN "EDAD" IS NULL OR "EDAD" < 14 OR "EDAD" > 110 THEN 'No informado'
         WHEN "EDAD" < 20 THEN '1. Menos de 20'
         WHEN "EDAD" < 25 THEN '2. 20-24'
         WHEN "EDAD" < 30 THEN '3. 25-29'
         WHEN "EDAD" < 35 THEN '4. 30-34'
         WHEN "EDAD" < 40 THEN '5. 35-39'
         ELSE '6. 40 o más' END                                                 AS "TramoEdad",
    "DS_MEDIO_NOTIF"                                                            AS "MedioNotificacion",
    CAST("CDPROV_RESID" AS VARCHAR)                                             AS "CdProvincia",
    "DSPROV_RESID"                                                              AS "Provincia",
    CAST("CDMUNI_RESID" AS VARCHAR)                                             AS "CdMunicipio",
    "DSMUNI_RESID"                                                              AS "Municipio"
FROM BASE
