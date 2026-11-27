# Traspaso · Cuadro de mando de Dependencia en Celonis (View)

Documento para que una conversación nueva siga exactamente donde se quedó la anterior (06/11/2026; tablas nuevas, 24/11; modelo nuevo cargado en desarrollo y View ampliada, 27/11; View completa con todos los bloques del mockup, 27/11 por la noche). Leer **antes** que nada: `CLAUDE.md`, `dependencia/MEMORIA_DEPENDENCIA_CELONIS.md`, `dependencia/MAPEO_MOCKUP_CU1.md` y `dependencia/MAPEO_TABLAS_SIDEMA.md`.

**Regla de oro:** datos de la Comunidad de Madrid, nunca a GitHub ni a nada público (artifacts incluidos). Ni logins, ni IDs de solicitud reales, ni filas. Los ficheros con datos van solo al scratchpad. En el repositorio, solo SQL, PQL, estructura y decisiones.

## 1. Qué estamos haciendo

Anthony (Madrid Digital, primera vez con Celonis) está montando en **Celonis Studio** la View **«Dependencia View»** para que se parezca lo máximo posible al mockup `mockups/MockupCU1_v2.html` (Cuadro de Mando de Gestión de Equipo · CU1). Al principio solo había **3 tablas** de SIDEMA (`SIDM_SOLICITUD`, `SIDM_HIST_ESTADO`, `SIDM_ESTADO_SOLICITUD`). Desde el 27/11 el modelo de desarrollo tiene también las tablas nuevas: valoración, valorador, PIA, bandeja, subsanación, etc. (sección 2).

- Ruta: **Studio > Implementación > Dependencia** → «Dependencia View» y el Knowledge Model `dm_test_perspective_custom_dependencia-km`. El 27/11 Roberto aprobó *Test changes*, la perspectiva con los eventos nuevos y el KM: hecho.
- **Ahora lo hace desde el editor visual, NO por YAML** (lo pidió él). Le guío **paso a paso**: qué hacemos, por qué, cómo, qué debería ver. Un paso cada vez; él manda capturas.
- Desde la sesión en la nube no se puede controlar su navegador. **El 06/11 y el 27/11 se trabajó en local con Claude in Chrome** (Anthony lo pidió): solo editor visual y lectura del DOM. El 27/11 sí se pudo **leer** la definición de la View, en solo lectura (un GET a `initial-load-v2` desde la propia página). Los cambios, siempre en el editor visual.
- **Create version** y **Deploy** (producción), nunca sin Roberto. En «Pruebas Anthony» (tarea de extracción), salir siempre con **Discard**.

## 2. Modelo de datos en Celonis (lo que funciona en PQL)

- Objeto: **`"o_custom_SolicitudDependencia"`** (v2 desde el 27/11) con atributos:
  - de antes: `ID`, `NumeroSolicitud`, `FechaSolicitud`, `FechaRegistroEntrada`, `FechaAlta`, `FechaFinPlazo`, `FechaBaja`, `CodigoEstadoActual`, `EstadoActual`, `TipoSolicitud`, `Urgente`, `Traslado`, `Extinguido`, `NumeroRevision` (**texto**: '1', '2'…), `IdSolicitudOriginal`, `UsuarioAlta` e `IdSolicitante`;
  - nuevos: `FechaNacimiento`, `Sexo`, `Municipio`, `ZonaDependencia`, `Distrito`, `FechaFallecimiento`, `MotivoAlta`, `CodigoGrado` (texto, '0' a '3'), `GradoNivel`, `TipoBaremo`, `TipoResolucionGrado`, `FechaResolucionGrado` y `Origen`.
- **Objetos nuevos (27/11)**, enlazados en la perspectiva (atributos completos en los SQL 06–08):
  - `"o_custom_ValoracionDependencia"` (→ Solicitud y → Valorador): `TipoBaremo` (BVD / EVE), `Telematica` (S / N), fechas de valoración y de grabación…
  - `"o_custom_ValoradorDependencia"`.
  - `"o_custom_PIADependencia"` (→ Solicitud): `CodigoEstadoPIA`, `EstadoPIA`, `AgrupacionPrestacion`, `FechaResolucionPIA`, `FechaConsultaBeneficiario` (vacía en la muestra)…
- Eventos: **a través del event log `"el__EventosDependencia"`** (perspectiva «Dependencia», objeto principal SolicitudDependencia).
  - Desde el 27/11 tiene **17 eventos**: Registro, Alta y CambioEstado de antes, más los 14 de los SQL 09–22.
  - Columnas: `ID`, `ACTIVITY`, `TIMESTAMP`, `CodigoEstado`, `Estado`, `Fase`, `Usuario`, `SolicitudDependencia_ID`, `LEAD_OBJECT_ID`, `epoch`, `_CELONIS_CHANGE_DATE`.
- En `ACTIVITY`, los eventos nuevos se llaman **`'e_custom_<Evento>'`**: `'e_custom_CambioEstadoPIA'`, `'e_custom_ResolucionPIA'`, `'e_custom_SubsanacionRequerida'`… Para quedarse con un evento: `"el__EventosDependencia"."ACTIVITY" = 'e_custom_…'`. En la muestra no todos tienen filas: urgencias, traslados, llamadas y requerimientos del PIA salen vacíos.
- Las tablas `"e_custom_…"` sueltas **no están conectadas** al objeto (PU_MIN da «tables are not connected»): para cruzar con la solicitud, siempre el event log.
  - **Excepción:** `"e_custom_RecepcionBandeja"` se usa sola en «Pendientes de grabar». Las entradas sin grabar no tienen solicitud y no entran en el event log, y un `COUNT` sobre una sola tabla no necesita conexión.
- Modelo cargado en **desarrollo** con *Test changes* el 27/11 (Roberto lo aprobó). Detalle en la sección 9g de la memoria. Sin Create version ni Deploy.
- Variables de la View: solo `objetivo_dias` (30), `objetivo_f2` (120) y `objetivo_f3` (180).
- El KM tiene también **`"el_custom_SolicitudDependencia"`** («SolicitudDependencia Event Log»), con las mismas columnas y marcado como **Default**. No se usa: en los PQL, nombrar siempre `"el__EventosDependencia"` de forma explícita.

### Revisión en el navegador (06/11, solo lectura)
- **Objects & Events** (pool «OCPM DataPool VALIDACION y PRODUCCION»): objeto `SolicitudDependencia` con 17 atributos tipados (ID String PK; fechas Datetime; resto String) y etiqueta Dependencia. Eventos relacionados («involves one»): `RegistroEntradaDependencia` (ID, Time), `AltaSolicitudDependencia` (ID, Usuario, Time) y `CambioEstadoDependencia` (ID, CodigoEstado, Estado, Fase, Usuario, Time).
- Perspectiva «Dependencia»: 1 objeto, 1 event log, data model **Successful** (última ejecución 06/11 07:17), enlazada al paquete Dependencia (Draft) como `test:perspective_custom_Dependencia`.
- **Ojo:** en la lista de transformaciones, `SolicitudDependencia` y `CambioEstadoDependencia` se ejecutaron el 06/11 a las 07:15, pero `RegistroEntradaDependencia` y `AltaSolicitudDependencia` salen **«Not executed»**. La View sigue mostrando eventos. Comprobar con un recuento por `ACTIVITY` y, si faltan, preguntar a Roberto.
- Studio: 3 cambios sin versionar (contador de Create version). No se ha tocado.
- Datos cargados (entorno de pruebas): **200 solicitudes** (100 de 2007 y 100 del 1.er semestre de 2025, metidas con INSERT por Anthony), **399 eventos** (registro + alta; una solicitud sin fecha de registro), **0 cambios de estado** porque el histórico local es de otras solicitudes. Por eso subsanación, AVC, citación, dictamen y grado salen a 0 o «–».

## 3. Lecciones de PQL en esta View (importante)

