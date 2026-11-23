# Mapa de datos · cuadro de Natalidad (mockup v32) · 23/11/2026

Para cada pieza del mockup `mockups/MockupNatalidad_v32.html`: de dónde sale, si ya la tenemos y el PQL de partida. Los PQL son **borradores**: se prueban cuando exista el Knowledge Model de la perspectiva «Natalidad».

## 0. Qué hay en Celonis (visto el 23/11, solo lectura)

- Pool «OCPM DataPool VALIDACION y PRODUCCION» → Objects & Events: **3 objetos** (`NatExpedientes`, `NatEtapas`, `NatInteresados`) y **8 eventos** Nat… en borrador. 23 cambios sin versionar en el pool (no son solo nuestros).
- Perspectivas: Dependencia, PnCAtlantix, Discapacidad, DMPensionesNoContributiva. **No hay perspectiva «Natalidad»**.
- Data models: ninguno de Natalidad. `test:perspective_custom_PnCAtlantix` es de Pensiones No Contributivas (PnCExpedientes, PnCPropuesta, PnCRevision…): no sirve para Natalidad.
- Studio › Implementación › **«Familia Natalidad»**: paquete **vacío** (sin View ni KM), enlazado al data model `test:perspective_custom_DMPensionesNoContributiva`. Al crear la View habrá que enlazarlo al de Natalidad.
- Conclusión: **sin la perspectiva y su Test changes no hay datos que pintar**. La View no se puede empezar con datos hasta entonces.

## 1. Nombres que se suponen en los PQL (comprobar en el KM)

- Objeto: `"o_custom_NatExpedientes"`. Event log: `"el__EventosNatalidad"` (si la perspectiva le da otro nombre, cambiarlo en todos).
- Cada tipo de evento se reconoce por un atributo que solo tiene él:
  - presentación: `"Actividad" = 'Solicitud presentada por la interesada'`
  - alta: `"Actividad" = 'Alta del expediente'`
  - resolución: `"SentidoResolucion" IS NOT NULL` (valores: Favorable, Denegación, Desistimiento, Sin documento)
  - anulación: `"Actividad" = 'Expediente anulado'`
  - etapas: `"Fase" IS NOT NULL`; inicio `"Actividad" LIKE 'Inicio de la Etapa%'`
  - bitácora: `"Actividad" = 'Anulación de Etapa'`, `'Envío a Intervención'`, `'Documento requerido añadido'`…
  - notificaciones: `"TipoNotificacion" IS NOT NULL`, `"ConAcuse" = 'S'`
- Abreviaturas usadas abajo (en el PQL real van enteras):
  - `RES` = `PU_MIN("o_custom_NatExpedientes", "el__EventosNatalidad"."TIMESTAMP", "el__EventosNatalidad"."SentidoResolucion" IS NOT NULL)`
  - `PRES` = `"o_custom_NatExpedientes"."FechaPresentacionInteresado"`
  - `ALTA` = `"o_custom_NatExpedientes"."FechaInicio"`
- Variables de la View: `${plazo_dias}` (90 por defecto, plazo sin confirmar por la unidad).

## 2. Cabecera · Seguimiento del proceso

