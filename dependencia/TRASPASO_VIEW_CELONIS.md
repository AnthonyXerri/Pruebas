# Traspaso · Cuadro de mando de Dependencia en Celonis (View)

Documento para que una conversación nueva siga exactamente donde se quedó la anterior (06/11/2026). Leer **antes** que nada: `CLAUDE.md`, `dependencia/MEMORIA_DEPENDENCIA_CELONIS.md` y `dependencia/MAPEO_MOCKUP_CU1.md`.

**Regla de oro:** datos de la Comunidad de Madrid, nunca a GitHub ni a nada público (artifacts incluidos). Ni logins, ni IDs de solicitud reales, ni filas. Los ficheros con datos van solo al scratchpad. En el repositorio, solo SQL, PQL, estructura y decisiones.

## 1. Qué estamos haciendo

Anthony (Madrid Digital, primera vez con Celonis) está montando en **Celonis Studio** la View **«Dependencia View»** para que se parezca lo máximo posible al mockup `mockups/MockupCU1_v2.html` (Cuadro de Mando de Gestión de Equipo · CU1), con los datos de las **3 tablas** de SIDEMA que hay: `SIDM_SOLICITUD`, `SIDM_HIST_ESTADO`, `SIDM_ESTADO_SOLICITUD`.

- Ruta: **Studio > Implementación > Dependencia** → «Dependencia View» y el Knowledge Model `dm_test_perspective_custom_dependencia-km` (vacío; no se toca sin Roberto).
- **Ahora lo hace desde el editor visual, NO por YAML** (lo pidió él). Le guío **paso a paso**: qué hacemos, por qué, cómo, qué debería ver. Un paso cada vez; él manda capturas.
- Desde la sesión en la nube no se puede controlar su navegador. **El 06/11 se trabajó en local con Claude in Chrome** (Anthony lo pidió): solo editor visual y lectura del DOM; leer la View por API lo bloquea el clasificador de permisos.
- Nada de **Create version** ni **Deploy** sin Roberto. En «Pruebas Anthony» (tarea de extracción), salir siempre con **Discard**.

## 2. Modelo de datos en Celonis (lo que funciona en PQL)

- Objeto: **`"o_custom_SolicitudDependencia"`** con atributos `ID`, `NumeroSolicitud`, `FechaSolicitud`, `FechaRegistroEntrada`, `FechaAlta`, `FechaFinPlazo`, `FechaBaja`, `CodigoEstadoActual`, `EstadoActual`, `TipoSolicitud`, `Urgente`, `Traslado`, `Extinguido`, `NumeroRevision`, `IdSolicitudOriginal`, `UsuarioAlta`, `IdSolicitante`.
- Eventos: **a través del event log `"el__EventosDependencia"`** (perspectiva «Dependencia», event log EventosDependencia, objeto principal SolicitudDependencia, eventos Registro, Alta y CambioEstado). Columnas (comprobadas en el KM el 06/11): `ID`, `ACTIVITY`, `TIMESTAMP`, `CodigoEstado`, `Estado`, `Fase`, `Usuario`, `SolicitudDependencia_ID`, `LEAD_OBJECT_ID`, `epoch`, `_CELONIS_CHANGE_DATE`.
- Las tablas `"e_custom_…"` existen pero **no están conectadas** al objeto (PU_MIN da «tables are not connected»): no usarlas.
- El KM tiene también **`"el_custom_SolicitudDependencia"`** («SolicitudDependencia Event Log»), con las mismas columnas y marcado como **Default**. No se usa: en los PQL, nombrar siempre `"el__EventosDependencia"` de forma explícita.

### Revisión en el navegador (06/11, solo lectura)
- **Objects & Events** (pool «OCPM DataPool VALIDACION y PRODUCCION»): objeto `SolicitudDependencia` con 17 atributos tipados (ID String PK; fechas Datetime; resto String) y etiqueta Dependencia. Eventos relacionados («involves one»): `RegistroEntradaDependencia` (ID, Time), `AltaSolicitudDependencia` (ID, Usuario, Time) y `CambioEstadoDependencia` (ID, CodigoEstado, Estado, Fase, Usuario, Time).
- Perspectiva «Dependencia»: 1 objeto, 1 event log, data model **Successful** (última ejecución 06/11 07:17), enlazada al paquete Dependencia (Draft) como `test:perspective_custom_Dependencia`.
- **Ojo:** en la lista de transformaciones, `SolicitudDependencia` y `CambioEstadoDependencia` se ejecutaron el 06/11 a las 07:15, pero `RegistroEntradaDependencia` y `AltaSolicitudDependencia` salen **«Not executed»**. La View sigue mostrando eventos. Comprobar con un recuento por `ACTIVITY` y, si faltan, preguntar a Roberto.
- Studio: 3 cambios sin versionar (contador de Create version). No se ha tocado.
- Datos cargados (entorno de pruebas): **200 solicitudes** (100 de 2007 y 100 del 1.er semestre de 2025, metidas con INSERT por Anthony), **399 eventos** (registro + alta; una solicitud sin fecha de registro), **0 cambios de estado** porque el histórico local es de otras solicitudes. Por eso subsanación, AVC, citación, dictamen y grado salen a 0 o «–».

