-- Objeto SolicitudDependencia · v2 (27/11/2026): la 01 + persona, territorio, origen, grado y resolución.
-- Pegar en Objects & Events sin el punto y coma final. Data Source: None (Global).
-- Los alias son los nombres de los atributos: declararlos igual en el tipo de objeto.
-- 27/11 (auditoría): añadido Origen (DSORIGENDOC de la bandeja, preferida la de altas iniciales "INI").
-- En la muestra no cruza (la bandeja cargada son entradas sin grabar), pero en producción sí.
-- La edad NO se calcula aquí: se guarda FechaNacimiento y la View la calcula en PQL
-- (YEARS_BETWEEN), así se puede elegir "edad al solicitar" o "edad hoy" sin tocar el modelo.
SELECT
    CAST(s."IDSOLICITUD" AS VARCHAR) AS "ID",
    s."NMSOLICITUD"   AS "NumeroSolicitud",
    s."FCSOLICITUD"   AS "FechaSolicitud",
    s."FCREGENTRADA"  AS "FechaRegistroEntrada",
    s."FCALTA"        AS "FechaAlta",
    s."FC_FIN_PLAZO"  AS "FechaFinPlazo",
    s."FCBAJA"        AS "FechaBaja",
    s."CDESTADO"      AS "CodigoEstadoActual",
    e."DSESTADO"      AS "EstadoActual",
    s."CDTIPO"        AS "TipoSolicitud",
    s."IT_URGENTE"    AS "Urgente",
    s."IT_TRASLADO"   AS "Traslado",
    s."ITEXTINGUIDO"  AS "Extinguido",
    s."NMREVISION"    AS "NumeroRevision",
    CAST(s."IDSOLICITUD_ORIG_REVISION" AS VARCHAR) AS "IdSolicitudOriginal",
    s."IDALTA"        AS "UsuarioAlta",
    CAST(s."IDSOLICITANTE" AS VARCHAR) AS "IdSolicitante",
    -- Nuevos (27/11) ----------------------------------------------------------
    p."FCNACIMIENTO"  AS "FechaNacimiento",                 -- edad: en PQL
    p."ITSEXO"        AS "Sexo",
    m."DSMUNI"        AS "Municipio",
    p."CDZONADEP"     AS "ZonaDependencia",
    p."CDDISTRITO"    AS "Distrito",                        -- solo Madrid capital
    p."FCFALLEC_INE"  AS "FechaFallecimiento",
    ma."DSMOTALTA"    AS "MotivoAlta",                      -- Alta ORVE / Simple / con Servicios
    CAST(d."CDGRADO" AS VARCHAR) AS "CodigoGrado",          -- entero en origen: se pasa a texto
    d."DSGRADO_NIVEL" AS "GradoNivel",
    d."CDTIPO_BAREMO" AS "TipoBaremo",                      -- BVD o EVE
    r."DSTIPODOCUMENTO" AS "TipoResolucionGrado",
    r."FCRESOLUCION"  AS "FechaResolucionGrado",
    o."DSORIGENDOC"   AS "Origen"                           -- canal: ORVE / Presencial / Internet (bandeja)
FROM "SIDM_SOLICITUD" s
LEFT JOIN "SIDM_ESTADO_SOLICITUD" e
       ON RIGHT(e."CDESTADO", 2) = RIGHT(s."CDESTADO", 2)
LEFT JOIN "SIDM_SOLICITANTE" p
       ON CAST(p."IDSOLICITANTE" AS VARCHAR) = CAST(s."IDSOLICITANTE" AS VARCHAR)
LEFT JOIN "SUCA_MUNICIPIO" m                                -- CDMUNI llega a veces sin ceros: LPAD
       ON m."CDPROV" = LPAD(p."CDPROV", 2, '0')
      AND m."CDMUNI" = LPAD(p."CDMUNI", 3, '0')
LEFT JOIN "SIDM_MOTALTA" ma
       ON ma."CDMOTALTA" = s."CDMOTALTA"
LEFT JOIN (                                                 -- grado reconocido vigente: el último modificado
    SELECT x."IDSOLICITUD", x."CDGRADO", x."DSGRADO_NIVEL", x."CDTIPO_BAREMO",
           ROW_NUMBER() OVER (PARTITION BY x."IDSOLICITUD" ORDER BY x."FCMODI" DESC) AS "rn"
    FROM "SIDM_DICTAMEN" x
    WHERE x."FCBAJA" IS NULL
) d
       ON CAST(d."IDSOLICITUD" AS VARCHAR) = CAST(s."IDSOLICITUD" AS VARCHAR) AND d."rn" = 1
LEFT JOIN (                                                 -- última resolución de grado no anulada
    SELECT y."IDSOLICITUD", y."FCRESOLUCION", t."DSTIPODOCUMENTO",
           ROW_NUMBER() OVER (PARTITION BY y."IDSOLICITUD" ORDER BY y."FCRESOLUCION" DESC) AS "rn"
    FROM "SIDM_MR_RESOLUCIONES" y
    LEFT JOIN "SIDM_MR_TIPOS_DOCUMENTOS" t ON t."CDTIPODOCUMENTO" = y."CDTIPODOCUMENTO"
    WHERE y."FCBAJA" IS NULL
) r
       ON CAST(r."IDSOLICITUD" AS VARCHAR) = CAST(s."IDSOLICITUD" AS VARCHAR) AND r."rn" = 1
LEFT JOIN (                                                 -- origen: la entrada de la bandeja con su referencia
    SELECT CAST(b."NMREFERENCIA" AS VARCHAR) AS "NMREFERENCIA", b."DSORIGENDOC",
           ROW_NUMBER() OVER (PARTITION BY CAST(b."NMREFERENCIA" AS VARCHAR)
                              ORDER BY CASE WHEN b."CD_BANDEJA" = 'INI' THEN 0 ELSE 1 END,
                                       COALESCE(b."FC_RECEPCION", b."FCALTA")) AS "rn"
    FROM "SIDM_BANDEJA_RECEPCIONADOS" b
    WHERE b."DSORIGENDOC" IS NOT NULL
) o
       ON o."NMREFERENCIA" = CAST(s."NMREFERENCIA" AS VARCHAR) AND o."rn" = 1
