# Traspaso · Cuadro de mando de Dependencia en Celonis (View)

Documento para que una conversación nueva siga exactamente donde se quedó la anterior (06/11/2026; tablas nuevas, 24/11; modelo nuevo cargado en desarrollo y View ampliada, 27/11). Leer **antes** que nada: `CLAUDE.md`, `dependencia/MEMORIA_DEPENDENCIA_CELONIS.md`, `dependencia/MAPEO_MOCKUP_CU1.md` y `dependencia/MAPEO_TABLAS_SIDEMA.md`.

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

## 4. Cómo está la View ahora (revisada en el navegador el 06/11 y el 27/11, guardada como borrador)

**Auditoría del 27/11:** ya no queda ningún número fijo de objetivo en los PQL, ni `TODAY()` / `NOW()`. Todas las variables que se usan existen. Los 6 desplegables que eran marcadores «(pendiente)» tienen ya PQL real.

**Cabecera (fuera de las pestañas):**
- Logo de la Comunidad de Madrid y texto de la DG.
- Solicitudes activas: sin cambios. Falta que Andrés diga qué estados cierran un expediente.
- **Plazo proceso completo** (27/11) = Tiempo E2E de la fase 1 + el de la fase 2 + el de la fase 3, como dice el mockup («suma E2E fases 1→3»).
- **Cumplimiento SLA global y Fuera de plazo:** de la solicitud al grado resuelto (90/34/36) frente a `${objetivo_f3}`. El 27/11 se quitó el 180 fijo. **Ojo:** si se cambia el objetivo de la fase 3, cambia también el SLA global. Hay que decidir si el SLA global es el plazo legal (`FechaFinPlazo`) o una variable propia.
- Altas / mes y vs mes anterior.

**Título** «Cuadro de Mando de Gestión de Equipo» y **barra de filtros común:**
- Periodo: Date range sobre `"o_custom_SolicitudDependencia"."FechaAlta"`, display name «Periodo».
- **Territorio** (27/11): municipio del solicitante. La mancomunidad del mockup necesita el catálogo municipio → mancomunidad.
- **Edad** (27/11): edad al presentar la solicitud, en los tramos del mockup. El mockup tiene «Mayores de 18» y «Mayores de 90», que se solapan: aquí son «De 18 a 89 años» y «90 años y más».
- Planeados también: botón **Limpiar** y KPI **Actualizado** (`MAX("el__EventosDependencia"."TIMESTAMP")`).

**Contenedor con 3 pestañas:**
- **Fase 1 · Grabación de solicitudes:**
  - Filtros propios: Estado (4 grupos), Objetivo (Input box → `objetivo_dias`) y **Origen** (27/11), el canal de la bandeja: Internet → «Telemática», ORVE → «ORBE / presencial». En la muestra todo sale «Sin dato» porque la bandeja cargada no cruza con las solicitudes grabadas.
  - **Pendientes de grabar** (27/11): entradas de la bandeja sin solicitud grabada (`"e_custom_RecepcionBandeja"`). Antes era una aproximación con las fechas de la solicitud.
  - «ESTA FASE»: Personas involucradas, Tiempo E2E, vs objetivo, % del equipo total (pendiente), Previsión carga, Entran/sem, Resuelven/sem.
  - Plazos de tramitación (KPIs y gráfico dentro/fuera de plazo con Plazo medio y Objetivo SLA): leen `${objetivo_dias}`.
  - Subsanaciones y AVC (KPIs por los estados del histórico; la muestra coherente del 27/11 ya trae el histórico de las mismas solicitudes).
  - **Tabla «AVC · Reproceso en bucle»** (antes gráfico): Nº de vueltas AVC (0 / 1 / 2 / 3+, `PU_COUNT` de los estados 05/20/15) · Exp. · % · Plazo +. Ordenada por nº de vueltas.
  - Textos «pendiente de datos»: Subsanación por motivo y Flujo por atributo. Para la primera ya está el evento `SubsanacionRequerida`, pero sin el catálogo de motivos (bloque 2 del script) solo saldrían códigos.
  - **Detalle por Trabajador — Equipo de Grabación** (arriba, como en el mockup; antes gráfico): Trabajador (`UsuarioAlta`) · Expedientes · Carga (% frente a la media del equipo) · Plazo medio · vs equipo · Subsanaciones · Estado (Crítico — sobrecarga > 115 %, Subcarga — reasignar < 70 %, Óptimo). Ordenada por Carga.
  - **Detalle por Trabajador — Equipo de Subsanación** (debajo): Trabajador (`Usuario` del evento) · Exp. subsanados (60/30/25) · Subsanaciones/día · AVC en bucle · Carga · Estado («Sin subsanaciones» si 0). Ordenada por Carga.