- **`CASE` solo en forma completa:** `CASE WHEN cond THEN … END`. La forma corta `CASE campo WHEN valor` da «Syntax error near RIGHT».
- **Variables de la View:** `${nombre_variable}`. Si el nombre no coincide con una variable existente, Celonis no la sustituye y da «Syntax error near [$]». La variable del objetivo de la fase 1 se llama **`objetivo_dias`** (VIEW, tipo número, por defecto 30). Las de las fases 2 y 3 son `objetivo_f2` (120) y `objetivo_f3` (180). Un `${…}` dentro de un comentario `/* */` también se sustituye, sin romper nada.
- Estado actual: comparar con `RIGHT("o_custom_SolicitudDependencia"."CodigoEstadoActual", 2)` y códigos entre comillas (`'01'`).
- Del histórico a la solicitud: `PU_MIN("o_custom_SolicitudDependencia", "el__EventosDependencia"."TIMESTAMP", "el__EventosDependencia"."CodigoEstado" IN ('90','34','36'))` (fecha de entrada en un estado) y `PU_COUNT(…)` (vueltas).
- `GLOBAL(…)` para porcentajes y comparaciones con el total del equipo.
- Fechas de referencia sobre el último dato (`PU_MAX(CONSTANT(), …)`) mejor que `TODAY()` mientras haya muestras antiguas.
- Un filtro (desplegable o fechas) **filtra toda la View**, aunque esté dentro de una pestaña. Pendiente de configurar en **Interactions** qué escucha cada componente.
- El placeholder de un Input box no se ve si la variable tiene valor por defecto: se usa un Text box como etiqueta.
- Un KPI de texto (Previsión, Estado) **sin agregación** devuelve una fila por expediente: envolverlo en un `CASE` sobre agregados (`COUNT`, `AVG`…).
- Para «pendiente de datos» sin romper el KPI: un comentario `/* Pendiente de datos: … */` y una expresión agregada que da nulo (`AVG(CASE WHEN "o_custom_SolicitudDependencia"."ID" IS NULL THEN 0.0 END)`). Sale «–» y queda el PQL documentado.
- Formato de porcentaje: **Rounded con unidad «%»** si el PQL ya multiplica por 100 (el formato «Percentage» vuelve a multiplicar).
- Nunca números fijos de objetivo en los PQL (había `120` en el gráfico y KPIs de la fase 2): siempre `${objetivo_dias}`, `${objetivo_f2}`, `${objetivo_f3}`.
- Un componente vacío (sin filas) muestra «There's data missing» en rojo. Con los datos de prueba pasa en todo lo que depende de cambios de estado (47, 90/34/36, 60/30/25…). No es un error de PQL.

**Lecciones del 27/11:**
- **Tipos:**
  - `TO_STRING` solo acepta enteros, ni texto ni decimales; `TO_INT` no acepta decimales. Para pasar un decimal a texto: `TO_STRING(FLOOR(…))`.
  - `YEARS_BETWEEN` devuelve decimales: `FLOOR(…)` da los años cumplidos.
- `||` con un nulo deja nula toda la cadena: en cadenas de prueba, `COALESCE(…, 'nulo')` en cada trozo.
- **Explorar valores sin sacar filas:** en un KPI de prueba que no se guarda, `PU_COUNT_DISTINCT(CONSTANT(), col)` (cuántos valores hay) y `PU_FIRST` / `PU_LAST(CONSTANT(), col, filtro, ORDER BY col ASC)` (el primero y el último).
- **Desplegables:**
  - El Preview de un desplegable enseña filas con repetidos (hasta 50), no los valores distintos.
  - Un desplegable da **un valor por fila**. Si las opciones del mockup se solapan (en Tipo de valoración, «BVD», «Telemática» e «Inicial» a la vez), se usa una etiqueta combinada («BVD · Telemática · Inicial»).
  - Un desplegable sobre otra tabla (valoraciones, PIA) cambia la **tabla común**. El filtro llega a las solicitudes por la relación: se quedan las que tienen alguna valoración o PIA con ese valor.
- **Agrupar por palabras clave** (`UPPER(col) LIKE '%…%'`): el orden de los `WHEN` importa, gana el primero. Por ejemplo, «Desestimatoria grado 0» va a Grado 0 antes que a Denegatoria.
- Un KPI sobre una tabla sin conexión con la solicitud (la bandeja) **no escucha** los filtros de la solicitud, como Periodo. En «Pendientes de grabar» es lo correcto: es una foto de la bandeja.

### Trucos del editor (Studio)
- **Con Claude in Chrome:**
  - El editor PQL es Monaco. `monaco.editor.getEditors()` y quedarse con el que está dentro de `pql-qb-editor`; `setValue(…)` pega el PQL. Para el nombre visible, poner el valor en el `input` del panel derecho y lanzar `input`, `change` y `blur`.
  - Al recargar la página se pierden los atajos definidos en `window`: hay que volver a definirlos.
  - Después de Ctrl+Enter, esperar antes de leer el Preview del DOM: si no, se lee el resultado anterior.
  - Si una salida de JavaScript sale «[BLOCKED: Cookie/query string data]», no darle la vuelta: devolver solo índices o tipos.
- Dentro del contenedor de pestañas: doble clic para entrar y clic en el componente.
- Abrir el PQL de cada KPI: pinchar el componente y luego el chip del KPI en Settings. El botón `</>` del panel abre el editor de todo el componente (en gráficos y tablas, pinchando la cabecera de cada columna del Preview se cambia de métrica).
- **Done no cierra** si el Preview dice «Data requirements … not met»: antes, Ctrl+Enter para ejecutar.
- Mover componentes: arrastrar el asa «Move Component» (arriba a la izquierda del componente seleccionado). Se puede soltar encima de otro; algunos huecos el editor no los acepta.
- Reordenar columnas con teclado: foco en el chip, Espacio, flechas **de una en una**, Espacio.
- Guardar con **Save** (borrador). Cancelar un editor con cambios pide «Close Editor» y descarta todo lo del editor.

## 4. Cómo está la View ahora (revisada y auditada el 27/11 por la noche, guardada como borrador)

**27/11 (noche): la View tiene todos los bloques del mockup CU1 con componentes reales.** Ya no queda ningún texto «⚠ Pendiente de datos» ocupando el sitio de un componente. Lo que aún falta (catálogos, efectivos, umbrales) está explicado en el comentario `/* */` de cada PQL. En algunas columnas sale el valor «Sin dato» o «Pendiente de datos» porque la muestra no trae ese campo (Tipo y Zona del valorador, Perfil de gestión del tramitador). No hay números fijos de objetivo ni `TODAY()` / `NOW()`. Todo está guardado con **Save**: no se ha hecho Create version ni Deploy.

**Cabecera (fuera de las pestañas):**
- Logo de la Comunidad de Madrid y texto de la DG.
- **Actualizado** (27/11): Text box alineado a la derecha, junto al título: «Actualizado: {fecha_corte}». Muestra la fecha y la hora del último evento cargado.
  - Ojo: respeta los filtros activos.
  - En la muestra, el último evento es un alta de prueba.
- Solicitudes activas: sin cambios. Falta que Andrés diga qué estados cierran un expediente.
- **Plazo proceso completo** = Tiempo E2E de la fase 1 + el de la fase 2 + el de la fase 3, como dice el mockup («suma E2E fases 1→3»).
- **Cumplimiento SLA global y Fuera de plazo:** miden de la solicitud al grado resuelto (estados 90/34/36), frente a `${objetivo_f3}`.
  - Ojo: si se cambia el objetivo de la fase 3, cambia también el SLA global.
  - Hay que decidir si el SLA global es el plazo legal (`FechaFinPlazo`) o una variable propia.
- Altas / mes y vs mes anterior.

**Título** «Cuadro de Mando de Gestión de Equipo» y **barra de filtros común:**
- Periodo: Date range sobre `"o_custom_SolicitudDependencia"."FechaAlta"`, con display name «Periodo».
- **Territorio:** municipio del solicitante. Para la mancomunidad del mockup hace falta el catálogo municipio → mancomunidad.
- **Edad:** edad al presentar la solicitud, en los tramos del mockup.
- **Limpiar** = el embudo de la propia View (arriba a la derecha, «N filters applied») → **Reset filters**. El componente Button de Studio no tiene ninguna acción para borrar filtros. La *Filter bar* lateral se probó y se dejó apagada, como estaba.

**Contenedor con 3 pestañas.** En las tres, «ESTA FASE» tiene ya el **% del equipo total** (27/11): «% del equipo total · de {personas_total}». Las personas se cuentan así:
- Fase 1: usuarios de alta.
- Fase 2: usuarios de los eventos de citación y valoración (fases 2a y 2b).
- Fase 3: técnicos PIA (usuarios de `CambioEstadoPIA`).

