# Mapa de datos · cuadro de Natalidad (mockup v32) · 23/11/2026

Para cada pieza del mockup `mockups/MockupNatalidad_v32.html`: de dónde sale, si ya la tenemos y el PQL de partida. Los PQL son **borradores**: se prueban cuando exista el Knowledge Model de la perspectiva «Natalidad».

## 0. Qué hay en Celonis (visto el 23/11, solo lectura)

- Pool «OCPM DataPool VALIDACION y PRODUCCION» → Objects & Events: **3 objetos** (`NatExpedientes`, `NatEtapas`, `NatInteresados`) y **8 eventos** Nat… en borrador. 23 cambios sin versionar en el pool (no son solo nuestros).
- Perspectivas: Dependencia, PnCAtlantix, Discapacidad, DMPensionesNoContributiva. **23/11: creada la perspectiva «Natalidad»** (borrador, ver sección 6).
- Data models: ninguno de Natalidad. `test:perspective_custom_PnCAtlantix` es de Pensiones No Contributivas (PnCExpedientes, PnCPropuesta, PnCRevision…): no sirve para Natalidad.
- Studio › Implementación › **«Familia Natalidad»**: paquete **vacío** (sin View ni KM), enlazado al data model `test:perspective_custom_DMPensionesNoContributiva`. Al crear la View habrá que enlazarlo al de Natalidad.
- Conclusión: **sin la perspectiva y su Test changes no hay datos que pintar**. La View no se puede empezar con datos hasta entonces.
- **23/11 (tarde):** Test changes de la perspectiva «Natalidad» hecho con el visto bueno de Roberto. Data model `test:perspective_custom_Natalidad` cargado. En «Familia Natalidad» hay ya una variable de paquete para ese data model, el KM **«Natalidad KM»** y la View **«Natalidad View»**, todo en borrador. Lo montado está en la **sección 7**.

## 1. Nombres que se suponen en los PQL (comprobar en el KM)

- Objeto: `"o_custom_NatExpedientes"`. Event log: `"el__EventosNatalidad"` (si la perspectiva le da otro nombre, cambiarlo en todos).
- Cada tipo de evento se reconoce por un atributo que solo tiene él:
  - presentación: `"Actividad" = 'Solicitud presentada por la interesada'`
  - alta: `"Actividad" = 'Alta del expediente'`
  - resolución: `"SentidoResolucion" IS NOT NULL` (valores: Favorable, Denegación, Desistimiento, Sin documento)
  - anulación: `"Actividad" = 'Expediente anulado'`
  - etapas: `"Fase" IS NOT NULL`; inicio `"Actividad" LIKE 'Inicio de la Etapa%'` ⚠ **23/11: no coincide** con el `Actividad` real de los eventos de etapa. Usar `"Fase" IS NOT NULL` (ver sección 7).
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
| Composición | ver tabla de dimensiones | ✅ 5 de 10 dimensiones (23/11); el resto, «Pendiente de datos» | dimensión elegible con un selector (variable `comp_dim`); PQL en la sección 7 |
| Expedientes sin actividad | último evento del expediente (cualquier tipo) | ✅ 23/11 (sin «Atrasos» ni «Meses de atraso»: Nexus; exportar, sin decidir) | días sin actuación = `DAYS_BETWEEN(PU_MAX(expediente, TIMESTAMP), fecha de corte)`; selectores de etapa (una o varias, lista sacada de los datos), días (30/60/90/180) y «Depende de», con variables del KM; **sin** `UsuarioAsignado`. PQL en la sección 7 |
| Gestión económica (crédito, atrasos, remesa, revisados sin proponer) | Nexus, Soluciones | ⏳ Pendiente de datos | textos «Pendiente de datos» con lo que falta |
| Comparativa de periodos | la cabecera en dos periodos | ✅ | mismos KPIs con dos rangos de fechas (variables) y diferencia en número y % |
| Explorador de procesos | event log | ✅ | componente Process Explorer sobre `"el__EventosNatalidad"` |

Fecha de corte: el último dato, `PU_MAX(CONSTANT(), "el__EventosNatalidad"."TIMESTAMP")`, mejor que `TODAY()`.

## 4. Dimensiones de «Composición»