## 3. Lecciones de PQL en esta View (importante)

- **`CASE` solo en forma completa:** `CASE WHEN cond THEN … END`. La forma corta `CASE campo WHEN valor` da «Syntax error near RIGHT».
- **Variables de la View:** `${nombre_variable}`. Si el nombre no coincide con una variable existente, Celonis no la sustituye y da «Syntax error near [$]». La variable del objetivo de la fase 1 se llama **`objetivo_dias`** (VIEW, tipo número, por defecto 30). Planeadas: `objetivo_f2` (120) y `objetivo_f3` (180).
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

### Trucos del editor (Studio)
- Abrir el PQL de cada KPI: pinchar el componente y luego el chip del KPI en Settings. El botón `</>` del panel abre el editor de todo el componente (en gráficos y tablas, pinchando la cabecera de cada columna del Preview se cambia de métrica).
- **Done no cierra** si el Preview dice «Data requirements … not met»: antes, Ctrl+Enter para ejecutar.
- Mover componentes: arrastrar el asa «Move Component» (arriba a la izquierda del componente seleccionado). Se puede soltar encima de otro; algunos huecos el editor no los acepta.
- Reordenar columnas con teclado: foco en el chip, Espacio, flechas **de una en una**, Espacio.
- Guardar con **Save** (borrador). Cancelar un editor con cambios pide «Close Editor» y descarta todo lo del editor.

## 4. Cómo está la View ahora (revisada en el navegador el 06/11, guardada como borrador)

**Cabecera (fuera de las pestañas):** logo de la Comunidad de Madrid + texto de la DG · Solicitudes activas (199) · Plazo proceso completo («–») · Cumplimiento SLA global y Fuera de plazo («–») · Altas / mes (29, media del periodo) y vs mes anterior. Los «–» necesitan el histórico (fecha de resolución del grado).

**Título** «Cuadro de Mando de Gestión de Equipo» y **barra de filtros común:** Periodo (Date range sobre `"o_custom_SolicitudDependencia"."FechaAlta"`, display name «Periodo») · Territorio · Edad (marcadores «Pendiente de datos»). Planeados también: botón **Limpiar** y KPI **Actualizado** (`MAX("el__EventosDependencia"."TIMESTAMP")`).

**Contenedor con 3 pestañas:**
- **Fase 1 · Grabación de solicitudes** (completa con los datos actuales):
  - Filtros propios: Estado (4 grupos), Origen (marcador), Objetivo (Input box → `objetivo_dias`).
  - «ESTA FASE»: Personas involucradas, Tiempo E2E, vs objetivo, % del equipo total (pendiente), Previsión carga, Entran/sem, Resuelven/sem.
  - Plazos de tramitación (KPIs y gráfico dentro/fuera de plazo con Plazo medio y Objetivo SLA): leen `${objetivo_dias}`.
  - Subsanaciones y AVC (KPIs a 0 hasta cargar el histórico).
  - **Tabla «AVC · Reproceso en bucle»** (antes gráfico): Nº de vueltas AVC (0 / 1 / 2 / 3+, `PU_COUNT` de los estados 05/20/15) · Exp. · % · Plazo +. Ordenada por nº de vueltas.
  - Textos «pendiente de datos»: Subsanación por motivo y Flujo por atributo.
  - **Detalle por Trabajador — Equipo de Grabación** (arriba, como en el mockup; antes gráfico): Trabajador (`UsuarioAlta`) · Expedientes · Carga (% frente a la media del equipo) · Plazo medio · vs equipo · Subsanaciones · Estado (Crítico — sobrecarga > 115 %, Subcarga — reasignar < 70 %, Óptimo). Ordenada por Carga.
  - **Detalle por Trabajador — Equipo de Subsanación** (debajo): Trabajador (`Usuario` del evento) · Exp. subsanados (60/30/25) · Subsanaciones/día · AVC en bucle · Carga · Estado («Sin subsanaciones» si 0). Ordenada por Carga. **Hoy sale vacía**: no hay cambios de estado en los datos de prueba.
