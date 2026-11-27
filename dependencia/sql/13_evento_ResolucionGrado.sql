-- Evento ResolucionGrado (27/11/2026): resolución de grado firmada (hito 9).
-- Pegar sin punto y coma. Data Source: None (Global). Se excluyen las resoluciones dadas de baja.
SELECT
    'RG_' || CAST(r."IDRESOLUCION" AS VARCHAR) AS "ID",
    r."FCRESOLUCION"                 AS "Time",
    CAST(r."IDSOLICITUD" AS VARCHAR) AS "SolicitudDependencia",
    r."CDTIPODOCUMENTO"              AS "CodigoTipoResolucion",
    t."DSTIPODOCUMENTO"              AS "TipoResolucion",
    r."IT_ELA"                       AS "ViaELA",
    r."IDALTA"                       AS "Usuario"
FROM "SIDM_MR_RESOLUCIONES" r
LEFT JOIN "SIDM_MR_TIPOS_DOCUMENTOS" t ON t."CDTIPODOCUMENTO" = r."CDTIPODOCUMENTO"
WHERE r."FCRESOLUCION" IS NOT NULL
  AND r."FCBAJA" IS NULL