| Dimensión | Fuente | Estado |
|---|---|---|
| Edad de la solicitante | `NatInteresados.TramoEdad` de la solicitante | ✅ montada; ⚠ la mayoría «No informado». Tramos del dato: `1. Menos de 20`, `2. 20-24`, `3. 25-29`, `4. 30-34`, `5. 35-39`, `6. 40 o más`, `No informado` (el mockup usa otros cortes) |
| Nacionalidad | `NatInteresados.NacionalidadAprox` de la solicitante: `Española (DNI)`, `Extranjera (NIE o pasaporte)`, `No informado` | ✅ montada; ⚠ aproximación por tipo de documento |
| Municipio de residencia | `NatInteresados.Municipio` de la solicitante | ✅ montada; sin municipio → «No informado» |
| Sentido de la resolución | `SentidoResolucion` (`SENT`): Favorable, Denegación, Desistimiento, Sin documento | ✅ montada |
| Respuesta de la Intervención | columna **`Etapas`** del event log (eventos `NatEtapaFinalizada`): `FAVORABLE CONCESIÓN`, `FAVORABLE CON OBS CONCESIÓN`, `ACTUACIÓN INTERESADA CONCESIÓN`, `DEV A INSTANCIA PROMO CONCESIÓN` | ✅ montada (última respuesta de cada expediente) |
| Tipo de solicitud, Canal, País, Hijos, Requisito incumplido | Soluciones / eReg | ⏳ Pendiente de datos |

En la composición se cuenta **la solicitante**: `EsSolicitante = 'S'`. Hay exactamente una por expediente. No sirve `EsPrincipal`: también lo llevan algunos representantes, y unos pocos expedientes no tienen ninguna solicitante.

## 5. Reprocesos (borrador)

Un expediente resuelto tiene reproceso si alguna etapa empieza en una fase **anterior** a una a la que ya había llegado, o si la bitácora tiene «Anulación de Etapa». Los requerimientos (misma fase) no cuentan.

- Número de fase: `CASE WHEN "Fase" LIKE '2.%' THEN 2 WHEN "Fase" LIKE '3.%' THEN 3 WHEN "Fase" LIKE '4.%' THEN 4 WHEN "Fase" LIKE '5.%' THEN 5 END`.
- Vuelta atrás: comparar con el máximo acumulado anterior (`RUNNING_MAX` por expediente, si el motor lo admite) o con `ACTIVITY_LAG` de la fase; si no, quedarse con «Anulación de Etapa» como primera versión.
- Expediente con reproceso: `PU_COUNT("o_custom_NatExpedientes", "el__EventosNatalidad"."ID", <condición de vuelta atrás>) > 0`.

## 6. Orden propuesto

1. ✅ 23/11: perspectiva «Natalidad» guardada (borrador): objetos `NatExpedientes`, `NatEtapas` y `NatInteresados` (dos relaciones 1–N incluidas); event log **`EventosNatalidad`** (Default), objeto principal `NatExpedientes`, los 8 eventos marcados **sin** dividir la actividad por atributos. Data model «Not executed», sin paquetes enlazados. El primer Save dio «Perspective not saved» (error genérico); el segundo funcionó y no quedó duplicada. Celonis avisa de que crear event logs en la perspectiva se va a retirar (pasará al Knowledge Model) y que crea solo un event log por objeto con sus eventos directos.
2. ✅ 23/11: Test changes solo de esa perspectiva, con el visto bueno de Roberto.
3. ✅ 23/11: nombres reales comprobados en el KM; coinciden con la sección 1 salvo el texto de inicio de etapa.
4. ▶ Montar la View por bloques: cabecera ✅ → tiempos por fase ✅ → entradas/salidas/stock ✅ → stock por antigüedad ✅ → composición ✅ → sin actividad ✅ → comparativa → explorador. Lo que espera datos, con «Pendiente de datos».

## 7. Lo montado en «Natalidad View» (23/11, borrador)

Abreviaturas de la sección 1, más:
- `SENT` = `PU_LAST("o_custom_NatExpedientes", "el__EventosNatalidad"."SentidoResolucion", "el__EventosNatalidad"."SentidoResolucion" IS NOT NULL)`: último sentido de cada expediente. Así cada uno cuenta una sola vez.
- `CORTE` = `PU_MAX(CONSTANT(), "el__EventosNatalidad"."TIMESTAMP")`: fecha del último dato.
- `ID` = `"o_custom_NatExpedientes"."ID"`.

Variables de la View: `plazo_dias` (Number, 90 por defecto), `ver_por` (String, «Mes» por defecto) y `comp_dim` (String, «Sentido de la resolución» por defecto). Filtro guardado en el KM: **«Expedientes pendientes»** (`expedientes_pendientes`, no global) = `FILTER ALTA IS NOT NULL AND "o_custom_NatExpedientes"."FechaAnulacion" IS NULL AND RES IS NULL;`.

**Cabecera (5 KPI lists):**