Es una aproximación con usuarios del sistema. Faltan los efectivos reales por fase, y quien trabaja en dos fases cuenta dos veces.

- **Fase 1 · Grabación de solicitudes:**
  - Filtros propios: Estado (4 grupos), Objetivo (Input box → `objetivo_dias`), Origen y **Atributo** (27/11).
    - Origen es el canal de la bandeja. En la muestra todo sale «Sin dato», porque la bandeja cargada no cruza con las solicitudes grabadas.
    - Atributo es un desplegable Territorio / Edad / Origen que guarda la variable `atributo_f1` (por defecto «Territorio»). Lo usa la tabla «Flujo por atributo».
  - **Pendientes de grabar:** entradas de la bandeja sin solicitud grabada. Ojo: es un `COUNT` aislado de la tabla `e_custom_` y no responde a los filtros.
  - «ESTA FASE»: Personas involucradas, Tiempo E2E, vs objetivo, % del equipo total, Previsión carga, Entran/sem y Resuelven/sem.
  - Plazos de tramitación: KPIs y gráfico dentro / fuera de plazo, con Plazo medio y Objetivo SLA. Leen `${objetivo_dias}`.
  - **Subsanaciones y AVC** (27/11): la Tasa de subsanación y el Número de subsanaciones cuentan una vez cada expediente. Un expediente cuenta como subsanado si tiene un requerimiento (evento `SubsanacionRequerida`) o si pasó por los estados 60/30/25.
  - **Tabla «Subsanación · por motivo»** (27/11): Motivo (código) · Exp. · % · Plazo +.
    - El motivo es el código del primer requerimiento. Para poner el texto del motivo falta el catálogo (bloque 2 del script).
    - La fila «0 · sin subsanación (referencia)» es la base con la que se compara el Plazo +.
  - **Tabla «Flujo por atributo»** (27/11): Atributo · Exp. · % sub. · Plazo + · Días bloq. subs.
    - La primera columna cambia según el desplegable Atributo.
    - Días bloq. subs. es el antiguo pendiente «KPI días bloqueado en subsanación».
  - Tabla «AVC · Reproceso en bucle»: Nº de vueltas AVC · Exp. · % · Plazo +.
  - Detalle por Trabajador: dos tablas, Equipo de Grabación y Equipo de Subsanación.
- **Fase 2 · Valoración:**
  - Filtros propios: Resolución de grado y Tipo de valoración.
  - «ESTA FASE» con PQL propios y % del equipo total.
  - **Productividad y carga** (27/11): Total valoradores · Media exp/persona · Sobrecargados (>115 %), y el gráfico «# Valoradores» por tramo de carga.
  - **Variabilidad del criterio BVD** (27/11):
    - KPIs: Valoradores activos (BVD) · Criterio sesgado (>10 pp) · % Alineación.
    - Tabla «Distribución de grados BVD por valorador»: G0 · G1 · G2 · G3 · Desv. (pp) · Criterio.
    - El grado de cada valoración es la banda del mayor baremo (físico o cognitivo): <25 G0, 25–49 G1, 50–74 G2, ≥75 G3.
  - Plazos: gráfico «Expedientes valorados: dentro vs fuera del plazo objetivo» y KPIs «% en plazo (≤ ${objetivo_f2} d)» / «% fuera (> ${objetivo_f2} d)». El nombre del KPI enseña el objetivo que se está usando.
  - **Hitos** (27/11): tres tramos.
    - ④ Citación → ⑤ Valoración: no imputable al valorador, depende de la agenda.
    - ⑤ Valoración → ⑥ Grabación.
    - ⑥ Grabación → ⑦ Dictamen.
  - **Detalle por Trabajador — Valoración** (27/11): Trabajador · Tipo · Zona · Expedientes · Carga · Plazo medio · vs equipo · Variab. criterio · Estado. Tipo y Zona salen «Sin dato» porque vienen vacíos en la muestra.
  - **Evaluación individual del valorador** (27/11): Valoraciones · Cita → visita (no imputable) · Días a grabación · Días a dictamen · Total imputable · Nivel (bandas del mockup: <15 d, 15–25 d, ≥26 d; por confirmar).
- **Fase 3 · Resolución de PIA:**
  - Filtros propios: Estado fase 3 y Tipo de prestación. Van sobre la tabla de PIA: filtran las solicitudes que tienen algún PIA con ese valor.
  - «ESTA FASE» completa, con % del equipo total. El Tiempo E2E va del primer trámite del PIA a la primera resolución del PIA. No empieza en la resolución del grado porque en la muestra grado y PIA se resuelven el mismo día y saldría 0 (pregunta a Andrés).
  - **Plazos de tramitación** (27/11): PIA resueltos · Resueltos en plazo · Resueltos fuera de plazo, y el gráfico por mes de `ResolucionPIA` con Plazo medio y Objetivo SLA (`${objetivo_f3}`).
    - Ojo: aquí el plazo va de la solicitud a la resolución del PIA (proceso completo).
    - El E2E de «ESTA FASE» solo mide la fase 3, pero los dos se comparan con el mismo `objetivo_f3`. Pregunta a Andrés.
  - **Productividad y carga** (27/11): Técnicos PIA · Media exp/técnico · Sobrecargados (>115 %), y el gráfico «# Técnicos PIA por tramo de carga».
  - **Variabilidad de la prestación** (27/11):
    - Tabla «Prestación prescrita por territorio»: Territorio · PIA · Resid. · SAD · Teleas. · Desv. CM.
    - KPIs: Territorios con PIA · Territorios atípicos (>10 pp) · Mayor dispersión.
    - El territorio es el municipio hasta que llegue el catálogo de mancomunidades.
  - **Detalle por Trabajador — Resolución de PIA** (27/11): Técnico PIA · Expedientes · Carga · Plazo medio · vs equipo · Territorio principal · Estado · Variab. prescrip. (pp de Residencia frente al equipo).
  - **Evaluación individual del tramitador — Gestión del PIA** (27/11): Exp. resueltos · Plazo imputable · vs equipo · % con requerimiento · Llamadas/exp · Perfil de gestión.
    - % con requerimiento y Llamadas/exp necesitan los eventos de requerimiento y de llamada del PIA, que el modelo aún no tiene.
    - Perfil de gestión sale «Pendiente de datos».

**Auditoría del 27/11 (noche):** se comprobó en el navegador que los KPIs, las tablas y los gráficos de cada fase cuadran entre sí. Las cifras no se apuntan aquí. Observaciones para Roberto y Andrés:
- Fase 3: el E2E mide solo la fase, mientras que «Resueltos en plazo» y el gráfico miden de la solicitud al PIA. Los dos se comparan con `${objetivo_f3}`.
- Fase 3: «Exp. resueltos» de la evaluación del tramitador cuenta el expediente para cada tramitador que interviene en él, así que la suma de la columna puede ser mayor que «PIA resueltos».
- Fase 2: «Media exp/persona» cuenta pares expediente–valorador. Si dos valoradores valoran el mismo expediente, cuenta para los dos.
- Origen sale vacío en la muestra (la bandeja no cruza con las solicitudes).
- La muestra trae unas filas de prueba. Se notan en un mes antiguo del gráfico de la fase 1, en «Sin dato de edad» y en «Actualizado». Con los datos reales desaparecen.
- Pendientes de grabar no responde a los filtros (`COUNT` aislado de la bandeja).
- Umbrales que se han puesto por el mockup y hay que confirmar:
  - carga: 115 % sobrecarga, 70 % subcarga y 130 % en el gráfico de tramos;
  - criterio BVD: sesgo >10 pp, leve 5–10 pp y alineado ≤5 pp;
  - territorios atípicos: >10 pp;
  - nivel del valorador: <15 días, 15–25 días y ≥26 días.

## 5. Dónde nos quedamos (siguiente paso exacto)

Todo lo anterior está **guardado con Save (borrador)**. No se ha hecho Create version ni Deploy (eso, con Roberto).

Historia corta:
- **24/11:** llegaron las tablas de SIDEMA para el CU1 y el CU2: 29 tablas en la extracción «Extraccion Dependencia» (data job «Dependencia VASOCIAL_SIDM»).
  - Mapeo: `dependencia/MAPEO_TABLAS_SIDEMA.md`.
  - Script de vistas para Roberto: `dependencia/sql/VistasSIDMPRODv3.sql`.
  - La extracción **sigue fallando por Snappy**, así que en Celonis solo están las muestras.
