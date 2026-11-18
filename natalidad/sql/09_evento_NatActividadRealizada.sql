-- Evento NatActividadRealizada · cada anotación de la bitácora de Atlantix (GSTA_V_CEL_ACTIVIDAD) de los expedientes de Natalidad
-- Adaptado de PNCActividadRealizada (18/11/2026). Cambios:
--   * Filtro D032 + 3163; relaciones NatExpedientes y NatEtapas.
--   * Sin los CTE de usuarios (Tramitadores/Gestores salen de tablas PNCA_, propias de PnC) ni columnas de usuario:
--     el mockup no mide por persona y los logins son datos sensibles.
--   * Se excluyen, además de «Finalización de la Etapa» (ya está en NatEtapaFinalizada) y los errores labelsMessage,
--     «Apertura de expediente» (= NatExpedienteAbierto) y «Anulado expediente» (= NatExpedienteAnulado), para no duplicar.
--   * Clasificación de PnC + clases propias para Natalidad: Anulación de Etapa (reprocesos/requerimientos),
--     Cambio de unidad a/desde la Intervención Delegada.
-- Relaciones (crear antes): involves one NatExpedientes ("NatExpedientes"), involves one NatEtapas ("NatEtapas").
-- Data Source: PRATLX_RO.
-- OJO: DescripcionActividad es el texto completo y puede llevar DNI o nombres: no mostrarlo en las vistas.
WITH Expedientes AS (
    SELECT DISTINCT CDEXPEDIENTE
    FROM "GSTA_V_CEL_EXPEDIENTE"
    WHERE CDAPLICACION = 'D032'
      AND CDPROCEDIMIENTO = '3163'
)
SELECT DISTINCT
    'ActividadRealizada_' || A."CDEXPEDIENTE" || '_' || CAST(A."ORDEN" AS VARCHAR)   AS "ID",
    'Etapa_' || CAST(A."IDETAPA" AS VARCHAR) || '_' || A."CDEXPEDIENTE"              AS "NatEtapas",
    A."CDEXPEDIENTE"                                                                 AS "NatExpedientes",
    CAST(A."FCACTIVIDAD" AS TIMESTAMP)                                               AS "Time",
    CASE
        WHEN A."DSACTIVIDAD" LIKE 'Anulación de la Etapa%'
          OR A."DSACTIVIDAD" LIKE 'Anulaci%n de la Etapa%'                         THEN 'Anulación de Etapa'
        WHEN A."DSACTIVIDAD" LIKE 'Anulado el hito%'                               THEN 'Anulación de Hito'
        WHEN A."DSACTIVIDAD" LIKE 'Informado el hito%'                             THEN A."DSACTIVIDAD"
        WHEN A."DSACTIVIDAD" LIKE 'Envio a Intervencion%'
          OR A."DSACTIVIDAD" LIKE 'Env%o a Intervenci%n%'                          THEN 'Envío a Intervención'
        WHEN A."DSACTIVIDAD" LIKE 'Cambio de unidad%Intervenci%n%'                 THEN 'Cambio de unidad: Intervención Delegada'
        WHEN A."DSACTIVIDAD" LIKE 'Cambio de unidad%'                              THEN 'Cambio de unidad: Sección de Natalidad'
        WHEN A."DSACTIVIDAD" LIKE 'Se ha cambiado el expediente a la convocatoria%' THEN 'Cambio de Convocatoria'
        WHEN A."DSACTIVIDAD" LIKE 'Añadido documento requerido%'                   THEN 'Documento requerido añadido'
        WHEN A."DSACTIVIDAD" LIKE 'Eliminado documento requerido%'                 THEN 'Documento requerido eliminado'
        WHEN A."DSACTIVIDAD" LIKE 'Eliminado documento%'
          OR A."DSACTIVIDAD" LIKE 'Aportaci%n o elaboraci%n de [Dd]ocumentaci%n%'
          OR A."DSACTIVIDAD" LIKE 'Documento aportado%'                            THEN 'Gestión de Documentos Requeridos'
        WHEN A."DSACTIVIDAD" LIKE 'Incorporado documento elaborado%'
          OR A."DSACTIVIDAD" LIKE 'Adjuntado fichero%'                             THEN 'Incorporación de Documento'
        WHEN A."DSACTIVIDAD" LIKE 'Solicitada información al servicio ICDA%'
          OR A."DSACTIVIDAD" LIKE 'No se ha recibido respuesta del servicio ICDA%' THEN 'Consulta Servicio ICDA'
        WHEN A."DSACTIVIDAD" LIKE 'Recibida%informaci%n%servicio ICDA%'
          OR A."DSACTIVIDAD" LIKE ' Recibida%informaci%n%servicio ICDA%'           THEN 'Respuesta ICDA'
        WHEN A."DSACTIVIDAD" LIKE 'Modific%'                                       THEN 'Modificación de Metadatos'
        WHEN A."DSACTIVIDAD" LIKE 'Generado nuevo documento%'
          OR A."DSACTIVIDAD" LIKE 'Se ha generado el documento%'                   THEN 'Generación de Documento'
        WHEN A."DSACTIVIDAD" LIKE 'Enviado a firma%'                               THEN 'Envío a Firma'
        WHEN A."DSACTIVIDAD" LIKE 'Firmado documento%'                             THEN 'Firma de Documento'
        WHEN A."DSACTIVIDAD" LIKE 'Recibido firmado documento%'                    THEN 'Recepción Documento Firmado'
        WHEN A."DSACTIVIDAD" LIKE 'Recibido rechazo%firma%'
          OR A."DSACTIVIDAD" LIKE 'Rechazada firma documento%'                     THEN 'Rechazo de Firma'
        WHEN A."DSACTIVIDAD" LIKE 'Retirado de la firma%'                          THEN 'Retirado de Firma'
        WHEN A."DSACTIVIDAD" LIKE 'Firma offline documento%'                       THEN 'Firma Offline'
        WHEN A."DSACTIVIDAD" LIKE 'Elaborar resolución%'
          OR A."DSACTIVIDAD" LIKE 'Emitir resolución%'                             THEN 'Firma de Resolución'
        WHEN A."DSACTIVIDAD" LIKE 'Alta de notificación%'
          OR A."DSACTIVIDAD" LIKE 'Envío de notificación%'
          OR A."DSACTIVIDAD" LIKE 'Enviada notificación%'
          OR A."DSACTIVIDAD" LIKE 'Notificar resolución positiva / Seleccionar%'
          OR A."DSACTIVIDAD" LIKE 'Creaci%n de notificaci%n%'
          OR A."DSACTIVIDAD" LIKE 'Guardada notificación%'
          OR A."DSACTIVIDAD" LIKE 'Notificaci%n /%'                                THEN 'Notificación'
        WHEN A."DSACTIVIDAD" LIKE 'Acuse de recibo%'
          OR A."DSACTIVIDAD" LIKE 'Acuse recibido%'
          OR A."DSACTIVIDAD" LIKE 'Notificar resolución positiva / Aportar acuses%'
          OR A."DSACTIVIDAD" LIKE 'Recepción de acuse de recibo%'                  THEN 'Acuse de Recibo'
        WHEN A."DSACTIVIDAD" LIKE 'Impresi%n de notificaciones%'                   THEN 'Impresión de Notificaciones'
        WHEN A."DSACTIVIDAD" LIKE 'Eliminada notificaci%'                          THEN 'Eliminación de Notificación'
        WHEN A."DSACTIVIDAD" LIKE 'Interesados asociados%'
          OR A."DSACTIVIDAD" LIKE 'Interesados desasociados%'                      THEN 'Asociación de Interesados'
        WHEN A."DSACTIVIDAD" LIKE 'Representantes asociados%'
          OR A."DSACTIVIDAD" LIKE 'Representantes desasociados%'                   THEN 'Gestión de Representantes'
        WHEN A."DSACTIVIDAD" LIKE 'Informado el estado%'                           THEN 'Informado Estado Externo'
        WHEN A."DSACTIVIDAD" LIKE 'Dado de baja el expediente%'                    THEN 'Baja en Sistema Externo'
        WHEN A."DSACTIVIDAD" LIKE 'Expediente asignado%'
          OR A."DSACTIVIDAD" LIKE 'Expediente desasignado%'                        THEN 'Asignación de Gestor'
        WHEN A."DSACTIVIDAD" LIKE 'Enviado a unidad%'                              THEN 'Envío a Unidad'
        WHEN A."DSACTIVIDAD" LIKE 'Reabierta tramitaci%n%'
          OR A."DSACTIVIDAD" LIKE 'Reapertura de expediente%'
          OR A."DSACTIVIDAD" LIKE 'Reactivado el expediente%'                      THEN 'Reapertura de Tramitación'
        WHEN A."DSACTIVIDAD" LIKE 'Restaurado expediente%'                         THEN 'Restauración de Expediente'
        WHEN A."DSACTIVIDAD" LIKE 'Cierre%'                                        THEN 'Cierre de Expediente'
        WHEN A."DSACTIVIDAD" LIKE 'Finalizacion de la Fase%'                       THEN 'Finalización de Fase'
        WHEN A."DSACTIVIDAD" LIKE 'Revisión jurídica%'
          OR A."DSACTIVIDAD" LIKE 'Revisión administrativa%'
          OR A."DSACTIVIDAD" LIKE 'Revisión técnica%'
          OR A."DSACTIVIDAD" LIKE 'Revisar documentaci%n%'                         THEN 'Revisión de Documentación'
        WHEN A."DSACTIVIDAD" LIKE 'Subsanaci%'                                     THEN 'Subsanación'
        WHEN A."DSACTIVIDAD" LIKE 'Recepci%n%documentaci%n%'                       THEN 'Recepción de Documentación'
        WHEN A."DSACTIVIDAD" LIKE 'Anexado documento%'                             THEN 'Anexado de Documento'
        WHEN A."DSACTIVIDAD" LIKE 'Cambio de documento de identificaci%'           THEN 'Cambio de Identificación'
        WHEN A."DSACTIVIDAD" LIKE 'Cancelaci%n del expediente%'                    THEN 'Cancelación de Expediente'
        WHEN A."DSACTIVIDAD" LIKE 'Se crea instancia BPM%'                         THEN 'Creación Instancia BPM'
        WHEN A."DSACTIVIDAD" LIKE 'Enviado el documento%'                          THEN 'Envío de Documento'
        ELSE 'Sin clasificar'
    END                                                                              AS "Actividad",
    A."DSACTIVIDAD"                                                                  AS "DescripcionActividad",
    CAST(A."IDETAPA" AS VARCHAR)                                                     AS "IdEtapa",
    A."ITAUTOMATICA"                                                                 AS "EsAutomatica",
    CAST(A."ORDEN" AS VARCHAR)                                                       AS "OrdenActividad",
    CAST(A."ORDEN" AS INTEGER)                                                       AS "OrdenActividadNum"
FROM "GSTA_V_CEL_ACTIVIDAD" AS A
INNER JOIN Expedientes AS B
    ON A."CDEXPEDIENTE" = B.CDEXPEDIENTE
WHERE A."CDEXPEDIENTE" IS NOT NULL
  AND A."FCACTIVIDAD" IS NOT NULL
  AND A."DSACTIVIDAD" NOT LIKE 'Finalización de la Etapa%'
  AND A."DSACTIVIDAD" NOT LIKE 'Apertura de%xpediente%'
  AND A."DSACTIVIDAD" NOT LIKE 'Anulado expediente%'
  AND A."DSACTIVIDAD" NOT LIKE 'labelsMessage%'
  AND A."DSACTIVIDAD" <> 'Etiqueta desconocida'