| Bloque | KPI | PQL | Formato |
|---|---|---|---|
| Tramitación | Expedientes dados de alta | `COUNT(CASE WHEN ALTA IS NOT NULL THEN ID END)` | Rounded |
| Tramitación | Pendientes de resolver | `COUNT(CASE WHEN ALTA IS NOT NULL AND "FechaAnulacion" IS NULL AND RES IS NULL THEN ID END)` | Rounded |
| Tramitación | Expedientes resueltos | `COUNT(CASE WHEN RES IS NOT NULL THEN ID END)` | Rounded |
| Tramitación | % resueltos | resueltos `* 100.0 /` dados de alta | Rounded, «%» |
| Tramitación | Favorables | `COUNT(CASE WHEN SENT = 'Favorable' THEN ID END)` | Rounded |
| Tramitación | Denegados o desistidos | `COUNT(CASE WHEN SENT IN ('Denegación', 'Desistimiento') THEN ID END)` | Rounded |
| Tiempos | Tiempo E2E | `AVG(DAYS_BETWEEN(PRES, RES))` | Rounded, «d» |
| Tiempos | Registro → alta | `AVG(DAYS_BETWEEN(PRES, ALTA))` | Rounded, «d» |
| Tiempos | Alta → resolución | `AVG(DAYS_BETWEEN(ALTA, RES))` | Rounded, «d» |
| Tiempos | Fuera de plazo | `COUNT(CASE WHEN DAYS_BETWEEN(PRES, RES) > ${plazo_dias} THEN ID END) * 100.0 / COUNT(CASE WHEN DAYS_BETWEEN(PRES, RES) IS NOT NULL THEN ID END)` | Rounded, «%» |
| Reprocesos (1.ª versión) | Resueltos con anulación de etapa | `COUNT(CASE WHEN RES IS NOT NULL AND PU_COUNT("o_custom_NatExpedientes", "el__EventosNatalidad"."ID", "el__EventosNatalidad"."Actividad" = 'Anulación de Etapa') > 0 THEN ID END)` | Rounded |
| Reprocesos (1.ª versión) | % de resueltos | lo anterior `* 100.0 /` resueltos | Rounded, «%» |
| Fase previa | Entradas en registro, Aportaciones, Pendientes de alta, Duplicadas | marcador `/* Pendiente de datos: eReg (…) */` | — |
| Gestión económica | Altas en nómina, Beneficiarias activas, Pagos únicos, Dejan de cobrar, Importe pagado | marcador `/* Pendiente de datos: Nexus (y Soluciones) (…) */` | — |

Comprobaciones hechas (sin copiar cifras aquí):
- resueltos + pendientes + anulados sin resolver = dados de alta;
- favorables + denegados o desistidos + «Sin documento» = resueltos.

**Gráficos.** Van en una rejilla de 2 × 2, como en el mockup:
- fila 1: [Tiempo por fase | Entradas y salidas];
- fila 2: [Stock por fase | Composición].

La rejilla de Studio tiene 36 columnas y filas de 8 px. Las posiciones son: gráficos en las filas 73–109 y 109–145, mitad izquierda en las columnas 1–19 y mitad derecha en las 19–37. Composición: selector en 109–114 (columnas 29–37) y gráfico en 115–145.