| Bloque | KPI | Fuente | Estado | PQL de partida |
|---|---|---|---|---|
| Fase previa | Entradas en registro, aportaciones, pendientes de alta, duplicadas | eReg | ⏳ Pendiente de datos | marcador `/* Pendiente de datos: eReg */` |
| Fase previa | Solicitudes recibidas | `NatSolicitudPresentada` (solo las que ya tienen expediente) | ⚠ parcial | `COUNT(CASE WHEN PRES IS NOT NULL THEN "o_custom_NatExpedientes"."ID" END)` |
| Tramitación | Expedientes dados de alta | `NatExpedientes.FechaInicio` | ✅ | `COUNT(CASE WHEN ALTA IS NOT NULL THEN "o_custom_NatExpedientes"."ID" END)` |
| Tramitación | Expedientes resueltos (% de los de alta) | `NatExpedienteResuelto` | ✅ | `COUNT(CASE WHEN RES IS NOT NULL THEN "o_custom_NatExpedientes"."ID" END)`; % = eso × 100.0 / dados de alta |
| Tramitación | Pendientes de resolver | alta sin resolución ni anulación | ✅ total | `COUNT(CASE WHEN ALTA IS NOT NULL AND RES IS NULL AND "o_custom_NatExpedientes"."FechaAnulacion" IS NULL THEN "o_custom_NatExpedientes"."ID" END)` |
| Tramitación | · en revisión o requerimiento / ya propuestos | fase actual (última etapa iniciada) | ✅ | por la fase de la última etapa: 2 = en revisión, 3–5 = propuestos |
| Tramitación | · revisados sin proponer | revisión de conformidad | ⏳ el campo aún no existe | marcador |
| Tramitación | Favorables / Denegados o desistidos (% de los resueltos) | `SentidoResolucion` | ✅ | `COUNT(DISTINCT CASE WHEN "el__EventosNatalidad"."SentidoResolucion" = 'Favorable' THEN "o_custom_NatExpedientes"."ID" END)` (ídem con `IN ('Denegación','Desistimiento')`) |
| Tiempos | Tiempo E2E | resolución − presentación | ✅ | `AVG(DAYS_BETWEEN(PRES, RES))` |
| Tiempos | Registro → alta | alta − presentación | ✅ | `AVG(DAYS_BETWEEN(PRES, ALTA))` |
| Tiempos | Alta → resolución | resolución − alta | ✅ | `AVG(DAYS_BETWEEN(ALTA, RES))` |
| Tiempos | Incumplimiento del plazo | % de resueltos con E2E > plazo | ✅ (plazo por confirmar) | `COUNT(CASE WHEN DAYS_BETWEEN(PRES, RES) > ${plazo_dias} THEN "o_custom_NatExpedientes"."ID" END) * 100.0 / COUNT(CASE WHEN RES IS NOT NULL THEN "o_custom_NatExpedientes"."ID" END)` |
| Reprocesos | Expedientes con reprocesos (% de resueltos) | vuelta a una fase anterior (orden de `Fase` en las etapas) + «Anulación de Etapa» de la bitácora | ✅ (PQL a probar) | ver sección 5 |
| Gestión económica | Altas en nómina, beneficiarias activas, pagos únicos, dejan de cobrar, importes | Soluciones y Nexus | ⏳ Pendiente de datos | marcadores |

Lógica del mockup: **tramitación** = embudo de las solicitudes presentadas en el periodo, con su situación a la fecha de corte; **tiempos** = sobre los resueltos en el periodo. Con un solo filtro de fechas de Celonis no salen las dos cosas a la vez: probar dos variables de fecha (`${desde}`, `${hasta}`) usadas dentro del PQL, o dos filtros con Interactions distintas.

## 3. Gráficos y tablas

