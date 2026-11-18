-- Objeto NatExpedientes · atributos
-- Adaptado de PnCExpedientes (18/11/2026): mismo origen, filtro por la aplicación de Natalidad.
-- Cambios respecto a PnC: filtro D032 + procedimiento 3163 (D032 incluye otras ayudas de FJAS), sin el CASE de
-- procedimientos de PnC y sin las fechas duplicadas FCINICIO, FCRESOLUCION, FCFINTRAMITACION.
-- Los alias son los nombres de los atributos: declararlos igual en el objeto ("Add attributes").
SELECT
    e."CDEXPEDIENTE"                              AS "ID",
    e."CDAPLICACION"                              AS "Aplicacion",
    e."CDPROCEDIMIENTO"                           AS "CodigoProcedimiento",
    e."CDCONVOCATORIA"                            AS "CodigoConvocatoria",
    CAST(e."NMEJERCICIOCONV" AS VARCHAR)          AS "EjercicioConvocatoria",
    e."CDEXPEDIENTE"                              AS "CodigoExpediente",
    CAST(e."FCINICIO" AS TIMESTAMP)               AS "FechaInicio",
    CAST(e."FCRESOLUCION" AS TIMESTAMP)           AS "FechaResolucion",
    CAST(e."FCFINTRAMITACION" AS TIMESTAMP)       AS "FechaFinTramitacion",
    CAST(e."IDESTADO" AS VARCHAR)                 AS "IdEstado",
    e."DSESTADO"                                  AS "DescripcionEstado",
    e."USUARIOASIGNADO"                           AS "UsuarioAsignado",
    CAST(e."FCANULACION" AS TIMESTAMP)            AS "FechaAnulacion",
    CAST(e."IDUNIDAD" AS VARCHAR)                 AS "IdUnidad",
    e."DSUNIDAD"                                  AS "DescripcionUnidad",
    CAST(MIN(e."FC_SOL_INTERESADO") AS TIMESTAMP) AS "FechaPresentacionInteresado",
    CAST(MIN(e."FC_SOL_EREG") AS TIMESTAMP)       AS "FechaEntradaSistemaRegistro",
    CAST(MIN(e."FC_SOL_CONS") AS TIMESTAMP)       AS "FechaEntradaRegistroConsejeria",
    CAST(MIN(e."FCCIERRE") AS TIMESTAMP)          AS "FechaCierre"
FROM "GSTA_V_CEL_EXPEDIENTE" e
WHERE e."CDEXPEDIENTE" IS NOT NULL
  AND e."CDAPLICACION" = 'D032'                   -- aplicación de Infancia, Familia y Natalidad
  AND e."CDPROCEDIMIENTO" = '3163'                -- Natalidad: Sección de Ayudas Económicas a la Natalidad
GROUP BY
    e."CDEXPEDIENTE",
    e."CDAPLICACION",
    e."CDPROCEDIMIENTO",
    e."CDCONVOCATORIA",
    e."NMEJERCICIOCONV",
    e."FCINICIO",
    e."FCRESOLUCION",
    e."FCFINTRAMITACION",
    e."IDESTADO",
    e."DSESTADO",
    e."USUARIOASIGNADO",
    e."FCANULACION",
    e."IDUNIDAD",
    e."DSUNIDAD"