- **27/11 (mañana):** modelo de las tablas nuevas en Objects & Events: 4 objetos y 14 eventos, todos «Passed» (SQL en `dependencia/sql/05…22`, detalle en la sección 9g de la memoria).
- **27/11 (tarde):** *Test changes* hecho con el OK de Roberto. La View lee las tablas nuevas, y se montaron los filtros que faltaban y la «ESTA FASE» de la fase 3.
- **27/11 (noche):** la View está completa (sección 4): se sustituyeron todos los textos «pendiente» de las fases 1, 2 y 3 por componentes reales, y se añadieron el % del equipo total, Actualizado y Limpiar. Se auditó.

Pendiente, en este orden:
1. **Enseñarle la View a Roberto** y, si le parece bien, hacer **Create version** (solo con su OK).
2. **Roberto:** revisar el script v3, ejecutar el bloque 3 y contestar las preguntas (sección 8 del mapeo).
   - Cuando las vistas estén en PROD y funcione la extracción, se apunta la extracción a `SIDM_V_DEP_*` con «Rename target table», para no cambiar los nombres de las tablas.
   - Pasarle el catálogo de motivos de subsanación (bloque 2), para poner el texto del motivo en la tabla «Subsanación · por motivo».
3. **Preguntas a Andrés** (sección 10 de la memoria):
   - ¿Grado y PIA se resuelven a la vez? ¿El estado 90 del PIA es «expediente resuelto»?
   - ¿Qué estados cierran un expediente? (Solicitudes activas)
   - ¿Dónde va el origen «Presencial»?
   - SLA global: ¿plazo legal (`FechaFinPlazo`) o una variable propia?
   - Fase 3: ¿el objetivo se mide sobre la fase (E2E) o sobre el proceso completo (solicitud → PIA)?
4. **Datos que faltan para terminar de afinar:**
   - catálogo municipio → mancomunidad (Territorio y Variabilidad de la prestación);
   - Origen que cruce con las solicitudes;
   - efectivos reales por fase (% del equipo total);
   - Tipo y Zona del valorador (vienen vacíos);
   - eventos de requerimiento y de llamada del PIA (evaluación del tramitador).
5. **Confirmar los umbrales** de la auditoría (sección 4).
6. **Interactions:** que la cabecera solo escuche los filtros comunes, y que los filtros de cada fase no se queden puestos en las otras.
7. Detalles:
   - formato del mes del gráfico de la fase 1 (sale MM/AAAA; el mockup usa `%b %Y`);
   - hueco pequeño encima de «% en plazo» en la fase 2;
   - tabla «Ver por expediente» con los 9 hitos;
   - comprobar que Tipo de valoración permite selección múltiple.

## 6. PQL listos para usar

Abreviaturas solo para leer; en Celonis se escribe todo completo.
- S = `"o_custom_SolicitudDependencia"`
- EL = `"el__EventosDependencia"`

**Objetivo en KPIs (fase 1):**
```
COUNT(CASE WHEN DAYS_BETWEEN("o_custom_SolicitudDependencia"."FechaSolicitud", "o_custom_SolicitudDependencia"."FechaAlta") <= ${objetivo_dias} THEN "o_custom_SolicitudDependencia"."ID" END)
```
(fuera de plazo: `>`); línea del objetivo: `AVG(CASE WHEN "o_custom_SolicitudDependencia"."FechaAlta" IS NOT NULL THEN ${objetivo_dias} * 1.0 END)`; vs objetivo: `AVG(DAYS_BETWEEN(S."FechaSolicitud", S."FechaAlta")) - ${objetivo_dias}`.

**Tooltip % fuera de plazo:**
```
COUNT(CASE WHEN DAYS_BETWEEN("o_custom_SolicitudDependencia"."FechaSolicitud", "o_custom_SolicitudDependencia"."FechaAlta") > ${objetivo_dias} THEN "o_custom_SolicitudDependencia"."ID" END) * 100.0
/ COUNT("o_custom_SolicitudDependencia"."FechaAlta")
```

**Altas / mes (media del periodo):**
```
COUNT("o_custom_SolicitudDependencia"."FechaAlta") * 1.0
/ COUNT(DISTINCT ROUND_MONTH("o_custom_SolicitudDependencia"."FechaAlta"))
```

**Pendientes de grabar** (27/11, bandeja de eReg; antes era una aproximación con las fechas de la solicitud):
```
/* Pendientes de grabar: entradas de la bandeja de eReg sin solicitud grabada (IT_ESTADO = 1, sin baja
   y sin solicitud con el mismo NMREFERENCIA). Se lee la tabla del evento RecepcionBandeja porque estas
   entradas, al no tener solicitud, no entran en el event log. */
COUNT(
  CASE
    WHEN "e_custom_RecepcionBandeja"."SolicitudDependencia_ID" IS NULL
     AND "e_custom_RecepcionBandeja"."EstadoBandeja" = '1'
     AND "e_custom_RecepcionBandeja"."FechaBaja" IS NULL
    THEN "e_custom_RecepcionBandeja"."ID"
  END
)
```

**Marcador de filtro sin datos:**
```
CASE WHEN "o_custom_SolicitudDependencia"."ID" IS NOT NULL THEN 'Pendiente de datos' END
```

**Estado fase 1** (grupos del mockup):
```
CASE
  WHEN RIGHT("o_custom_SolicitudDependencia"."CodigoEstadoActual", 2) IN ('01','03') THEN 'Alta de solicitud'
  WHEN RIGHT("o_custom_SolicitudDependencia"."CodigoEstadoActual", 2) IN ('60','30','25') THEN 'Pendiente de subsanación'
  WHEN RIGHT("o_custom_SolicitudDependencia"."CodigoEstadoActual", 2) IN ('05','20','15') THEN 'En bucle de AVC'
  WHEN RIGHT("o_custom_SolicitudDependencia"."CodigoEstadoActual", 2) IN ('00','40','39','99','98','06','41','42','43','07','11','44','45','48','32','47','33','50','51','35','04','70','71','90','34','36','91') THEN 'Completa · pasa a valoración'
  ELSE 'Otros'
END
```

**Estado fase 2** (40 Pendiente de citación de valoración · 07 En proceso de valoración en centros · 42 Citación manual · 43 Pendiente de valoración · 45 Pendiente de realizar dictamen técnico · 47 Pendiente de Comisión de Valoración · 50 Pendiente de resolución de grado · 90 Grado resuelto · ELSE 'Otros'), un `WHEN RIGHT(…, 2) = 'xx' THEN '…'` por estado.

**Tabla AVC · Reproceso en bucle:**
- Dimensión: `CASE WHEN PU_COUNT(S, EL."TIMESTAMP", EL."CodigoEstado" IN ('05','20','15')) = 0 THEN '0 · sin AVC (referencia)' WHEN … = 1 THEN '1 vuelta' WHEN … = 2 THEN '2 vueltas' ELSE '3+ vueltas (bucle)' END`.
- Columnas:
  - Exp.: `COUNT(DISTINCT S."ID")`.
  - %: sobre `GLOBAL` de las que tienen AVC > 0.
  - Plazo +: `AVG(días fase 1) - GLOBAL(AVG(CASE WHEN PU_COUNT(…) = 0 THEN días fase 1 END))`.

**Hitos (fase 2), entrada en estado:**
- ③ pendiente de citación: 40/39/99/00
- ④ citación: 43
- ⑦ dictamen: 47
- ⑧ comisión: 50
- ⑨ resolución del grado: 90/34/36

⑦ a ⑨ están por confirmar.

**Carga del trabajador (Grabación)**, % frente a la media del equipo; Estado con > 115 / < 70:
```
COUNT(DISTINCT "o_custom_SolicitudDependencia"."ID") * 100.0 / (GLOBAL(COUNT(DISTINCT "o_custom_SolicitudDependencia"."ID")) * 1.0 / GLOBAL(COUNT(DISTINCT "o_custom_SolicitudDependencia"."UsuarioAlta")))
```
En Subsanación, lo mismo con `COUNT(DISTINCT CASE WHEN "el__EventosDependencia"."CodigoEstado" IN ('60','30','25') THEN BIND("el__EventosDependencia", "o_custom_SolicitudDependencia"."ID") END)` y el divisor de usuarios con el mismo `CASE` sobre `"el__EventosDependencia"."Usuario"`.