Colores: solo hay tokens de la paleta. El gris pizarra del mockup (#464C6A) es **Context (20)**, exacto.

- **Entradas, salidas y stock** (*Grouped column*: dos métricas de columnas y una línea). La tabla común es el **event log**, porque altas y resoluciones van por fechas distintas.
  - Eje «Periodo (inicio)», formato fecha ISO (`%Y-%m-%d`), según el selector «Ver por»:
    ```
    CASE
    WHEN '${ver_por}' = 'Semana' THEN ROUND_WEEK("el__EventosNatalidad"."TIMESTAMP")
    WHEN '${ver_por}' = 'Quincena' THEN CASE WHEN DAY("el__EventosNatalidad"."TIMESTAMP") <= 15 THEN ROUND_MONTH("el__EventosNatalidad"."TIMESTAMP") ELSE ADD_DAYS(ROUND_MONTH("el__EventosNatalidad"."TIMESTAMP"), 15) END
    WHEN '${ver_por}' = 'Trimestre' THEN ROUND_QUARTER("el__EventosNatalidad"."TIMESTAMP")
    WHEN '${ver_por}' = 'Año' THEN ROUND_YEAR("el__EventosNatalidad"."TIMESTAMP")
    ELSE ROUND_MONTH("el__EventosNatalidad"."TIMESTAMP")
    END
    ```
    La quincena es «día 1» o «día 16» del mes. Comprobado: las dos quincenas suman lo del mes y el stock cuadra.
  - Columna 1, Altas: `COUNT(CASE WHEN "el__EventosNatalidad"."Actividad" = 'Alta del expediente' THEN "el__EventosNatalidad"."ID" END)`. Color Context (20).
  - Columna 2, Resueltos: `COUNT(DISTINCT CASE WHEN "el__EventosNatalidad"."SentidoResolucion" IS NOT NULL AND "el__EventosNatalidad"."TIMESTAMP" = RES THEN "el__EventosNatalidad"."NatExpedientes_ID" END)`: la primera resolución, una vez por expediente. Color Context (70).
  - Línea, Stock pendiente: `RUNNING_TOTAL(altas − resueltos − anulados sin resolución)`, con anulados = `Actividad = 'Expediente anulado' AND RES IS NULL`.
    - Va en el **eje secundario** y en Context (10).
    - `RUNNING_TOTAL` acepta agregaciones. El stock final cuadra con «Pendientes de resolver».
  - Ejes:
    - Y: «Expedientes dados de alta y resueltos»;
    - X: `${ver_por} (fecha de inicio)`;
    - Y secundario: «Pendientes al final del periodo».
- **Tiempo medio por fase** (*Column and line*), como el gráfico 1 del mockup.
  - Dimensión «Fase». Es un «cubo»: todo lo que no es fase 2–5 cae en Entrada, y las métricas deciden qué cuentan ahí.
    ```
    /* Las cinco fases del mockup. Los eventos que no son de las fases 2–5 caen en «1. Entrada»,
       pero ahí las métricas solo cuentan el evento de alta. Así no sale una barra «null» */
    CASE
    WHEN "el__EventosNatalidad"."Fase" IN ('2. Gestión del expediente', '3. Validación de terceros', '4. Intervención', '5. Resolución y pago') THEN "el__EventosNatalidad"."Fase"
    ELSE '1. Entrada (registro → alta)'
    END
    ```
  - Columnas, «Días de media» (Rounded, «d»).
    - En Entrada es registro → alta, por expediente. Cuadra con el KPI «Registro → alta».
    - En las fases 2–5 es la media **por etapa** (inicio → fin). Las etapas abiertas no cuentan.
    ```
    AVG(
      CASE
      WHEN "el__EventosNatalidad"."Actividad" = 'Alta del expediente' THEN DAYS_BETWEEN(PRES, ALTA)
      WHEN "el__EventosNatalidad"."Fase" IN (fases 2–5) THEN DAYS_BETWEEN("el__EventosNatalidad"."Fecha Inicio Etapa", "el__EventosNatalidad"."Fecha Fin Etapa")
      ELSE NULL
      END
    )
    ```
  - Línea, «Expedientes en la fase ahora» (eje secundario, Rounded). Con `N` =
    ```
    COUNT(DISTINCT CASE WHEN "el__EventosNatalidad"."Fase" IN (fases 2–5)
      AND ALTA IS NOT NULL AND "o_custom_NatExpedientes"."FechaAnulacion" IS NULL AND RES IS NULL
      AND PU_LAST("o_custom_NatExpedientes", "el__EventosNatalidad"."Fase", "el__EventosNatalidad"."Fase" IS NOT NULL) = "el__EventosNatalidad"."Fase"
      THEN "el__EventosNatalidad"."NatExpedientes_ID" ELSE NULL END)
    ```
    la métrica es `CASE WHEN N = 0 THEN NULL ELSE N END`.
    - Así Entrada queda vacía en vez de 0, porque los pendientes de alta son «Pendiente de datos» (eReg).
    - Comprobado: en cada fase coincide con el total de la barra del gráfico de stock.
  - **Sin filtro de componente.** Se quitó el *Attribute filter* de 7 fases: un filtro sobre eventos cambiaría `RES` y `PU_LAST` (MEMORIA, sección 5).
  - Colores:
    - barras con *Color mapping* por «Fase», regla «Entrada en gris claro»: Entrada en Context (70) y el resto (*Not Mapped*) en Context (20);
    - línea en Context (10).
  - Ejes: «Días de media en cada fase» / «Fase» / «Expedientes en la fase ahora». Leyenda sin título.
  - Diferencias con el mockup:
    - la leyenda solo puede mostrar las categorías de la regla («1. Entrada…») y la línea; el mockup dice «Antes del alta» y «Días de media en tramitación»;
    - falta el selector «Días de».
- **Stock pendiente por fase y antigüedad** (Stacked bar).
  - Dimensión «Fase actual»: `CASE WHEN PU_LAST("o_custom_NatExpedientes", "el__EventosNatalidad"."Fase", "el__EventosNatalidad"."Fase" IS NOT NULL) IS NULL THEN 'Sin etapa' ELSE PU_LAST(…) END`.
  - 4 métricas, una por tramo de `DAYS_BETWEEN(ALTA, CORTE)`, con los colores del mockup:
    - ≤ 30: Context (70);
    - 31–60: Context (50);
    - 61–90: Context (20);
    - > 90: Negative.
  - Filtro guardado «Expedientes pendientes». Es un filtro de **expedientes**: a los que quedan no les quita eventos, así que `PU_LAST` sigue bien. La suma cuadra con la cabecera.
  - Ejes: «Pendientes a la fecha de corte, por fase actual» / «Expedientes pendientes».
  - Se dejan Mantenimiento, Pago único y Sin etapa para que la suma cuadre con la cabecera, aunque el mockup solo tiene las 5 fases (pregunta 5).
  - Faltan las columnas «Pendientes» y «Antig. media» del mockup.
- **Composición** (*Bar*, horizontal), con un selector encima.
  - **Selector:** *Input dropdown* → *Manual input* → *Free text*, selección única, guarda en `${comp_dim}`.
    - 10 opciones: el texto es «Dimensión: …» y el valor, el nombre de la dimensión.
    - Opciones: Tipo de solicitud, Canal de entrada, Edad de la solicitante, Nacionalidad, País de nacimiento, Municipio de residencia, Hijos por solicitud, Sentido de la resolución, Requisito incumplido y Respuesta de la Intervención.
    - La variable guarda el **nombre** y no un código («sent»). Así el título del eje puede ser `${comp_dim}` tal cual: «↑ Sentido de la resolución».
  - Abreviatura nueva: `RINT` = `PU_LAST("o_custom_NatExpedientes", "el__EventosNatalidad"."Etapas", "el__EventosNatalidad"."Etapas" IN ('FAVORABLE CONCESIÓN', 'FAVORABLE CON OBS CONCESIÓN', 'ACTUACIÓN INTERESADA CONCESIÓN', 'DEV A INSTANCIA PROMO CONCESIÓN'))`. Es la última respuesta de la Intervención de cada expediente.
  - Dimensión «Categoría» (tabla común: `NatExpedientes`, una fila por expediente):
    ```
    /* Composición: el selector guarda en la variable comp_dim el nombre de la dimensión.
       Cada rama da una sola categoría por expediente. Los expedientes sin resolver
       (sentido) o sin respuesta (Intervención) van a una fila en blanco que no se pinta */
    CASE
    WHEN '${comp_dim}' = 'Edad de la solicitante' THEN COALESCE(PU_FIRST("o_custom_NatExpedientes", "o_custom_NatInteresados"."TramoEdad", "o_custom_NatInteresados"."EsSolicitante" = 'S'), 'No informado')
    WHEN '${comp_dim}' = 'Nacionalidad' THEN COALESCE(PU_FIRST("o_custom_NatExpedientes", "o_custom_NatInteresados"."NacionalidadAprox", "o_custom_NatInteresados"."EsSolicitante" = 'S'), 'No informado')
    WHEN '${comp_dim}' = 'Municipio de residencia' THEN COALESCE(PU_FIRST("o_custom_NatExpedientes", "o_custom_NatInteresados"."Municipio", "o_custom_NatInteresados"."EsSolicitante" = 'S'), 'No informado')
    WHEN '${comp_dim}' = 'Sentido de la resolución' THEN COALESCE(SENT, ' ')
    WHEN '${comp_dim}' = 'Respuesta de la Intervención' THEN COALESCE(RINT, ' ')
    /* Pendiente de datos: tipo de solicitud, canal de entrada, país de nacimiento, hijos por solicitud y requisito incumplido */
    ELSE 'Pendiente de datos'
    END
    ```
  - Métrica «Expedientes» (barra, con etiqueta de valor; orden descendente):
    ```
    /* Expedientes de cada categoría (suma 1 por expediente). No pintan barra:
       las dimensiones que aún no tienen datos y la fila en blanco de los expedientes
       sin resolver (sentido) o sin respuesta de la Intervención. SUM de todo NULL da NULL */
    CASE
    WHEN '${comp_dim}' IN ('Tipo de solicitud', 'Canal de entrada', 'País de nacimiento', 'Hijos por solicitud', 'Requisito incumplido') THEN NULL
    ELSE SUM(CASE
      WHEN '${comp_dim}' = 'Sentido de la resolución' AND SENT IS NULL THEN NULL
      WHEN '${comp_dim}' = 'Respuesta de la Intervención' AND RINT IS NULL THEN NULL
      ELSE 1
      END)
    END
    ```
  - Tooltip «% del total» (Rounded, «%»). Con `X` = el `SUM(CASE …)` de la métrica:
    ```
    /* % de cada categoría sobre el total de la dimensión (sin la fila en blanco).
       GLOBAL calcula la misma suma sin repartir por categorías */
    CASE
    WHEN '${comp_dim}' IN (las 5 pendientes) THEN NULL
    ELSE 100.0 * X / GLOBAL(X)
    END
    ```
    Comprobado: las categorías suman 100 %.
  - **Sin filtro de componente.** *Add Filter* del gráfico solo ofrece filtros por columna (o guardados en el KM), no PQL libre. Por eso los expedientes sin resolver no se filtran: van a la fila en blanco `' '` y la métrica los deja en NULL.
  - Colores: *Color mapping* por «Categoría», regla «Gris: sin dato o pendiente». «No informado», «Pendiente de datos» y «Sin documento» en Context (70); el resto (*Not Mapped*) en Context (20). Leyenda oculta (*Style* → *Legend* → *Hide*).
  - Ejes: Y = `${comp_dim}`; X = «Expedientes». *Allow scrolling* activado: en Municipio se ven 10 barras y el resto con scroll.
  - Probado en modo lectura con Sentido, Edad, Municipio, Respuesta de la Intervención y una pendiente (Tipo de solicitud).
  - Diferencias con el mockup:
    - cuenta **expedientes** según los filtros de la View (fecha de presentación), no «solicitudes recibidas» ni «resueltos en el periodo»;
    - en Respuesta de la Intervención cuenta la **última** respuesta de cada expediente; el mockup cuenta todas las respuestas del periodo;
    - los tramos de edad son los del dato, y salen ordenados por número de expedientes, no por edad;
    - la etiqueta solo muestra N; el % va en el tooltip (el mockup pone «N · X%»);
    - falta el subtítulo «N … · X % sin informar»;
    - el gris claro es Context (70) (#A9AED1); el #D3D3DD del mockup no está en la paleta;
    - queda una fila en blanco al final en Sentido y en Respuesta de la Intervención.

**Expedientes sin actividad (23/11):**

Debajo de la rejilla: una fila con el título y tres selectores, y la tabla a todo el ancho. Solo entran expedientes **pendientes** (con alta, sin anular y sin resolución).

Abreviaturas de este bloque:
- `ETAPA` = `COALESCE(PU_LAST("o_custom_NatExpedientes", "el__EventosNatalidad"."Etapas", "el__EventosNatalidad"."Fase" IS NOT NULL), 'Sin etapa')`: etapa actual. Es la misma regla que el gráfico de stock por fase.
- `ULTIMO` = `PU_MAX("o_custom_NatExpedientes", "el__EventosNatalidad"."TIMESTAMP")`: la última anotación del expediente, sea del tipo que sea.
- `DEPENDE` = el `CASE` de la columna «Depende de» (abajo).

*Variables del KM* (las modernas; se crean desde la View: icono *Variables* → **KNOWLEDGE MODEL** → «+»):

| Variable | Tipo | Por defecto | La escribe |
|---|---|---|---|
| `sa_umbral` | Number | 30 | selector de días |
| `sa_etapa` | String | `'Todas'`, **con** las comillas | selector «Etapa» |
| `sa_resp` | String | Todos | selector «Depende de» |

*Filtro guardado del KM* «Sin actividad (selectores)» (`sin_actividad_umbral`, no global). El PQL real lleva un comentario que explica cada variable:
```
FILTER ALTA IS NOT NULL
  AND "o_custom_NatExpedientes"."FechaAnulacion" IS NULL
  AND RES IS NULL
  AND DAYS_BETWEEN(ULTIMO, CORTE) > ${sa_umbral}
  AND ('Todas' IN (${sa_etapa}) OR ETAPA IN (${sa_etapa}))
  AND ('${sa_resp}' = 'Todos' OR '${sa_resp}' = '' OR DEPENDE = '${sa_resp}');
```
- `sa_etapa` llega como lista entre comillas (`'A', 'B'`), porque el selector admite varias etapas. Si no se marca ninguna, vuelve a su valor por defecto `'Todas'` y pasan todas.
- `sa_resp` llega sin comillas (selector de una sola opción). Por eso se compara con `'${sa_resp}'`.

*Selectores* (Input dropdown):

| Selector | Opciones | Selección | Variable |
|---|---|---|---|
| Etapa | *Load items*: dato `ETAPA` con el filtro guardado «Expedientes pendientes». La lista sale de los datos, con buscador y «Select all» | *Multiple* | `sa_etapa` |
| Días | *Manual input*: «Días sin actuación: más de 30 / 60 / 90 / 180» = 30 / 60 / 90 / 180 | *Single* | `sa_umbral` |
| Depende de | *Manual input*: «Depende de: todos» = Todos; Unidad gestora; Solicitante; Gestión económica; Intervención; Calendario | *Single* | `sa_resp` |

*Título* (Text box): «Expedientes sin actividad» y, debajo, «`n_sin_actividad` con más de `${sa_umbral}` días sin actuación».
- `n_sin_actividad` es un *placeholder* PQL: `COUNT("o_custom_NatExpedientes"."ID")` con el filtro guardado «Sin actividad (selectores)». Es el mismo filtro que usa la tabla, así que el número cuadra con ella.
- Lleva un comentario que nombra `${sa_umbral} · ${sa_etapa} · ${sa_resp}`, para que Studio lo recalcule al cambiar un selector.

*Tabla* (filtro guardado «Sin actividad (selectores)»; orden: «Días sin actuación», de más a menos):

| Columna | PQL |
|---|---|
| Expediente | `"o_custom_NatExpedientes"."CodigoExpediente"` |
| Fecha de registro | `PRES` |
| Etapa de Atlantix | `ETAPA` |
| Situación | `CASE` por la etapa actual: GESTIÓN EXPEDIENTE, REQUERIMIENTO y VALIDACIÓN TERCERO → «Pendiente de datos» (subestados de gestión, plazo del requerimiento, terceros); PROPUESTA FAVORABLE → «Esperando el fichero mensual»; INTERVENCIÓN CONCESIÓN → «En fiscalización»; ACTUACIÓN INTERESADA CONCESIÓN y DEV A INSTANCIA PROMO CONCESIÓN → «Respuesta desfavorable, sin devolver a gestión»; FAVORABLE CONCESIÓN y FAVORABLE CON OBS CONCESIÓN → «Respuesta favorable, pendiente de resolver»; RESOLUCIÓN FAVORABLE → «Esperando la nómina»; el resto, «—» |
| Depende de | `CASE` por la etapa actual: REQUERIMIENTO → Solicitante; VALIDACIÓN TERCERO → Gestión económica; INTERVENCIÓN CONCESIÓN → Intervención; PROPUESTA FAVORABLE y RESOLUCIÓN FAVORABLE → Calendario; el resto → Unidad gestora. Es el reparto del mockup, **sin validar** por la unidad. El filtro guardado repite este `CASE`: si se cambia uno, hay que cambiar el otro |
| Días desde el registro | `DAYS_BETWEEN(PRES, CORTE)` |
| Días sin actuación | `DAYS_BETWEEN(ULTIMO, CORTE)`. Pastilla de color: engranaje → *Data settings* → *Coloring* → *Thresholds* 60,5 y 90,5 → sin color / naranja / rojo, estilo *Value highlight* |
| Atrasos acumulados, Meses de atraso | marcador `/* Pendiente de datos: … vendrán de la nómina de Nexus */ 'Pendiente de datos'` |

Listo para los datos que faltan:
- «Días sin actuación» cuenta **cualquier** evento. Los que se añadan al event log (Atlantix, eReg o datos internos de la unidad) entran solos.
- La lista de etapas sale de los datos: una etapa nueva aparece sola en el selector.
- Una etapa nueva cae en «Unidad gestora» en «Depende de» y en «—» en «Situación». Así queda hasta que se añada a los dos `CASE` (el de la columna y el del filtro guardado).
- «Atrasos» y «Meses de atraso»: cuando llegue Nexus, solo cambia el PQL de la columna.

Probado en el lienzo, en modo lectura: cambian el contador y las filas con los días, con una etapa, con varias, con todas, sin ninguna y con «Depende de». Después se dejaron los tres selectores en su valor por defecto.

Para revisar con Roberto:
- Studio avisa de que el valor actual de una variable del KM «se aplica a todos los usuarios». Antes del Deploy, comprobar con dos usuarios si lo que elige uno en un selector lo ve también el otro.
- Han quedado **sin uso** las variables antiguas del KM `umbral_sin_actividad`, `etapa_sin_actividad` y `resp_sin_actividad`, y las de la View con el mismo nombre. Borrarlas con él.
- Exportar: la casilla de la tabla *Interactions* → *Export settings* → «Allow exporting from table» está **sin marcar**. Marcarla dejaría descargar números de expediente. Hay que decidirlo.

Diferencias con el mockup:
- no hay enlace «Abrir en Atlantix» (falta la dirección);
- «Atrasos» y «Meses de atraso» esperan a Nexus;
- no se puede exportar (pendiente de decidir).

**Barra de filtros (entre la cabecera y «Fase previa», como en el mockup):**

| Mockup | Componente | Qué hace |
|---|---|---|
| Desde / Hasta | *Date range* sobre `"o_custom_NatExpedientes"."FechaPresentacionInteresado"`, doble calendario | Filtro real. Filtra por **fecha de presentación**: lo que entra en el periodo y dónde está a la fecha de corte |
| Ver por | *Input dropdown* → `${ver_por}`: Semana, Quincena, Mes, Trimestre, Año (textos «Ver por: …») | Solo cambia el eje del gráfico de entradas y salidas |
| Año de solicitud | *Filter dropdown*: `YEAR("o_custom_NatExpedientes"."FechaPresentacionInteresado")` | Filtro real |
| Tipo de solicitud | *Filter dropdown*: `/* Pendiente de datos: tipo de solicitud (Nacimiento, Gestación, Adopción, Otros) */ CASE WHEN "o_custom_NatExpedientes"."ID" IS NOT NULL THEN 'Pendiente de datos' ELSE NULL END` | Marcador. Con el dato (Soluciones / eReg) solo cambia este PQL |
| Canal | *Filter dropdown*: `/* Pendiente de datos: canal de entrada (Sede electrónica, Oficina de registro, ORVE) */ CASE WHEN … THEN 'Pendiente de datos' ELSE NULL END` | Marcador, igual que el anterior |
| Plazo de tramitación | *Input dropdown* → `${plazo_dias}` (Number): 30, 60, 90, 120 y 180 días (textos «Plazo: … días») | Cambia el KPI «Fuera de plazo» |
| ✕ | *Button* → *Update variable*: `ver_por` = Mes, `plazo_dias` = 90 | Vuelve a los **parámetros** iniciales. Los filtros se quitan uno a uno o desde el embudo de la View: los botones no tienen acción «quitar filtros» |

Diferencias con el mockup:
- los tiempos del mockup son de «resueltos en el periodo», y aquí, de los presentados en el periodo;
- la fecha de corte sigue siendo el último dato (`CORTE`), no el «Hasta».

**Navegación (arriba a la derecha, junto al título):**
- Botón «Explorador de procesos →»: *Open linked view* → View **«Natalidad Explorador de procesos»**.
  - Contiene un *Process Explorer* sobre el event log `EventosNatalidad`, a todo el ancho.
- Botón «Comparativa de periodos →»: *Open linked view* → View **«Natalidad Comparativa de periodos»**.
  - Por ahora solo tiene un texto «en preparación» que adelanta lo que tendrá:
    - periodo 1 (el de los filtros) frente a periodo 2;
    - altas, resueltos, stock y tiempos;
    - actividad por mes, trimestre, semestre o año;
    - exportación a Excel.
- Las dos Views:
  - usan el mismo KM;
  - se abren como *Modal overlay*;
  - tienen *Sync view filters* en *Forwards*: heredan los filtros de la pantalla principal;
  - están ocultas en la navegación (ojo tachado), así que solo se llega a ellas desde los botones.

**Hallazgos para preguntar a la unidad (sin cifras):**
1. Casi no hay altas entre **dic-2024 y abr-2025**. ¿Cambio de convocatoria o de sistema?
2. «Anulación de Etapa» aparece en **más de la mitad** de los resueltos. Parece un apunte rutinario, no un reproceso. Hasta validarlo, el KPI se llama «con anulación de etapa». La versión buena es la vuelta a una fase anterior (sección 5).
3. «Fin sin concesión» tiene **duración media negativa**: hay etapas con fin anterior al inicio (calidad de datos).
4. Con 90 días, la **gran mayoría** de los resueltos está fuera de plazo. Confirmar el plazo real.
5. Hay expedientes pendientes cuya última etapa es **Mantenimiento** o **Pago único**, o que **no tienen etapa**. ¿Son stock de tramitación o seguimiento posterior a la concesión? El mockup solo cuenta las fases 1–5.
6. Hay expedientes **sin fecha de presentación**: salen como «-» en el filtro «Año de solicitud» y no entran en los tiempos desde el registro.
7. En `NatInteresados`, algunos **representantes** llevan `EsPrincipal = 'S'` y unos pocos expedientes **no tienen solicitante** (`EsSolicitante = 'S'`). ¿Es correcto? En Composición salen como «No informado».
8. En la etapa **PTE. ENVÍO INTERVENCIÓN**, el «Envío a Intervención» de la bitácora es siempre muy anterior (más de 60 días) al inicio de la etapa actual. ¿Qué fecha marca el inicio de esa etapa?
9. Arriba de «Expedientes sin actividad» salen expedientes de **2022** en RESOLUCIÓN FAVORABLE o FAVORABLE CONCESIÓN que llevan **años** sin actuación. ¿Están cerrados en otro sistema (por ejemplo, ya pagados en Nexus)?
10. ¿Vale el reparto de «Depende de» del mockup (requerimiento → solicitante, validación de terceros → gestión económica, etc.)? En el requerimiento falta la fecha límite de aportación para separar «en plazo» y «plazo vencido».
11. Para el enlace «Abrir en Atlantix», ¿qué dirección abre un expediente?

**Falta en la View:**
- decidir si la tabla de expedientes sin actividad se puede exportar;
- el contenido de la comparativa de periodos;
- % favorables;
- selector «Días de»;
- datos de tipo de solicitud y canal, que hoy son marcadores.

Cabecera de texto: «Dirección General de Infancia, Familia y Fomento de la Natalidad» (corregida el 23/11; venía copiada de Dependencia) / «Consejería de Familia, Juventud y Asuntos Sociales» / «Cuadro de mando de Ayudas por gestación, nacimiento o adopción · Seguimiento del proceso».
