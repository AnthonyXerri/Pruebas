-- Objeto ValoradorDependencia (27/11/2026). Pegar sin punto y coma. Data Source: None (Global).
-- Parte 1: los valoradores del maestro SIDM_DATOS_VALORADOR.
-- Parte 2: los códigos que aparecen en valoraciones o dictámenes pero NO están en el maestro
--          (en la muestra del 27/11 hay uno). Se crean sin atributos para que la relación
--          Valoracion -> Valorador no quede rota. Pregunta abierta para Andrés: ¿quiénes son?
SELECT
    v."CDVALORADOR"            AS "ID",
    v."NOMBRE_VALORADOR"       AS "Nombre",
    v."CDTURNO"                AS "Turno",                  -- M o T
    v."CDPERFIL_VALORADOR"     AS "Perfil",
    v."CDZONADEP"              AS "Zona",
    v."IT_VALORADOR_ENCOMIENDA" AS "Encomienda",            -- propio o externo (por confirmar)
    v."LOGIN"                  AS "Login",                  -- para cruzar con IDMODI del histórico
    v."FCBAJA"                 AS "FechaBaja",
    'Maestro'                  AS "Fuente"
FROM "SIDM_DATOS_VALORADOR" v
UNION ALL
SELECT
    x."CDVALORADOR",
    CAST(NULL AS VARCHAR), CAST(NULL AS VARCHAR), CAST(NULL AS VARCHAR), CAST(NULL AS VARCHAR),
    CAST(NULL AS VARCHAR), CAST(NULL AS VARCHAR), CAST(NULL AS TIMESTAMP),
    'Sin maestro'
FROM (
    SELECT "CDVALORADOR" FROM "SIDM_VALORACION_BVD"
    UNION
    SELECT "CDVALORADOR" FROM "SIDM_VALORACION_EVE"
    UNION
    SELECT "CDVALORADOR" FROM "SIDM_DICTAMEN_TECNICO"
) x
WHERE x."CDVALORADOR" IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM "SIDM_DATOS_VALORADOR" d WHERE d."CDVALORADOR" = x."CDVALORADOR")