**ESTA FASE · fase 2:**
- Personas: `COUNT(DISTINCT CASE WHEN "el__EventosDependencia"."Fase" IN ('2a · Citación','2b · Valoración') THEN "el__EventosDependencia"."Usuario" END)`
- Tiempo E2E: `AVG(DAYS_BETWEEN("o_custom_SolicitudDependencia"."FechaAlta", PU_MIN("o_custom_SolicitudDependencia", "el__EventosDependencia"."TIMESTAMP", "el__EventosDependencia"."CodigoEstado" IN ('90','34','36'))))`; vs objetivo, lo mismo `- ${objetivo_f2}`.
- Entran/sem (últimas 4 semanas sobre el último dato):
```
COUNT(CASE WHEN "o_custom_SolicitudDependencia"."FechaAlta" > ADD_DAYS(PU_MAX(CONSTANT(), "o_custom_SolicitudDependencia"."FechaAlta"), -28) AND "o_custom_SolicitudDependencia"."FechaAlta" <= PU_MAX(CONSTANT(), "o_custom_SolicitudDependencia"."FechaAlta") THEN "o_custom_SolicitudDependencia"."ID" END) / 4.0
```
- Resuelven/sem: igual, cambiando `FechaAlta` por el `PU_MIN(…)` de los estados 90/34/36.
- Previsión: `CASE WHEN E > R * 1.1 THEN 'Alta' WHEN E < R * 0.9 THEN 'Baja' WHEN E IS NULL THEN NULL ELSE 'Media' END` (E = Entran, R = Resuelven, escritos enteros).

**Gráfico y KPIs de plazo de la fase 2** (estado 47): en plazo `DAYS_BETWEEN(FechaAlta, PU_MIN(… IN ('47'))) <= ${objetivo_f2}`, fuera `> ${objetivo_f2}`, línea de objetivo `AVG(CASE WHEN PU_MIN(… IN ('47')) IS NOT NULL THEN ${objetivo_f2} * 1.0 END)`. Lo mismo en los KPIs «Valorados en plazo / fuera de plazo».

### PQL del 27/11 (todos guardados en la View)

Cada PQL lleva en la View un comentario `/* */` que explica qué mide y qué falta. Aquí, el código.

**Cumplimiento SLA global / Fuera de plazo (cabecera):**
```
COUNT(CASE WHEN DAYS_BETWEEN(S."FechaSolicitud", PU_MIN(S, EL."TIMESTAMP", EL."CodigoEstado" IN ('90','34','36'))) <= ${objetivo_f3} THEN S."ID" END) * 100.0
/ COUNT(CASE WHEN DAYS_BETWEEN(S."FechaSolicitud", PU_MIN(S, EL."TIMESTAMP", EL."CodigoEstado" IN ('90','34','36'))) IS NOT NULL THEN S."ID" END)
```
Fuera de plazo: lo mismo con `> ${objetivo_f3}`.

**Plazo proceso completo (cabecera):** la suma de los tres Tiempo E2E (fase 1 + fase 2 + fase 3, abajo):
```
AVG(DAYS_BETWEEN(S."FechaSolicitud", S."FechaAlta"))
+ AVG(DAYS_BETWEEN(S."FechaAlta", PU_MIN(S, EL."TIMESTAMP", EL."CodigoEstado" IN ('90','34','36'))))
+ AVG(DAYS_BETWEEN(
    PU_MIN(S, EL."TIMESTAMP", EL."ACTIVITY" = 'e_custom_CambioEstadoPIA'),
    PU_MIN(S, EL."TIMESTAMP", EL."ACTIVITY" = 'e_custom_ResolucionPIA')))
```

**Territorio (filtro común):**
```
CASE
  WHEN "o_custom_SolicitudDependencia"."Municipio" IS NULL THEN 'Sin municipio'
  ELSE "o_custom_SolicitudDependencia"."Municipio"
END
```

**Edad (filtro común)**: edad al solicitar, años cumplidos. `E` = `FLOOR(YEARS_BETWEEN(S."FechaNacimiento", S."FechaSolicitud"))`, escrito entero en cada línea:
```
CASE
  WHEN S."FechaNacimiento" IS NULL OR S."FechaSolicitud" IS NULL THEN 'Sin dato de edad'
  WHEN E < 3 THEN 'Menores de 3 años (EVE)'
  WHEN E <= 6 THEN 'De 3 a 6 años'
  WHEN E <= 10 THEN 'De 7 a 10 años'
  WHEN E <= 17 THEN 'De 11 a 17 años'
  WHEN E <= 89 THEN 'De 18 a 89 años'
  ELSE '90 años y más'
END
```

**Origen (fase 1):**
```
CASE
  WHEN S."Origen" IS NULL THEN 'Sin dato'
  WHEN UPPER(S."Origen") = 'INTERNET' THEN 'Telemática'
  WHEN UPPER(S."Origen") = 'ORVE' THEN 'ORBE / presencial'
  ELSE S."Origen"
END
```

**Resolución de grado (fase 2)**: `T` = `S."TipoResolucionGrado"`, `G` = `S."CodigoGrado"`. El orden importa: «Desestimatoria grado 0» también dice «desestimatoria», por eso Grado 0 va antes.
```
CASE
  WHEN T IS NULL THEN 'Sin resolución de grado'
  WHEN UPPER(T) LIKE '%DESISTIMIENTO%' THEN 'Desistimiento'
  WHEN UPPER(T) LIKE '%CADUCIDAD%' THEN 'Caducidad'
  WHEN UPPER(T) LIKE '%GRADO 0%' OR G = '0' THEN 'Grado 0'
  WHEN UPPER(T) LIKE '%DESESTIMATORIA%' OR UPPER(T) LIKE '%DENEGATORIA%' THEN 'Denegatoria'
  WHEN G IN ('1', '2', '3') THEN 'Grado I-III con PIA'
  ELSE T
END
```

**Tipo de valoración (fase 2)**: `V` = `"o_custom_ValoracionDependencia"`. La tabla común pasa a ser la de valoraciones.
```
CASE
  WHEN V."TipoBaremo" = 'BVD' AND V."Telematica" = 'S' THEN 'BVD · Telemática'
  WHEN V."TipoBaremo" = 'BVD' THEN 'BVD · Presencial'
  ELSE V."TipoBaremo"
END
|| CASE
  WHEN S."IdSolicitudOriginal" IS NULL THEN ' · Inicial'
  ELSE ' · Revisión'
END
```

**Estado fase 3**: `C` = `"o_custom_PIADependencia"."CodigoEstadoPIA"`, `N` = `"o_custom_PIADependencia"."EstadoPIA"`.
```
CASE
  WHEN C IS NULL THEN 'Sin estado'
  WHEN C IN ('00', '10', '20') THEN 'En propuesta'
  WHEN C IN ('30', '40') THEN 'En resolución'
  WHEN C = '90' THEN 'PIA resuelto'
  ELSE C || ' ' || N
END
```

**Tipo de prestación (fase 3)**: `A` = `"o_custom_PIADependencia"."AgrupacionPrestacion"`. El orden importa: la PEVS «vinculada a atención residencial» es prestación vinculada, no residencia.
```
CASE
  WHEN A IS NULL THEN 'Sin prestación'
  WHEN UPPER(A) LIKE '%VINCULADA%' THEN 'Prest. vinculada'
  WHEN UPPER(A) LIKE '%CUIDADOS%' THEN 'Prest. cuidados'
  WHEN UPPER(A) LIKE '%TELEASISTENCIA%' THEN 'Teleasistencia'
  WHEN UPPER(A) LIKE '%RESIDENCIA%' THEN 'Residencia'
  WHEN UPPER(A) LIKE '%DOMICILIO%' OR UPPER(A) LIKE '%SAD%' THEN 'SAD'
  WHEN UPPER(A) LIKE '%CENTRO DE D%' THEN 'Centro de día'
  ELSE A
END
```

