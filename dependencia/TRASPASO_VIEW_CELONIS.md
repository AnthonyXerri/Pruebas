# Traspaso · Cuadro de mando de Dependencia en Celonis (View)

Documento para que una conversación nueva siga exactamente donde se quedó la anterior (06/11/2026). Leer **antes** que nada: `CLAUDE.md`, `dependencia/MEMORIA_DEPENDENCIA_CELONIS.md` y `dependencia/MAPEO_MOCKUP_CU1.md`.

**Regla de oro:** datos de la Comunidad de Madrid, nunca a GitHub ni a nada público (artifacts incluidos). Ni logins, ni IDs de solicitud reales, ni filas. Los ficheros con datos van solo al scratchpad. En el repositorio, solo SQL, PQL, estructura y decisiones.

## 1. Qué estamos haciendo

Anthony (Madrid Digital, primera vez con Celonis) está montando en **Celonis Studio** la View **«Dependencia View»** para que se parezca lo máximo posible al mockup `mockups/MockupCU1_v2.html` (Cuadro de Mando de Gestión de Equipo · CU1), con los datos de las **3 tablas** de SIDEMA que hay: `SIDM_SOLICITUD`, `SIDM_HIST_ESTADO`, `SIDM_ESTADO_SOLICITUD`.

- Ruta: **Studio > Implementación > Dependencia** → «Dependencia View» y el Knowledge Model `dm_test_perspective_custom_dependencia-km` (vacío; no se toca sin Roberto).
- **Ahora lo hace desde el editor visual, NO por YAML** (lo pidió él). Le guío **paso a paso**: qué hacemos, por qué, cómo, qué debería ver. Un paso cada vez; él manda capturas.
- **No puedo controlar su navegador** desde la sesión en la nube (lo preguntó dos veces). Si quisiera, haría falta Claude in Chrome o uso del ordenador en local, y consultarlo antes con Roberto/seguridad (es el Celonis del cliente).
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

## 4. Cómo está la View ahora (según sus capturas del 05–06/11)

**Cabecera (fuera de las pestañas):** logo de la Comunidad de Madrid + texto de la DG · Solicitudes activas (199) · Plazo proceso completo («–») · Cumplimiento SLA global y Fuera de plazo («–») · Altas / mes (29, media del periodo) y vs mes anterior. Los «–» necesitan el histórico (fecha de resolución del grado).

**Título** «Cuadro de Mando de Gestión de Equipo» y **barra de filtros común:** Periodo (Date range sobre `"o_custom_SolicitudDependencia"."FechaAlta"`, display name «Periodo») · Territorio · Edad (marcadores «Pendiente de datos»). Planeados también: botón **Limpiar** y KPI **Actualizado** (`MAX("el__EventosDependencia"."TIMESTAMP")`).

