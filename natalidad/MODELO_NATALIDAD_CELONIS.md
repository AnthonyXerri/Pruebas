# Modelo de Natalidad en Celonis · ficha para reconstruirlo

Estado al 18/11/2026: **borrador guardado** (Save with Validation) en Objects & Events del pool «OCPM DataPool VALIDACION y PRODUCCION». Sin Create version ni Deploy (se hacen con Roberto).

Si el borrador se perdiera, todo se puede rehacer con esta ficha y las SQL de `natalidad/sql/`.

Reglas comunes:
- Etiqueta **Natalidad** (Custom Processes).
- Prefijo `Nat`.
- Data Source de **todas** las transformaciones: **OCPM DataPool IMPLEMENTACION _Conexión Producción PRATLX_RO**.
- Objetos y eventos «from scratch».
- Orden: crear, después relaciones y por último la transformación.

## Objetos

| Objeto | Atributos (además de ID String PK) | Relaciones | SQL |
|---|---|---|---|
| `NatExpedientes` | **String:** Aplicacion, CodigoProcedimiento, CodigoConvocatoria, EjercicioConvocatoria, CodigoExpediente, IdEstado, DescripcionEstado, UsuarioAsignado, IdUnidad, DescripcionUnidad, ReferenciaSolicitud, CodigoSolicitud, Convocatoria<br>**Datetime:** FechaInicio, FechaResolucion, FechaFinTramitacion, FechaAnulacion, FechaPresentacionInteresado, FechaEntradaSistemaRegistro, FechaEntradaRegistroConsejeria, FechaCierre | — (es el padre) | `01_objeto_NatExpedientes.sql` |
| `NatEtapas` | **String:** IDEtapa, DescripcionEtapa, Confiscalizacion, Fase | NatExpedientes **1 — N** NatEtapas (FK `NatExpedientes`) | `02_objeto_NatEtapas.sql` |
| `NatInteresados` | **String:** TipoInteresado, EsPrincipal, EsSolicitante, TipoDocumento, NacionalidadAprox, TramoEdad, MedioNotificacion, CdProvincia, Provincia, CdMunicipio, Municipio | NatExpedientes **1 — N** NatInteresados (FK `NatExpedientes`) | `11_objeto_NatInteresados.sql` |

## Eventos (todos con ID String PK y Time Datetime)

| Evento | Otros atributos | Relaciones (involves one) | SQL |
|---|---|---|---|
| `NatSolicitudPresentada` | Actividad (String) | NatExpedientes | `05_evento_NatSolicitudPresentada.sql` |
| `NatExpedienteAbierto` | Actividad (String) | NatExpedientes | `06_evento_NatExpedienteAbierto.sql` |
| `NatEtapaIniciada` | Actividad, Etapas, Fase (String); **Fecha Inicio Etapa, Fecha Fin Etapa (Datetime)** | NatEtapas, NatExpedientes | `03_evento_NatEtapaIniciada.sql` |
| `NatEtapaFinalizada` | Igual que NatEtapaIniciada | NatEtapas, NatExpedientes | `04_evento_NatEtapaFinalizada.sql` |
| `NatExpedienteResuelto` | Actividad, OrigenFecha, SentidoResolucion, CodigoPlantilla, DescripcionPlantilla, EstadoDocumento (String); **FechaResolucionExpediente, FechaGeneracionResolucion, FechaFirmaRechazoResolucion (Datetime)** | NatExpedientes | `07_evento_NatExpedienteResuelto.sql` |
| `NatExpedienteAnulado` | Actividad (String) | NatExpedientes | `08_evento_NatExpedienteAnulado.sql` |
| `NatActividadRealizada` | Actividad, DescripcionActividad, IdEtapa, EsAutomatica, OrdenActividad (String); **OrdenActividadNum (Long integer)** | NatExpedientes, NatEtapas | `09_evento_NatActividadRealizada.sql` |
| `NatNotificaciones` | Actividad, TipoNotificacion, ConAcuse, Titulo (String); **Fecha Notificacion, Fecha Acuse (Datetime)** | NatExpedientes | `10_evento_NatNotificaciones.sql` |

Ojo: los nombres con espacios (`Fecha Inicio Etapa`, `Fecha Notificacion`…) tienen que escribirse igual.

## Pendiente (con Roberto)

1. ✅ (23/11, borrador) Perspectiva «Natalidad»: objetos NatExpedientes, NatEtapas y NatInteresados; event log `EventosNatalidad` (Default, objeto principal NatExpedientes, 8 eventos, sin dividir la actividad por atributos).
2. Test changes, solo con esa perspectiva.
3. Create version y Deploy.
4. Knowledge Model y View.