**ESTA FASE · fase 3:**
- Personas involucradas:
```
COUNT(DISTINCT CASE
  WHEN "el__EventosDependencia"."ACTIVITY" = 'e_custom_CambioEstadoPIA' THEN "el__EventosDependencia"."Usuario"
END)
```
- Tiempo E2E (vs objetivo: lo mismo `- ${objetivo_f3}`):
```
AVG(DAYS_BETWEEN(
  PU_MIN("o_custom_SolicitudDependencia", "el__EventosDependencia"."TIMESTAMP", "el__EventosDependencia"."ACTIVITY" = 'e_custom_CambioEstadoPIA'),
  PU_MIN("o_custom_SolicitudDependencia", "el__EventosDependencia"."TIMESTAMP", "el__EventosDependencia"."ACTIVITY" = 'e_custom_ResolucionPIA')
))
```
- Resuelven/sem: `CORTE` = `PU_MAX(CONSTANT(), S."FechaAlta")`, `P` = el `PU_MIN(…)` de `'e_custom_ResolucionPIA'`, escritos enteros:
```
COUNT(CASE WHEN P > ADD_DAYS(CORTE, -28) AND P <= CORTE THEN S."ID" END) / 4.0
```
- Entran/sem: igual, con el `PU_MIN(…)` de los estados 90/34/36 (grados resueltos, lo que entra en PIA).
- Previsión carga: el mismo `CASE` de la fase 2 (±10 %), con los Entran y Resuelven de esta fase.

### PQL del 27/11 (noche): cabecera y fases 1, 2 y 3 (todos guardados en la View)

En la View cada PQL va **escrito entero**, sin abreviaturas, con su comentario `/* */`. Aquí se usan nombres cortos para que se lea mejor. Abreviaturas de tablas, además de S y EL:
- V = `"o_custom_ValoracionDependencia"`
- VD = `"o_custom_ValoradorDependencia"`
- P = `"o_custom_PIADependencia"`

Un nombre en MAYÚSCULAS (RPIA, SUBN…) es un trozo de PQL que se pega entero donde aparece. Si va en una suma o en una comparación, se pega entre paréntesis.

#### Cabecera y «% del equipo total»

```
P1 = COUNT(DISTINCT S."UsuarioAlta")
P2 = COUNT(DISTINCT CASE WHEN EL."Fase" IN ('2a · Citación', '2b · Valoración') THEN EL."Usuario" END)
P3 = COUNT(DISTINCT CASE WHEN EL."ACTIVITY" = 'e_custom_CambioEstadoPIA' THEN EL."Usuario" END)
```
- `personas_total` = `(P1 + P2 + P3)`, con la unidad « personas». La misma persona en dos fases cuenta dos veces.
- `pct_equipo_f1` = `P1 * 100.0 / (P1 + P2 + P3)`, con la unidad « %» y el formato Rounded. Lo mismo con P2 y P3 para `pct_equipo_f2` y `pct_equipo_f3`.
- El texto de cada fase es «% del equipo total · de {personas_total}», y la cifra va en Heading 2.
- **Actualizado** (`fecha_corte`), en un Text box:
```
TO_STRING(PU_MAX(CONSTANT(), "el__EventosDependencia"."TIMESTAMP"), FORMAT('%d/%m/%Y %H:%M'))
```

#### Fase 1 · Subsanación

```
EVN   = PU_COUNT(S, EL."TIMESTAMP", EL."ACTIVITY" = 'e_custom_SubsanacionRequerida')
SUBN  = (EVN + PU_COUNT(S, EL."TIMESTAMP", EL."CodigoEstado" IN ('60','30','25')))
D1    = DAYS_BETWEEN(S."FechaSolicitud", S."FechaAlta")
START = PU_MIN(S, EL."TIMESTAMP", EL."ACTIVITY" = 'e_custom_SubsanacionRequerida' OR EL."CodigoEstado" IN ('60','30','25'))
END   = PU_MIN(S, EL."TIMESTAMP", EL."TIMESTAMP" > START AND EL."CodigoEstado" IS NOT NULL AND EL."CodigoEstado" NOT IN ('60','30','25'))
```
- Tasa subsanación: `AVG(CASE WHEN SUBN > 0 THEN 100.0 ELSE 0.0 END)`.
- Número de subsanaciones: `COUNT(CASE WHEN SUBN > 0 THEN S."ID" END)`.

**Tabla «Subsanación · por motivo»:**

| Columna | PQL |
|---|---|
| Motivo (código) | `CASE WHEN SUBN = 0 THEN '0 · sin subsanación (referencia)' WHEN EVN = 0 THEN 'Sin requerimiento (solo estado)' ELSE CONCAT('Código ', PU_FIRST(S, EL."CodigoEstadoDocumentacion", EL."ACTIVITY" = 'e_custom_SubsanacionRequerida')) END` |
| Exp. | `COUNT(DISTINCT S."ID")` |
| % | `COUNT(DISTINCT CASE WHEN SUBN > 0 THEN S."ID" END) * 100.0 / GLOBAL(COUNT(DISTINCT CASE WHEN SUBN > 0 THEN S."ID" END))` |
| Plazo + | `AVG(D1) - GLOBAL(AVG(CASE WHEN SUBN = 0 THEN D1 END))` |

**Tabla «Flujo por atributo»**: usa la variable `atributo_f1` (String, por defecto «Territorio»). EDAD, ORIGEN y TERRITORIO son los mismos `CASE` de los filtros (más arriba).

| Columna | PQL |
|---|---|
| Atributo | `CASE WHEN '${atributo_f1}' = 'Edad' THEN EDAD WHEN '${atributo_f1}' = 'Origen' THEN ORIGEN ELSE TERRITORIO END` |
| Exp. | `COUNT(DISTINCT S."ID")` |
| % sub. | `COUNT(DISTINCT CASE WHEN SUBN > 0 THEN S."ID" END) * 100.0 / COUNT(DISTINCT S."ID")` |
| Plazo + | `AVG(CASE WHEN SUBN > 0 THEN D1 END) - GLOBAL(AVG(CASE WHEN SUBN = 0 THEN D1 END))`, con formato `+,.0f` |
| Días bloq. subs. | `AVG(DAYS_BETWEEN(START, END))` (si aún no hay END, no cuenta) |

#### Fase 2 · Valoración

```
VS     = V."SolicitudDependencia_ID"
VV     = V."ValoradorDependencia_ID"
DICT   = PU_MIN(S, EL."TIMESTAMP", EL."CodigoEstado" = '47')          (dictamen)
CIT    = PU_MIN(S, EL."TIMESTAMP", EL."CodigoEstado" = '43')          (citación)
EXPVAL = PU_COUNT_DISTINCT(DOMAIN_TABLE(VV), VS)                       (expedientes de cada valorador)
MEDIAV = (PU_COUNT_DISTINCT(CONSTANT(), CONCAT(VS, '|', VV)) * 1.0 / PU_COUNT_DISTINCT(CONSTANT(), VV))
B      = GREATEST(COALESCE(V."BaremoFisico", 0.0), COALESCE(V."BaremoCognitivo", 0.0))
ISBVD  = V."TipoBaremo" = 'BVD' AND (V."BaremoFisico" IS NOT NULL OR V."BaremoCognitivo" IS NOT NULL)
```

**Productividad y carga:**
- Total valoradores: `COUNT(DISTINCT VV)`.
- Media exp/persona: `COUNT(DISTINCT CONCAT(VS, '|', VV)) * 1.0 / COUNT(DISTINCT VV)`.
- Sobrecargados (>115 %): `COUNT(DISTINCT CASE WHEN EXPVAL * 100.0 / MEDIAV > 115 THEN VV END)`.
- El gráfico «# Valoradores» se hace igual que el de los técnicos PIA (fase 3, más abajo), con EXPVAL y MEDIAV.

**Variabilidad del criterio BVD:**
```
BAND   = CASE WHEN ISBVD THEN (CASE WHEN B >= 75 THEN 'G3' WHEN B >= 50 THEN 'G2' WHEN B >= 25 THEN 'G1' ELSE 'G0' END) END
XG(k)  = CASE WHEN (BAND) IS NOT NULL THEN (CASE WHEN (BAND) = 'Gk' THEN 100.0 ELSE 0.0 END) END
PVG(k) = PU_AVG(DOMAIN_TABLE(VV), XG(k))          (% de Gk del valorador)
PCG(k) = PU_AVG(CONSTANT(), XG(k))                (% de Gk del equipo)
DESVV  = GREATEST(ABS(PVG(0) - PCG(0)), ABS(PVG(1) - PCG(1)), ABS(PVG(2) - PCG(2)), ABS(PVG(3) - PCG(3)))
```
- Valoradores activos (BVD): `COUNT(DISTINCT CASE WHEN ISBVD THEN VV END)`.
- Criterio sesgado (>10 pp): `COUNT(DISTINCT CASE WHEN ISBVD AND DESVV > 10 THEN VV END)`.
- % Alineación: `COUNT(DISTINCT CASE WHEN ISBVD AND DESVV <= 5 THEN VV END) * 100.0 / COUNT(DISTINCT CASE WHEN ISBVD THEN VV END)`.

