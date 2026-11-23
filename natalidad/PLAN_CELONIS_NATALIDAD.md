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
| E ✅ | `NatInteresados` (edad en tramos, nacionalidad, país, municipio; sin nombres ni DNI) | `GSTA_V_INTERESADOS` | Composición | Pendiente |
| F ✅ | Completar `NatExpedientes`: `REF_SOLICITUD`, año y nombre de la convocatoria (`GSTA_V_EXPEDIENTE`), nombre del procedimiento | `GSTA_V_CEL_EXPEDIENTE`, `GSTA_V_EXPEDIENTE`, `GSTA_V_CEL_CAT_PROC` | Filtros, enlace futuro con eReg | Pendiente |
| G ✅ (no están: se piden) | Búsquedas: revisión de conformidad, fichero o tercero de Nexus, plazo de requerimiento (`LIKE` en la bitácora y en los hitos) | Bitácora, hitos | «Revisados sin proponer», subestados de terceros | Pendiente |
| H ▶ siguiente | Test changes, perspectiva («Natalidad»), Knowledge Model (KPIs en PQL) y View | — | El cuadro | Con Roberto |

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
| Edad de la solicitante | `NatInteresados.TramoEdad` | ⚠ Solo el 21 % tiene fecha de nacimiento (2022-23 menos del 10 %): pedir |
| Nacionalidad | `NatInteresados.NacionalidadAprox` (por tipo de documento: DNI / NIE) | ⚠ Aproximación; pedir el dato real |
| País de nacimiento | — | ❌ Pedir |
| Municipio de residencia | `NatInteresados.Municipio` | ✅ |
| Hijos por solicitud | Tabla propia de Natalidad | ❌ Pedir |
| Sentido de la resolución | `NatExpedienteResuelto.SentidoResolucion` | ✅ |
| Requisito incumplido | Tabla propia (motivo de denegación) | ❌ Pedir |
| Respuesta de la Intervención | Etapas (FAVORABLE / CON OBS / ACTUACIÓN INTERESADA / DEV. A INSTANCIA) e hito CONCESIÓN APROBADA | ✅ |

## Petición de datos (18/11)

- **Para enviar a la Comunidad:** `mockups/Datos_que_faltan_Natalidad.xlsx`, una sola tabla sencilla con solo lo que falta: 21 datos por sistema (Nº | Qué necesitamos | Para qué lo usamos | Prioridad | ¿Dónde está?, esta última en amarillo para que la rellenen). Se genera con `natalidad/gen_tabla_peticion.py`.
- **Detalle interno:** `mockups/Datos_que_faltan_Natalidad_detalle.xlsx`, tres hojas, generadas con `natalidad/gen_datos_que_faltan.py`.
  - **Qué pedir:** 30 datos (eReg 5, Atlantix propias 13, Nexus 7, unidad 5), con estado, prioridad y columnas amarillas para que rellenen tabla, columna e histórico.
  - **Dudas a confirmar:** 10.
  - **Ya disponible:** lo que sale de Atlantix y en qué objeto o evento de Celonis está.
- **Respuesta de la unidad (20/11):**
  - La unidad (Soluciones y la gestora) no conoce tablas ni columnas. Las etapas, sus fechas y el registro los tiene que informar el equipo de ATLX, así que se quitan de su tabla.
  - Para los campos propios de Natalidad (3163) hay que indicar el punto exacto de la pantalla o pestaña donde aparece cada uno.
  - Propuesta: una sesión de unos 30 minutos con la gestora viendo la pestaña de Natalidad (o capturas con los datos tapados). Después se envía al equipo de ATLX una tabla con dato, pestaña y etiqueta en pantalla.
  - eReg, bandeja de registros y Nexus se piden a los equipos técnicos a través de Madrid Digital. Preguntar a Roberto cómo se pidieron las tablas PNCA_ de PnC.
- **Respuestas del 23/11:**
  - **Soluciones** indicará el punto de la pantalla de los campos propios de 3163.
  - **Revisión de conformidad:** no existe todavía; es un campo nuevo sin petición FARO. El indicador «revisados sin proponer» del mockup queda pendiente. Si se crea, pedir que se registre en la bitácora, para tener la fecha.
  - **Primera nómina:** se paga en el mes de la propuesta favorable, así que sale de la etapa PROPUESTA FAVORABLE y no se pide.
  - **Propuesta a nómina:** el mes es el de la propuesta favorable; solo se pide el importe propuesto (lo calcula la aplicación al grabar la propuesta).
  - **Revisado contra `Datos_necesarios_cuadro_Natalidad_v9.xlsx`:** faltaba en la lista un dato propio de Atlantix: los datos económicos del expediente, es decir, el importe propuesto y el pagado cada mes (la unidad dijo que Atlantix los tiene). La documentación requerida **no** se pide: ya está en la bitácora («Añadido / Eliminado documento requerido») y en `GSTA_V_CEL_CAT_DOCREQ`. La fecha de nacimiento de la solicitante tampoco: está en `GSTA_V_INTERESADOS`, solo en una parte de los expedientes, como dice la unidad. Se piden a Soluciones con tabla y columna; el acceso desde Celonis se pide después.
  - **Bajas y modificaciones:** no se piden. Las etapas de baja y de modificación ya salen de Atlantix y los pagos saldrán de Nexus.
  - **Datos de la solicitante** (nacionalidad, país, fecha de nacimiento): no todos los expedientes los tienen; se muestran solo donde existan.
  - **Calendario de nómina:** no hay día fijo. El envío a la Intervención es la fecha de propuesta (Atlantix) y la parte contable está en Nexus por documento contable. No se pide calendario.
  - **Fichero de terceros:** se hace fuera del sistema. Referencias: fecha de generación del CSV que Familia envía a Gestión Económica y fecha de carga del CSV de vuelta. Pedir esas dos fechas por mes.
  - **Plazos** de tramitación y de aportación: sin respuesta todavía.
  - **Conversación con Soluciones (24/11):**
    - **Revisión de conformidad:** se crearán dos campos (marca y fecha) cuando llegue la petición oficial FARO; depende del proveedor. Solo existirán mientras el expediente no tenga propuesta favorable. **Riesgo:** si se borran al proponer, se pierde el histórico. Hay que pedir que la fecha se conserve o quede en la bitácora.
    - **Primer pago:** es el mes de la fecha de la propuesta favorable (confirmado).
    - **Último mes pagado:** lo pueden dar, aunque dicen que es «relativo».
    - **Nacionalidad:** solo existe la de origen, del formulario, añadida hace pocos meses, no obligatoria y con pocos datos. Será una sola dimensión «Nacionalidad» con lo que haya; el país de nacimiento, solo si existe. Alternativa si sale casi vacía: aproximar por tipo de documento (DNI / NIE).
    - **Municipio de residencia:** ya lo tenemos (`GSTA_V_INTERESADOS`).
    - Lo que se pide es tabla y columna, nunca datos por correo.
  - **Respuesta a Pablo:**
    - Del fichero de terceros se piden solo las fechas por mes, nunca el contenido del CSV (lleva datos personales y bancarios).
    - Se le pregunta si la carga del CSV de vuelta es lo que cierra la etapa VALIDACIÓN TERCERO. Si lo es, solo falta la fecha de generación.
    - El ciclo mensual sale de los datos: propuesta favorable, «Envío a Intervención» de la bitácora, respuestas por lotes y resolución mensual.
