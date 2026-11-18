# Plan Celonis · Natalidad (desde el 18/11/2026)

Objetivo: sacar de Atlantix (pool PRATLX_RO) todo lo posible del mockup v31 mientras llegan eReg, Nexus y las tablas propias de Natalidad. Un paso cada vez; sin Create version ni Deploy sin Roberto.

Filtro en todo: `CDAPLICACION = 'D032'` y `CDPROCEDIMIENTO = '3163'`.
Data Source en todas las transformaciones: **OCPM DataPool IMPLEMENTACION _Conexión Producción PRATLX_RO**.
Prefijo `Nat` y etiqueta **Natalidad**. Memoria detallada: `natalidad/MEMORIA_NATALIDAD_CELONIS.md`. SQL: `natalidad/sql/`.

## Bloques de trabajo

| Bloque | Qué | Tabla origen | Para el mockup | Estado |
|---|---|---|---|---|
| A | `NatExpedientes`, `NatEtapas`, `NatEtapaIniciada`, `NatEtapaFinalizada` | `GSTA_V_CEL_EXPEDIENTE`, `GSTA_V_CEL_ETAPA` | Cabecera de tramitación, tiempos por fase, stock por fase, explorador | ✅ |
| B | Eventos de entrada y cierre: `NatSolicitudPresentada`, `NatExpedienteAbierto`, `NatExpedienteResuelto` (sentido y firma), `NatExpedienteAnulado` | `GSTA_V_CEL_EXPEDIENTE`, `GSTA_V_CEL_DOC_ELABORADA` | Fase 1 (registro → alta), tiempo E2E, registro → alta, alta → resolución, entradas/salidas, sentido de la resolución | ✅ |
| C | Bitácora: `NatActividadRealizada` ✅ (anulaciones de etapa, hitos, envío a la Intervención, cambios de unidad, documentos requeridos, notificaciones y acuses, ICDA, cambio de convocatoria; la última actuación sale de su `Time`). Pendiente: revisar los otros eventos de PnC (hitos, notificaciones, documentos, actividad inicio/resolución, automáticos, fase) por si aportan algo que no esté | `GSTA_V_CEL_ACTIVIDAD` | Reprocesos, requerimientos, Intervención, expedientes sin actividad, explorador | ▶ siguiente |
| D | `NatNotificaciones` ✅ (todas, con fecha de acuse y tipo). Documentos aportados y elaborados, e hitos: ya cubiertos en la bitácora y en `NatExpedienteResuelto`; revisar los eventos de PnC solo si falta algo | `GSTA_V_CEL_NOTIFICACION`, `GSTA_V_CEL_DOC_*`, `GSTA_V_CEL_HITO` | Notificación y acuse del requerimiento, aportaciones, plazo vencido | ✅ lo principal |
| E ▶ siguiente | `NatInteresados` (edad en tramos, nacionalidad, país, municipio; sin nombres ni DNI) | `GSTA_V_INTERESADOS` | Composición | Pendiente |
| F | Completar `NatExpedientes`: `REF_SOLICITUD`, año y nombre de la convocatoria (`GSTA_V_EXPEDIENTE`), nombre del procedimiento | `GSTA_V_CEL_EXPEDIENTE`, `GSTA_V_EXPEDIENTE`, `GSTA_V_CEL_CAT_PROC` | Filtros, enlace futuro con eReg | Pendiente |
| G | Búsquedas: revisión de conformidad, fichero o tercero de Nexus, plazo de requerimiento (`LIKE` en la bitácora y en los hitos) | Bitácora, hitos | «Revisados sin proponer», subestados de terceros | Pendiente |
| H | Test changes, perspectiva («Natalidad»), Knowledge Model (KPIs en PQL) y View | — | El cuadro | Con Roberto |

Para cada evento de PnC que se copie: ver su SQL, atributos y relaciones; crear el evento Nat (tipos bien puestos); relaciones; transformación con PRATLX_RO; Preview; Save with Validation.

## Qué saldrá del mockup solo con Atlantix

- **Sí:**
  - Cabecera de la fase de tramitación: altas, pendientes, resueltos, denegados o desistidos, favorables.
  - Tiempos: E2E, registro → alta, alta → resolución, incumplimiento con el plazo como parámetro.
  - Reprocesos.
  - Tiempo y stock por fase.
  - Entradas, salidas y stock: «recibidas» = solo las que ya tienen expediente.
  - Expedientes sin actividad.
  - Sentido de la resolución y respuesta de la Intervención.
  - Comparativa.
  - Explorador de procesos.
- **Parcial:**
  - «En revisión / revisados sin proponer / ya propuestos»: falta localizar la revisión de conformidad (bloque G).
  - Composición: edad, nacionalidad, país y municipio, si `GSTA_V_INTERESADOS` los trae.
  - «Depende de»: falta el reparto de la unidad.
- **No (esperan datos):**
  - eReg: entradas, aportaciones, canal, pendientes de alta, duplicadas.
  - Tablas propias de Natalidad: tipo de solicitud, hijos, mes de nómina, importes, motivo de denegación.
  - Nexus: terceros, pagos, nómina, A/D/OK, crédito y atrasos.

## Decisiones

- **18/11: un solo evento de solicitud.** De 53.375 expedientes, solo 140 tienen la fecha de eReg distinta de la de presentación y 157 la de Consejería; a 408 les falta la de eReg. **No se crean** `NatSolicitudRegistrada` ni `NatSolicitudRecibidaConsejeria`: basta `NatSolicitudPresentada` (`FC_SOL_INTERESADO`).

## Dimensiones de «Composición» del mockup (18/11)

| Dimensión | De dónde sale | Estado |
|---|---|---|
| Tipo de solicitud (nacimiento, gestación, adopción, otros) | Tabla propia de Natalidad en Atlantix | ❌ Pedir |
| Canal de entrada (sede, oficina, ORVE) | eReg | ❌ Pedir |
| Edad de la solicitante | `NatInteresados.TramoEdad` | ✅ |
| Nacionalidad | `NatInteresados.NacionalidadAprox` (por tipo de documento: DNI / NIE) | ⚠ Aproximación; pedir el dato real |
| País de nacimiento | — | ❌ Pedir |
| Municipio de residencia | `NatInteresados.Municipio` | ✅ |
| Hijos por solicitud | Tabla propia de Natalidad | ❌ Pedir |
| Sentido de la resolución | `NatExpedienteResuelto.SentidoResolucion` | ✅ |
| Requisito incumplido | Tabla propia (motivo de denegación) | ❌ Pedir |
| Respuesta de la Intervención | Etapas (FAVORABLE / CON OBS / ACTUACIÓN INTERESADA / DEV. A INSTANCIA) e hito CONCESIÓN APROBADA | ✅ |