| Componente | Fuente | Estado | Cómo |
|---|---|---|---|
| Tiempo medio y expedientes resueltos por fase | `NatEtapaIniciada` / `NatEtapaFinalizada` (`Fase`, fechas de etapa) | ✅ tiempos; ⚠ selector «Días de» parcial | dimensión `"el__EventosNatalidad"."Fase"`; días = `AVG(DAYS_BETWEEN("Fecha Inicio Etapa", "Fecha Fin Etapa"))` en eventos de inicio. «Días de» (unidad, solicitante, Intervención…): de momento por grupos de fase |
| Entradas, salidas y stock | alta, resolución | ✅ | por `ROUND_MONTH`: altas = `COUNT` por mes de `ALTA`; salidas = por mes de `RES`; stock = `RUNNING_SUM(altas − salidas)` |
| Stock pendiente por fase y antigüedad | abiertos por fase actual, tramos 0–30, 31–60, 61–90, > 90 | ✅ | fase de la última etapa iniciada (`PU_LAST`); tramo con `CASE WHEN DAYS_BETWEEN(ALTA, fecha de corte) <= 30 THEN '0–30' WHEN … END` |
| Composición | ver tabla de dimensiones | ⚠ parcial | dimensión elegible con un selector |
| Expedientes sin actividad | última `NatActividadRealizada.TIMESTAMP` | ✅ (sin «Atrasos» ni «Meses de atraso») | días sin actuación = `DAYS_BETWEEN(PU_MAX(bitácora), fecha de corte)`; filtro de etapa y umbral 30/60/90/180; **sin** `UsuarioAsignado`; botón de exportar |
| Gestión económica (crédito, atrasos, remesa, revisados sin proponer) | Nexus, Soluciones | ⏳ Pendiente de datos | textos «Pendiente de datos» con lo que falta |
| Comparativa de periodos | la cabecera en dos periodos | ✅ | mismos KPIs con dos rangos de fechas (variables) y diferencia en número y % |
| Explorador de procesos | event log | ✅ | componente Process Explorer sobre `"el__EventosNatalidad"` |

Fecha de corte: el último dato, `PU_MAX(CONSTANT(), "el__EventosNatalidad"."TIMESTAMP")`, mejor que `TODAY()`.

## 4. Dimensiones de «Composición»

| Dimensión | Fuente | Estado |
|---|---|---|
| Edad de la solicitante | `NatInteresados.TramoEdad` (principal) | ⚠ solo ~21 % informado: mucho «No informado» |
| Nacionalidad | `NatInteresados.NacionalidadAprox` (DNI / NIE) | ⚠ aproximación |
| Municipio de residencia | `NatInteresados.Municipio` | ✅ (comprobar cuántos informados: `sql/00i_comprobar_municipio.sql`) |
| Sentido de la resolución | `SentidoResolucion` | ✅ |
| Respuesta de la Intervención | etapas FAVORABLE CONCESIÓN / FAVORABLE CON OBS / ACTUACIÓN INTERESADA / DEV A INSTANCIA PROMO | ✅ |
| Tipo de solicitud, Canal, País, Hijos, Requisito incumplido | Soluciones / eReg | ⏳ Pendiente de datos |

En la composición, contar solo el interesado principal (`EsPrincipal`) para no duplicar expedientes.

## 5. Reprocesos (borrador)

Un expediente resuelto tiene reproceso si alguna etapa empieza en una fase **anterior** a una a la que ya había llegado, o si la bitácora tiene «Anulación de Etapa». Los requerimientos (misma fase) no cuentan.

- Número de fase: `CASE WHEN "Fase" LIKE '2.%' THEN 2 WHEN "Fase" LIKE '3.%' THEN 3 WHEN "Fase" LIKE '4.%' THEN 4 WHEN "Fase" LIKE '5.%' THEN 5 END`.
- Vuelta atrás: comparar con el máximo acumulado anterior (`RUNNING_MAX` por expediente, si el motor lo admite) o con `ACTIVITY_LAG` de la fase; si no, quedarse con «Anulación de Etapa» como primera versión.
- Expediente con reproceso: `PU_COUNT("o_custom_NatExpedientes", "el__EventosNatalidad"."ID", <condición de vuelta atrás>) > 0`.

## 6. Orden propuesto

1. Crear la perspectiva «Natalidad» (borrador): objeto principal `NatExpedientes`, objetos `NatEtapas` y `NatInteresados`, event log `EventosNatalidad` con los 8 eventos. **Necesita el «adelante» de Anthony.**
2. Test changes solo de esa perspectiva → **solo con el visto bueno de Roberto**.
3. Comprobar nombres reales en el KM (sección 1) y probar estos PQL en una View de borrador dentro de «Familia Natalidad».
4. Montar la View por bloques: cabecera → tiempos por fase → entradas/salidas/stock → stock por antigüedad → sin actividad → composición → comparativa → explorador. Lo que espera datos, con «Pendiente de datos».