- **Fase 2 · Valoración:**
  - «ESTA FASE» con PQL propios (ya no es copia de la fase 1): Personas involucradas (usuarios distintos en eventos de fase 2a/2b; aproximación por el usuario que modifica), Tiempo E2E (alta → grado resuelto 90/34/36), vs objetivo (`- ${objetivo_f2}`), Entran/sem y Resuelven/sem (últimas 4 semanas sobre el último dato), Previsión (Alta/Media/Baja ±10 %).
  - Borrados los bloques repetidos (Previsión dentro de Variabilidad BVD, Tiempo E2E dentro de Plazos, texto Personas en Productividad) y subido el contenido para cerrar el hueco. Queda un hueco pequeño encima de «% en plazo / % fuera» (el editor no deja moverlo).
  - Gráfico «Expedientes valorados: dentro vs fuera del plazo objetivo» (por mes de dictamen, estado 47) y KPIs «% en plazo / % fuera»: **ahora con `${objetivo_f2}`** (tenían 120 fijo). Salen «There's data missing» o «–» hasta que haya histórico.
  - Hitos ① a ⑨, ⑤ Fecha de valoración y «Detalle por Trabajador — Valoración» como textos «pendiente de datos».
- **Fase 3 · Resolución de PIA:**
  - «ESTA FASE»: Entran/sem = grados resueltos en las últimas 4 semanas / 4 (lo que entra en PIA). El resto, marcadores con comentario `/* Pendiente de datos: … */` que dan «–» (login del técnico PIA, fecha de resolución de PIA…); vs objetivo ya con `${objetivo_f3}`.
  - Contenido subido para cerrar el hueco grande.

## 5. Dónde nos quedamos (siguiente paso exacto)

Todo lo anterior está **guardado con Save (borrador)**. No se ha hecho Create version ni Deploy (eso, con Roberto).

Pendiente, en este orden:
1. **Cargar el histórico de las mismas 100 solicitudes de 2025** (enciende subsanación, AVC, citación, dictamen, grado, plazo total, SLA y la tabla de Subsanación): en «Pruebas Anthony», tabla `SIDM_HIST_ESTADO`, filtro `IDSOLICITUD IN (…)` por **lotes de 10** (el Preview solo trae 100 filas; si un lote devuelve justo 100, partirlo). Anthony tiene el fichero de lotes (los IDs **no** están en el repo). Me pega el Preview → genero `INSERT INTO "SIDM_HIST_ESTADO"` en el scratchpad → él lo ejecuta → recargar. Después, revisar que los «–» y los «There's data missing» se llenan.
2. Con los datos nuevos que pidió el grupo (sección 8), cambiar los marcadores de las fases 2 y 3 (buscar el comentario `/* Pendiente de datos */` en cada PQL).
3. Fase 2 · Personas involucradas: cambiar la aproximación por el valorador real cuando llegue.
4. **Interactions:** que la cabecera solo escuche los filtros comunes y que los filtros de cada fase no se queden puestos en las otras.
5. Detalles: botón Limpiar, KPI Actualizado, formato del mes del gráfico de la fase 1 (sale MM/AAAA; mockup `%b %Y`), hueco pequeño de «% en plazo» en la fase 2, KPI días bloqueado en subsanación, tabla «Ver por expediente» con los 9 hitos.
6. Enseñárselo a Roberto y, si le parece bien, Create version.

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

**Pendientes de grabar (aproximación):** registradas sin alta y sin baja:
```
COUNT(CASE WHEN "o_custom_SolicitudDependencia"."FechaRegistroEntrada" IS NOT NULL AND "o_custom_SolicitudDependencia"."FechaAlta" IS NULL AND "o_custom_SolicitudDependencia"."FechaBaja" IS NULL THEN "o_custom_SolicitudDependencia"."ID" END)
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

**Gráfico y KPIs de plazo de la fase 2** (estado 47): en plazo `DAYS_BETWEEN(FechaAlta, PU_MIN(… IN ('47'))) <= ${objetivo_f2}`, fuera `> ${objetivo_f2}`, línea de objetivo `AVG(CASE WHEN PU_MIN(… IN ('47')) IS NOT NULL THEN ${objetivo_f2} * 1.0 END)`.

## 7. Ficheros del repositorio

- `dependencia/MEMORIA_DEPENDENCIA_CELONIS.md`: memoria viva del proyecto (tablas, estados y fases, decisiones, SQL, pendientes).
- `dependencia/MAPEO_MOCKUP_CU1.md`: mockup elemento a elemento (✅/🟡/❌) y revisión completa del 05/11 (tooltips, selectores, datos del JS, definiciones del mockup).
- `dependencia/sql/01…04_*.sql`: SQL del objeto y de los 3 eventos (Objects & Events).
- `dependencia/celonis/DependenciaView.yaml`: YAML v2 de la View (referencia; ahora se trabaja en el editor visual). Se generaba con un script del scratchpad que ya no existe en sesiones nuevas.
- `dependencia/celonis/logo_comunidad_madrid.png`: logo para el componente Imagen.
- `mockups/MockupCU1_v2.html`: el mockup.

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

- Error de Snappy en la extracción (Roberto / Javier Olmeda): por eso solo hay muestras.
- Create version, Deploy y perspectiva definitiva con Roberto.
- Natalidad: correo de convocatoria con [día] [hora] por completar (jueves 5 o 12 de noviembre).