- **Fase 2 · Valoración:**
  - Filtros propios (27/11):
    - **Resolución de grado:** tipo de la última resolución de grado y grado del último dictamen, en las opciones del mockup (Grado 0 / Grado I-III con PIA / Desistimiento / Denegatoria / Caducidad). Lo que no está en el mockup sale con su nombre.
    - **Tipo de valoración:** sobre la tabla de valoraciones, con etiqueta combinada (BVD · Presencial o Telemática, o EVE) + (Inicial o Revisión). La EVE no tiene telemática.
  - «ESTA FASE» con PQL propios (ya no es copia de la fase 1): Personas involucradas (usuarios distintos en eventos de fase 2a/2b; aproximación por el usuario que modifica), Tiempo E2E (alta → grado resuelto 90/34/36), vs objetivo (`- ${objetivo_f2}`), Entran/sem y Resuelven/sem (últimas 4 semanas sobre el último dato), Previsión (Alta/Media/Baja ±10 %).
  - Borrados los bloques repetidos (Previsión dentro de Variabilidad BVD, Tiempo E2E dentro de Plazos, texto Personas en Productividad) y subido el contenido para cerrar el hueco. Queda un hueco pequeño encima de «% en plazo / % fuera» (el editor no deja moverlo).
  - Gráfico «Expedientes valorados: dentro vs fuera del plazo objetivo» (por mes de dictamen, estado 47) y KPIs «% en plazo / % fuera»: **con `${objetivo_f2}`** (tenían 120 fijo). El 27/11, lo mismo en los KPIs «Valorados en plazo» y «Valorados fuera de plazo», que aún tenían el 120.
  - Hitos ① a ⑨, ⑤ Fecha de valoración y «Detalle por Trabajador — Valoración» como textos «pendiente de datos». Ya hay datos para montarlos (sección 5).
- **Fase 3 · Resolución de PIA:**
  - Filtros propios (27/11):
    - **Estado fase 3:** estado actual de cada PIA, agrupado: En propuesta (00-20), En resolución (30-40) y PIA resuelto (90). Los demás códigos salen con código y nombre.
    - **Tipo de prestación:** agrupación de la prestación del PIA, con las etiquetas del mockup. SAD y centro de día no salen en la muestra.
  - Los dos van sobre la tabla de PIA: filtran las solicitudes que tienen algún PIA con ese valor (revisiones incluidas).
  - «ESTA FASE» (completa el 27/11):
    - Personas involucradas: técnicos distintos que registran trámites del PIA (`Usuario` de `CambioEstadoPIA`). Es una aproximación: el rol, por confirmar.
    - **Tiempo E2E:** del primer trámite del PIA a la primera resolución del PIA («del primer al último cambio de estado dentro de la fase», como en el mockup).
    - vs objetivo: lo mismo `- ${objetivo_f3}`.
    - Entran/sem: grados resueltos en las últimas 4 semanas / 4.
    - Resuelven/sem: PIA resueltos en las últimas 4 semanas / 4.
    - Previsión carga: Alta / Media / Baja (±10 %).
    - % del equipo total: sigue pendiente (faltan los efectivos de cada unidad).
  - **Por qué el E2E no empieza en la resolución del grado:** en la muestra, grado y PIA se resuelven el mismo día en todas las solicitudes con PIA, y saldría 0. Pregunta a Andrés.
  - Siguen como textos «pendiente» (hacen falta componentes nuevos, sección 5): PIA resueltos / en plazo / fuera, Productividad y carga, Variabilidad de la prestación, Detalle por Trabajador PIA y Evaluación del tramitador.

## 5. Dónde nos quedamos (siguiente paso exacto)