**Tabla «Distribución de grados BVD por valorador»** (una fila por valorador):
```
AG(k) = AVG(XG(k))                      columnas G0…G3, con la unidad « %»
DG(k) = (AG(k) - GLOBAL(AG(k)))         diferencia con el equipo
DTAB  = GREATEST(ABS DG(0), ABS DG(1), ABS DG(2), ABS DG(3))        columna Desv. (pp)
```
Columna Criterio (en la View, los cuatro `WHEN` van escritos enteros):
```
CASE WHEN DTAB IS NULL THEN 'Sin BVD'
     WHEN DTAB > 10 THEN (CASE WHEN ABS DG(0) = DTAB THEN (CASE WHEN DG(0) > 0 THEN 'Sesgo G0 ↑' ELSE 'Sesgo G0 ↓' END)
                               … lo mismo con G1 y G2 …
                               ELSE (CASE WHEN DG(3) > 0 THEN 'Sesgo G3 ↑' ELSE 'Sesgo G3 ↓' END) END)
     WHEN DTAB > 5 THEN 'Leve'
     ELSE 'Alineado' END
```

**Hitos** (KPIs):
```
H4 = PU_MIN(S, EL."TIMESTAMP", EL."CodigoEstado" IN ('43'))
H5 = PU_MIN(S, V."FechaValoracion")
H6 = PU_MIN(S, V."FechaFinGrabacion")
H7 = PU_MIN(S, EL."TIMESTAMP", EL."CodigoEstado" IN ('47'))
```
- ④ → ⑤: `AVG(DAYS_BETWEEN(H4, H5))`.
- ⑤ → ⑥: `AVG(DAYS_BETWEEN(H5, H6))`.
- ⑥ → ⑦: `AVG(DAYS_BETWEEN(H6, H7))`.

**Detalle por Trabajador — Valoración:**
```
d     = DAYS_BETWEEN(S."FechaAlta", DICT)
cnt   = PU_COUNT(DOMAIN_TABLE(VS, VV), V."ID")      (valoraciones del par expediente–valorador)
PLZ2E = (SUM(d / cnt) / SUM(CASE WHEN d IS NOT NULL THEN 1.0 / cnt END))
PLZ2T = (GLOBAL(SUM(d / cnt)) / GLOBAL(SUM(CASE WHEN d IS NOT NULL THEN 1.0 / cnt END)))
```
`PLZ2E` es la media por expediente: cada expediente cuenta una vez aunque tenga varias valoraciones del mismo valorador. `PLZ2T` es lo mismo para todo el equipo.

| Columna | PQL |
|---|---|
| Trabajador | `VV` |
| Tipo | `CASE WHEN VD."Encomienda" IS NULL OR VD."Encomienda" = '' THEN 'Sin dato' ELSE VD."Encomienda" END` |
| Zona | `CASE WHEN VD."Zona" IS NULL OR VD."Zona" = '' THEN 'Sin dato' ELSE VD."Zona" END` |
| Expedientes | `COUNT(DISTINCT VS)` |
| Carga | `COUNT(DISTINCT VS) * 100.0 / MEDIAV` |
| Plazo medio | `PLZ2E` |
| vs equipo | `CASE WHEN ABS(PLZ2E - PLZ2T) < 0.5 THEN 0.0 ELSE (PLZ2E - PLZ2T) END` |
| Variab. criterio | el mismo `CASE` de la columna Criterio |
| Estado | `CASE WHEN carga > 115 THEN 'Crítico — sobrecarga' WHEN carga < 70 THEN 'Subcarga — reasignar' ELSE 'Óptimo' END` |

**Evaluación individual del valorador** (FV = `V."FechaValoracion"`, FG = `V."FechaFinGrabacion"`):

| Columna | PQL |
|---|---|
| Valoraciones | `COUNT(DISTINCT V."ID")` |
| Cita → visita (no imputable) | `AVG(CASE WHEN CIT <= FV THEN DAYS_BETWEEN(CIT, FV) END)` |
| Días a grabación | `AVG(DAYS_BETWEEN(FV, FG))` |
| Días a dictamen | `AVG(CASE WHEN FG <= DICT THEN DAYS_BETWEEN(FG, DICT) END)` |
| Total imputable (TOTI) | días a grabación + días a dictamen |
| Nivel | `CASE WHEN TOTI IS NULL THEN 'Sin dictamen' WHEN TOTI < 15 THEN 'Óptimo (<15 d)' WHEN TOTI < 26 THEN 'Aceptable (15–25 d)' ELSE 'Crítico (≥26 d)' END` |

#### Fase 3 · Resolución de PIA

```
RPIA = PU_MIN(S, EL."TIMESTAMP", EL."ACTIVITY" = 'e_custom_ResolucionPIA')
CEP  = PU_MIN(S, EL."TIMESTAMP", EL."ACTIVITY" = 'e_custom_CambioEstadoPIA')
D3   = DAYS_BETWEEN(S."FechaSolicitud", RPIA)
CEPC = EL."ACTIVITY" = 'e_custom_CambioEstadoPIA'
MARK = EL."ID" = PU_FIRST(DOMAIN_TABLE(EL."SolicitudDependencia_ID", EL."Usuario"), EL."ID", CEPC, ORDER BY EL."TIMESTAMP" ASC)
```
MARK marca un solo evento por par expediente–técnico. Así, un técnico con varios trámites en el mismo expediente no pesa más en las medias.

**Plazos de tramitación:**

| Componente | PQL |
|---|---|
| PIA resueltos | `COUNT(RPIA)` |
| Resueltos en plazo | `COUNT(CASE WHEN D3 <= ${objetivo_f3} THEN S."ID" END)` |
| Resueltos fuera de plazo | `COUNT(CASE WHEN D3 > ${objetivo_f3} THEN S."ID" END)` |
| Gráfico: dimensión | `ROUND_MONTH(RPIA)` |
| Gráfico: Plazo medio | `AVG(D3)` |
| Gráfico: Objetivo SLA (días) | `AVG(CASE WHEN RPIA IS NOT NULL THEN ${objetivo_f3} * 1.0 END)` |

**Productividad y carga:**
```
TECS    = COUNT(DISTINCT CASE WHEN CEPC THEN EL."Usuario" END)                                       (KPI Técnicos PIA)
PAIRS   = COUNT(DISTINCT CASE WHEN CEPC THEN CONCAT(EL."SolicitudDependencia_ID", '|', EL."Usuario") END)
EXPTEC  = PU_COUNT_DISTINCT(DOMAIN_TABLE(EL."Usuario"), EL."SolicitudDependencia_ID", CEPC)
MEDIAPU = PU_COUNT_DISTINCT(CONSTANT(), CONCAT(EL."SolicitudDependencia_ID", '|', EL."Usuario"), CEPC) * 1.0
          / PU_COUNT_DISTINCT(CONSTANT(), EL."Usuario", CEPC)
R       = EXPTEC * 100.0 / MEDIAPU
```
- Media exp/técnico: `PAIRS * 1.0 / TECS`.
- Sobrecargados (>115 %): `COUNT(DISTINCT CASE WHEN CEPC AND EXPTEC > 1.15 * MEDIAPU THEN EL."Usuario" END)`.
- Gráfico «# Técnicos PIA por tramo de carga». La dimensión es:
```
CASE WHEN CEPC THEN (CASE WHEN R < 70 THEN '1 · Baja (<70 %)' WHEN R <= 115 THEN '2 · Media (70–115 %)'
                          WHEN R <= 130 THEN '3 · Alta (115–130 %)' ELSE '4 · Sobrecarga (>130 %)' END) END
```
  El KPI es `COUNT(DISTINCT EL."Usuario")`.