**Contenedor con 3 pestañas:**
- **Fase 1 · Grabación de solicitudes:**
  - Filtros propios: Estado (4 grupos), Origen (marcador), Objetivo (Input box → `objetivo_dias`).
  - «ESTA FASE»: Personas involucradas (6), Tiempo E2E (77 d), vs objetivo, % del equipo total (pendiente), Previsión carga (Baja), Entran/sem, Resuelven/sem.
  - Plazos de tramitación: Solicitudes grabadas 200 · en plazo 97 · fuera 103 · Pendientes de grabar 0. **Ya leen `${objetivo_dias}`.**
  - Gráfico «↑ Solicitudes grabadas: dentro vs fuera del plazo objetivo» (columnas apiladas + líneas Plazo medio y Objetivo SLA, objetivo con `${objetivo_dias}`).
  - Subsanaciones y AVC: Tasa, Número, En bucle, Iteraciones (a 0 hasta cargar el histórico).
  - Gráfico AVC · Reproceso en bucle (pendiente de pasar a tabla), textos «pendiente de datos» de Subsanación por motivo y Flujo por atributo.
  - Detalle por Trabajador — Equipo de Subsanación (da «There's data missing»: no hay histórico) y Equipo de Grabación (gráfico; pendiente de pasar a tabla).
- **Fase 2 · Valoración:** filtros Estado (8 estados, PQL abajo), Tipo de valoración y Resolución de grado (marcadores), Objetivo (`objetivo_f2`, planeado). Contenido del YAML v2 (KPIs de plazos por dictamen, hitos ① a ⑨, pendientes).
- **Fase 3 · Resolución de PIA:** filtros Estado y Tipo de prestación (marcadores), Objetivo (`objetivo_f3`, planeado). Todo «Pendiente de datos».

## 5. Dónde nos quedamos (siguiente paso exacto)

Estábamos **dejando perfecto el gráfico de plazos de la fase 1**. Sus Settings tienen: Dimensions (Mes de grabación), Metrics (Grabadas en plazo, Grabadas fuera de plazo, Plazo medio (días), Objetivo SLA 30d), Tooltips, Annotation lines, Data Settings, Alternative display options, Interactions, Axis settings, Coloring, Style. Pasos pendientes de ese gráfico:
1. Renombrar la serie «Objetivo SLA 30d» → «Objetivo SLA» (y el KPI «vs objetivo 30d» → «vs objetivo»).
2. Rojo (fuera de plazo) **encima** de la barra, como en el mockup: cambiar el orden de las métricas y comprobar.
3. Axis settings: eje izquierdo «Solicitudes grabadas», derecho «Plazo (días)»; las dos líneas en el eje derecho.
4. Coloring: en plazo azul o gris oscuro (#464C6A), fuera de plazo rojo, plazo medio negro o azul muy oscuro, objetivo rojo.
5. Style: puntos en Plazo medio, objetivo discontinuo si existe.
6. Formato del mes (`%b %Y`).
7. Tooltip «% fuera de plazo» (PQL abajo).
8. Subtítulo en un Text box: «El reparto se calcula comparando la fecha de solicitud con la fecha de grabación, no por el estado actual del expediente.»

**Después, en este orden:**
1. Tabla «AVC · Reproceso en bucle» (PQL abajo) y borrar el gráfico.
2. Tablas «Detalle por Trabajador — Equipo de Grabación» (Trabajador `UsuarioAlta`, Expedientes, Carga % frente a la media, Plazo medio, vs equipo, Subsanaciones, Estado: crítico > 115 %, subcarga < 70 %) y «Equipo de Subsanación» (usuario del evento en estados 60/30/25 y 05/20/15).
3. KPI días bloqueado en subsanación.
4. **Interactions:** que la cabecera solo escuche los filtros comunes y que los filtros de cada fase no se queden puestos en las otras.
5. Fases 2 y 3: barras de filtros (variables `objetivo_f2`, `objetivo_f3`), revisar KPIs y gráficos, tabla «Ver por expediente» con los 9 hitos. Visto el 06/11: los Input box de objetivo ya están (120 y 180), pero **el bloque «ESTA FASE» de las fases 2 y 3 es una copia del de la fase 1** (6 personas, 77 d, +47 d, Baja, 3 y 6): hay que cambiar sus PQL o dejarlos como «pendiente de datos». En la fase 2 hay además un hueco grande en blanco, un bloque «Previsión carga» repetido dentro de «Variabilidad de criterio BVD» y textos cortados en los hitos.
6. **Cargar el histórico de las mismas 100 solicitudes de 2025** (lo que enciende subsanación, AVC, citación, dictamen, grado, plazo total y SLA): en «Pruebas Anthony», tabla `SIDM_HIST_ESTADO`, filtro `IDSOLICITUD IN (…)` por **lotes de 10** (el Preview solo trae 100 filas; si un lote devuelve justo 100, partirlo). Anthony tiene el fichero de lotes (se le envió el 05/11; los IDs **no** están en el repo). Me pega el Preview → genero `INSERT INTO "SIDM_HIST_ESTADO"` en el scratchpad → él lo ejecuta como hizo con `SIDM_SOLICITUD` → recargar.

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