Todo lo anterior está **guardado con Save (borrador)**. No se ha hecho Create version ni Deploy (eso, con Roberto).

**24/11: llegaron las tablas de SIDEMA para el CU1 y el CU2.** Son 29 tablas en la extracción «Extraccion Dependencia» (data job «Dependencia VASOCIAL_SIDM»).
- Mapeo: `dependencia/MAPEO_TABLAS_SIDEMA.md`.
- Script de vistas para Roberto: `dependencia/sql/VistasSIDMPRODv3.sql` (se genera con `dependencia/sql/generador/gen_vistas_v3.py`).
- La extracción **sigue fallando por Snappy** (20/11): en Celonis solo están las muestras de siempre.
- Las secciones 5 y 6 del mapeo dicen qué elementos de los mockups CU1 y CU2 se podrán montar con las tablas nuevas.
- Las tablas del CU2 y de citación existen en SIDEMA, pero el usuario de Celonis no puede leerlas: el bloque 3 del script pide a Roberto sus columnas para hacer la v4.

**27/11: modelo de las tablas nuevas montado en Objects & Events.** Muestra coherente de 2025 cargada en el Global de validación, con el histórico de las mismas solicitudes. 4 objetos y 14 eventos nuevos, todos «Passed». SQL en `dependencia/sql/05…22`; detalle en la sección 9g de la memoria.

**27/11 (tarde): *Test changes* hecho** con el OK de Roberto. La perspectiva con los 4 objetos y los 17 eventos está cargada en desarrollo y la View ya lee las tablas nuevas. Después se auditó la View y se montaron los filtros que faltaban y la «ESTA FASE» de la fase 3 (sección 4). Todo guardado con Save; **sin Create version ni Deploy**.

Pendiente, en este orden:
0. **Roberto** revisa el script v3, ejecuta el bloque 3 y contesta las preguntas (sección 8 del mapeo).
   - Cuando estén las vistas en PROD y funcione la extracción, se apunta la extracción a `SIDM_V_DEP_*` con «Rename target table», para no cambiar los nombres de las tablas.
   - Pasarle el catálogo de motivos de subsanación (bloque 2).
1. **Fase 3:** sustituir los textos «pendiente» por componentes reales.
   - Primero, «PIA resueltos / en plazo / fuera»: KPIs y gráfico por mes de `ResolucionPIA`, con `${objetivo_f3}`.
   - Después, Productividad y carga, y Detalle por Trabajador PIA (`Usuario` de `CambioEstadoPIA`).
   - Variabilidad de la prestación y Evaluación del tramitador, al final.
2. **Fase 2:**
   - «Detalle por Trabajador — Valoración» con `"o_custom_ValoradorDependencia"`.
   - Hitos con los eventos `ValoracionRealizada` (⑤), `ValoracionGrabada`, `ComisionValidada` (⑧) y `ResolucionGrado` (⑨).
   - Personas involucradas: cambiar la aproximación por el valorador real.
3. **Fase 1:** Subsanación por motivo con `SubsanacionRequerida`, cuando llegue el catálogo de motivos, y Flujo por atributo.
4. **Preguntas a Andrés** (sección 10 de la memoria):
   - ¿Grado y PIA se resuelven a la vez? ¿El estado 90 del PIA es «expediente resuelto»?
   - ¿Qué estados cierran un expediente? (Solicitudes activas)
   - ¿Dónde va el origen «Presencial»?
5. **SLA global:** hoy usa `${objetivo_f3}`. Decidir con Andrés si debe ser el plazo legal (`FechaFinPlazo`) o una variable propia.
6. **Interactions:** que la cabecera solo escuche los filtros comunes y que los filtros de cada fase no se queden puestos en las otras.
7. Detalles:
   - botón Limpiar y KPI Actualizado;
   - formato del mes del gráfico de la fase 1 (sale MM/AAAA; el mockup usa `%b %Y`);
   - hueco pequeño de «% en plazo» en la fase 2;
   - KPI días bloqueado en subsanación;
   - tabla «Ver por expediente» con los 9 hitos;
   - comprobar que Tipo de valoración permite selección múltiple.
8. Enseñárselo a Roberto y, si le parece bien, Create version.

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