**Variabilidad de la prestación:** A = `P."AgrupacionPrestacion"`, y TIPO es el `CASE` del filtro Tipo de prestación.
```
PCT(t) = AVG(CASE WHEN A IS NOT NULL THEN (CASE WHEN (TIPO) = 't' THEN 100.0 ELSE 0.0 END) END)
X(t)   = CASE WHEN A IS NOT NULL THEN (CASE WHEN (TIPO) = 't' THEN 100.0 ELSE 0.0 END) END
TR(t)  = PU_AVG(DOMAIN_TABLE(S."Municipio"), X(t))        (% del territorio)
CM(t)  = PU_AVG(CONSTANT(), X(t))                         (% de la Comunidad)
```
- Tabla «Prestación prescrita por territorio»:
  - Territorio: `S."Municipio"`.
  - PIA: `COUNT(CASE WHEN A IS NOT NULL THEN P."ID" END)`.
  - Resid. / SAD / Teleas.: `PCT('Residencia')`, `PCT('SAD')` y `PCT('Teleasistencia')`.
  - Desv. CM: `GREATEST(ABS(PCT_R - GLOBAL(PCT_R)), ABS(PCT_S - GLOBAL(PCT_S)), ABS(PCT_T - GLOBAL(PCT_T)))`.
- Territorios con PIA: `COUNT(DISTINCT CASE WHEN A IS NOT NULL THEN S."Municipio" END)`.
- Territorios atípicos (>10 pp): territorios en los que `ABS(TR(t) - CM(t)) > 10` para alguno de los tres tipos. El umbral 10 está por confirmar.
- Mayor dispersión: `GREATEST(PU_MAX(CONSTANT(), TR(t)) - PU_MIN(CONSTANT(), TR(t)))` para Residencia, SAD y Teleasistencia.

**Detalle por Trabajador — Resolución de PIA.** El filtro del componente deja solo los eventos `CambioEstadoPIA`.
```
MEDIA3 = GLOBAL(COUNT(DISTINCT CONCAT(EL."SolicitudDependencia_ID", '|', EL."Usuario"))) * 1.0 / GLOBAL(COUNT(DISTINCT EL."Usuario"))
PLZ3   = AVG(CASE WHEN MARK THEN DAYS_BETWEEN(CEP, RPIA) END)
RESX   = CASE WHEN PU_COUNT(S, P."ID", UPPER(A) LIKE '%RESIDENCIA%' AND NOT UPPER(A) LIKE '%VINCULADA%') > 0 THEN 100.0 ELSE 0.0 END
PRES   = AVG(CASE WHEN MARK THEN RESX END)
```

| Columna | PQL |
|---|---|
| Técnico PIA | `EL."Usuario"` |
| Expedientes | `COUNT(DISTINCT EL."SolicitudDependencia_ID")` |
| Carga | `COUNT(DISTINCT EL."SolicitudDependencia_ID") * 100.0 / MEDIA3` |
| Plazo medio | `PLZ3` |
| vs equipo | `PLZ3 - GLOBAL(PLZ3)` |
| Territorio principal | `MAX(PU_MODE(DOMAIN_TABLE(EL."Usuario"), BIND(EL, S."Municipio"), CEPC))` |
| Estado | `CASE WHEN carga > 115 THEN 'Crítico — sobrecarga' WHEN carga < 70 THEN 'Subcarga — reasignar' ELSE 'Óptimo' END` |
| Variab. prescrip. | `PRES - GLOBAL(PRES)`, en pp de Residencia; una diferencia de menos de 0,5 se muestra como 0 |

**Evaluación individual del tramitador — Gestión del PIA:**
```
ANTES = ROUND_DAY(EL."TIMESTAMP") <= ROUND_DAY(RPIA)            (trámite anterior o igual a la resolución)
RES3  = MARK AND RPIA IS NOT NULL AND ANTES
INI   = COALESCE(PU_MIN(S, P."FechaConsultaBeneficiario"), EL."TIMESTAMP")
```
- Exp. resueltos: `COUNT(DISTINCT CASE WHEN RPIA IS NOT NULL AND ANTES THEN EL."SolicitudDependencia_ID" END)`.
- Plazo imputable: `AVG(CASE WHEN RES3 THEN DAYS_BETWEEN(ROUND_DAY(INI), ROUND_DAY(RPIA)) END)`.
- vs equipo: el plazo imputable menos su `GLOBAL`.
- % con requerimiento y Llamadas/exp: se calculan solo si el modelo tiene los eventos de requerimiento y de llamada del PIA. Hoy no los tiene.
- Perfil de gestión: «Pendiente de datos» si hay PIA resueltos y «Sin PIA resueltos» si no los hay.

## 7. Ficheros del repositorio

- `dependencia/MEMORIA_DEPENDENCIA_CELONIS.md`: memoria viva del proyecto (tablas, estados y fases, decisiones, SQL, pendientes).
- `dependencia/MAPEO_MOCKUP_CU1.md`: mockup elemento a elemento (✅/🟡/❌) y revisión completa del 05/11 (tooltips, selectores, datos del JS, definiciones del mockup).
- `dependencia/MAPEO_TABLAS_SIDEMA.md` (24/11): las 29 tablas de la extracción, claves de unión, lo que hay además en el origen, los mockups CU1 y CU2 elemento a elemento, qué columnas van en las vistas y preguntas para Roberto.
- `dependencia/sql/VistasSIDMPRODv3.sql` (24/11): script Oracle para Roberto. 29 vistas `SIDM_V_DEP_*` con lista de columnas, 28 catálogos, consulta de columnas del CU2 y comprobación final.
- `dependencia/sql/generador/`: los scripts Python que generan el script de vistas (`gen_vistas_v2.py` tiene las columnas de cada tabla y el motivo de las que quedan fuera; `gen_vistas_v3.py` monta el v3). Se ejecutan con `python gen_vistas_v3.py <ruta del v1> <salida>`.
- `dependencia/sql/01…04_*.sql`: SQL del objeto y de los 3 eventos (Objects & Events).
- `dependencia/sql/05…22_*.sql` (27/11): objeto `SolicitudDependencia` v2 (con `Origen`), los objetos Valoracion, Valorador y PIA, y 14 eventos (el 22, `SubsanacionRequerida`, se añadió en la auditoría de la tarde). Se pegan sin punto y coma, con *Data Source* None (Global).
- `dependencia/celonis/DependenciaView.yaml`: YAML v2 de la View (referencia; ahora se trabaja en el editor visual). Se generaba con un script del scratchpad que ya no existe en sesiones nuevas.
- `dependencia/celonis/logo_comunidad_madrid.png`: logo para el componente Imagen.
- `mockups/MockupCU1_v2.html`: el mockup del CU1.
- `mockups/MockupCU2.html`: el mockup del CU2 (lista de espera de SAD y teleasistencia).

## 8. Lista de datos que faltan (enviada al grupo de Teams «Minería de Procesos - Dependencia», 05/11)

Tablas completas de producción · municipio del expediente y catálogo municipio → mancomunidad, zona y distrito · edad del solicitante (tramo) · canal de entrada (origen) · solicitudes registradas sin grabar (bandeja) · motivo de subsanación · datos de usuarios (nombre, tipo, rol, equipo, sede, territorio) · efectivos por fase · valorador por expediente (con asignación y zona) · tipo de valoración · fechas de visita y de grabación de la valoración · grado propuesto en el dictamen · grado reconocido y tipo de resolución · estados y fechas del PIA (consulta, propuesta, resolución, notificación) · prestación y técnico del PIA · requerimientos y llamadas.

Por confirmar:
- `FCMODI` es la fecha de entrada en el estado, el histórico está completo e `IDMODI` es la persona que hace el cambio.
- Agrupación de los estados en fases; qué son AVC y RA.
- Estados de dictamen, comisión y grado.
- `CDTIPO`.
- Días naturales o hábiles.
- Objetivos internos.
- Revisiones de grado.

## 9. Pendiente fuera de la View

- Error de Snappy en la extracción (Roberto / Javier Olmeda): por eso solo hay muestras. Seguía igual el 20/11; hay una pista sin comprobar en la sección 1 de `MAPEO_TABLAS_SIDEMA.md`.
- Create version y Deploy con Roberto. La perspectiva con los objetos y eventos nuevos ya está en desarrollo (27/11).
- Correo a Roberto con el estado del 27/11: pendiente de redactar.
- Natalidad: correo de convocatoria con [día] [hora] por completar (jueves 5 o 12 de noviembre).
