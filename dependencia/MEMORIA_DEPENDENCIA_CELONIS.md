# Memoria · Dependencia en Celonis

Documento vivo. Se actualiza cada vez que se aprende o se decide algo. Última actualización: 04/11/2026.

## 1. Cómo trabajar con Anthony

- Es su **primera vez con Celonis**. En cada paso: **qué hacemos, por qué, qué esperamos ver** y qué me tiene que devolver.
- **Un paso cada vez.** No avanzar hasta que el anterior esté claro.
- Explicar el SQL **línea a línea** cuando aparezca algo nuevo (JOIN, CASE, RIGHT, UNION ALL…).
- Él me pasa los resultados pegados o en CSV (botón **Download CSV** del Preview).
- Preguntas para Roberto o Andrés: dárselas redactadas, listas para enviar por Teams.

## 2. Contexto del proyecto

- **Cliente:** Consejería de Familia, Juventud y Asuntos Sociales (Comunidad de Madrid), vía Madrid Digital. Servicio de minería de procesos.
- **Dependencia = DG de Atención al Mayor y a la Dependencia.** Sistema: **SIDEMA** (tablas con prefijo `SIDM_`).
- **Casos de uso** (deck `deck/PainPoints_Dependencia_Discapacidad.pptx`, 29/09):
  - **CU1 · Reconocimiento del grado y PIA:** 1) Grabación (registro, alta, subsanación) · 2) Valoración (citación, visita, dictamen, comisión, resolución del grado) · 3) Resolución del PIA. Objetivos: 30 / 120 / 180 días (180 = plazo legal total).
  - **CU2 · Adjudicación de servicios comunitarios (EELL):** lista de espera → contacto → asignación → alta del servicio. Después del CU1. Sistemas SIDEMA y SAP.
- **Mockup de referencia:** `mockups/MockupCU1_v2.html` («Cuadro de Mando de Gestión de Equipo · CU1», 01/10). El archivo `20261001_MineriaDeProcesos_DependenciaMockup.html` que tiene Anthony es idéntico.
- **Equipo:** Andrés Esteban Zambrana Valle (lidera), Roberto Samir Astudillo Chehab (Celonis; hace PNC con Atlantix y discapacidad), Javi/Javier (natalidad), Javier Olmeda (soporte Celonis, para errores de extracción).

## 3. Celonis: dónde está cada cosa

- **Data Pool:** «OCPM DataPool IMPLEMENTACION». Es **compartido** con otros proyectos (PNC, reclamaciones…). No tocar sus tablas.
- **Data Job:** «Dependencia Global». Tarea de pruebas de Anthony: **«Pruebas Anthony»** (Transformation).
  - En el editor, **solo `SELECT`** para explorar: Execute query → Preview. **No pulsar Save** ni ejecutar `CREATE`, `DROP` o `INSERT` sin acordarlo con Roberto.
  - El editor ofrece «Translate to SparkSQL»: el dialecto por defecto es el clásico (Vertica). Funcionan `||`, `CAST`, `RIGHT`, `LENGTH`, `TO_CHAR`, `CASE`.
- **Data source:** las tablas locales están en **None (Global Schema)**. Las reales vendrán de la **conexión «Dependencia»** (entorno de **validación** de SIDEMA, no productivo; las tablas deberían ser iguales).
- **Filtros de extracción** (Table Configuration → Filtering): el *Filter Statement* es el `WHERE` sin la palabra WHERE, pero su intérprete **no admite funciones** (`TO_DATE` da «Error parsing filter»). Para fechas, usar el **Time Filter** (creation date / change date, eligiendo columna y fecha de inicio) o probar la fecha como texto (`FCALTA >= '2025-01-01'`, que depende de cómo la lea Oracle). Muestra pedida el 04/11: SOLICITUD con FCALTA ≥ 01/01/2025; HIST_ESTADO con FCMODI ≥ 01/12/2024; ESTADO_SOLICITUD entera. Esquema en origen: `DBA_SIDM.`
- **Extracción:** Data Integration → Extractions. Las tablas nuevas se buscan en MAYÚSCULAS o entre `%`. Solo sirven las del esquema DBA de SIDEMA (las `public.` dan error de permisos). Para tablas nuevas, ejecutar extracción **full**.
- **Objects & Events** (OCPM): Roberto usa el entorno de **validación y producción**. Los objetos se marcan con la **etiqueta «Dependencia»**. Puede que **ya exista** un objeto de solicitud de dependencia: comprobarlo antes de crear uno.
  - Cada objeto o evento es una SQL. **El `ID` es obligatorio.**
  - **Todo atributo de la SQL tiene que declararse en el objeto con exactamente el mismo nombre**; si no, no aparece en el Knowledge Model.
  - El Preview del objeto dice qué columnas no están mapeadas.
- **Cadena completa:** Extracción → Objetos y eventos (SQL) → Knowledge Model (KPIs en PQL) → Vistas (el cuadro).

## 4. Estado actual (04/11/2026)

- **La extracción real falla** con un error de la librería **Snappy** (compresión) en la JVM de extracción. Roberto lo consultó con Javier Olmeda. Pendiente.
- Mientras tanto, Roberto copió **3 tablas en local** (Global Schema). **Son muestras:** `SIDM_SOLICITUD` 100 filas, `SIDM_HIST_ESTADO` 100 filas, `SIDM_ESTADO_SOLICITUD` 41 filas (completa).
- **Las dos muestras no son de las mismas solicitudes:** de las 85 solicitudes del histórico, **0** están en `SIDM_SOLICITUD`. No es por el formato: `SIDM_SOLICITUD` tiene IDs de 2–3 cifras (18, 19, 304…) y el histórico, de 3–6 (11785, 147629…). Sirven para construir la estructura, no para ver recorridos. Se ha pedido a Roberto una muestra coherente.
- **`IDSOLICITUD` tiene distinto tipo en cada tabla** (numérico en una, texto en la otra): en los joins y UNION, convertir los dos con `CAST(... AS VARCHAR)`.
- **Objects & Events** (Data Pool «OCPM DataPool VALI…», validación): **el objeto `SolicitudDependencia` ya existe** (namespace custom, etiqueta Dependencia). **No hay eventos de Dependencia** todavía.
  - Referencia de otros proyectos: el evento «AltaSolicitud» (Discapacidad) tiene `ID` (PK, String) + `Time` (Datetime); el objeto «Cita» (Discapacidad) tiene 17 atributos tipados (Boolean, Datetime, String, Long integer).
  - Botones Test changes / Create version / **Deploy**: los cambios son un borrador hasta el Deploy, que los publica. **No hacer Deploy sin Roberto.**
- `SolicitudDependencia` se creó el 28/10 (en la reunión): solo tiene `ID` (PK, String) y etiqueta Dependencia. Su transformación «SolicitudDependenciaAttributes» solo tiene la plantilla comentada (sin SQL). Data preview desactivado.
- **Ojo, dos Data Pools:** las tablas SIDM locales están en **OCPM DataPool IMPLEMENTACION** (Global Schema, 28 tablas; Data Job «Dependencia Global»), pero el objeto está en **OCPM DataPool VALI…** (Global, 14 tablas, **sin SIDM**). La SQL de un objeto solo ve las tablas de su pool. Pregunta a Roberto: ¿modelar en implementación o copiar las tablas a validación?
- **Data Pools** (lista del 04/11): **OCPM DataPool IMPLEMENTACION** (extrae; 11 conexiones; estado rojo por la extracción fallida) · **OCPM DataPool VALIDACION y PRODUCCION** (modela; recibe conexiones compartidas «OCPM DataPool IMPLEMENTACION _ …») · **POC - Dependencia** (PoC de sept. 2025; posible referencia de trabajo previo con SIDEMA) · otros: 00 - Extraction Pool, PNC, OCPM Data Pool, POC Bono Social Térmico, POC Tramitación.
  - Entre pools se **comparten tablas**: el pool receptor las ve como otro *data source*. Hay que encontrar el data source de VALIDACION que trae las SIDM (o pedir a Roberto que las comparta).
- Editor de transformación del objeto: Transformation Scripts → Attributes (SQL del objeto) y Changes (opcional). Botones: Execute query, Preview, **Add attributes** (declara las columnas nuevas), Save with Validation, Cancel, Code Assistant.
- **Siguiente paso:** completar `SolicitudDependencia` (atributos y transformación) y crear los eventos (alta y cambio de estado). Muestra coherente pedida a Roberto (FCALTA del 1.er semestre de 2025 y todo su histórico).

## 5. Las tablas

Convención de nombres de SIDEMA: `ID` identificador · `NM` número visible · `CD` código · `DS` descripción · `FC` fecha · `IT` indicador (S/N).

### `SIDM_SOLICITUD` · el objeto (una fila por solicitud)
`IDSOLICITUD` (ID), `NMSOLICITUD`, `FCSOLICITUD`, `FCREGENTRADA`, `FCENTRADA_COMUNIDAD`, `FCALTA` (alta en SIDEMA = creación de la solicitud), `FCBAJA`, `FCMODI`, `IDMODI`, `CDESTADO` (estado actual), `CDMOTALTA`, `CDMOTBAJA`, `CDTIPO`, `CDPROVISIONAL`, `ID_EXPEDIENTE`, `ID_CICLO_VIDA`, `IDSOLICITANTE`, `IDREPRESENTANTE`, `IDREPRESENTANTE2`, `IDALTA`, `IDBAJA`, `NMREFERENCIA`, `NMREFERENCIA_EELL`, `NMREVISION`, `IDSOLICITUD_REVISION`, `IDSOLICITUD_ORIG_REVISION`, `NMREVISIONES_ORIGINAL`, `IT_URGENTE`, `IT_TRASLADO`, `ITEXTINGUIDO`, `IT_BLOQUEADO`, `ITGESTION`, `ITTRANSFERIDO`, `FC_FIN_PLAZO`, `FC_EFECTOS`, `FC_EFECTOS_ESTIMADA`, `ITINGRESO_RENTA`, `ITPATRIMONIO`, `ITBIENES`, `CD_CIPA`, columnas de envío (`ITENVIADO`, `FCENVIO`, `CDESTADOENVIO`, `CDMOTIVOENVIO`) y de ADEX/RGM/WS (técnicas).
- **No tiene** edad ni municipio: están en la tabla de personas (se llega por `IDSOLICITANTE`), que habrá que pedir.

### `SIDM_HIST_ESTADO` · los eventos (una fila por cada estado de cada solicitud)
`IDSOLICITUD`, `CDESTADO`, `FCMODI` (**la fecha del cambio**: no hay `FCALTA`), `IDMODI` (probablemente el usuario que hace el cambio; por confirmar).

### `SIDM_ESTADO_SOLICITUD` · diccionario de estados (no es el estado actual)
`CDESTADO`, `DSESTADO`, `FCALTA`, `FCBAJA`, `FCMODI`, `IDMODI`, `CDESTADO_GEST_VAL` (vacía en todos los estados: no sirve).

### Regla del join de estados (comprobada el 04/11)
- En el **histórico**, los códigos tienen **2 dígitos** (`50`, `40`…).
- En el **diccionario** hay códigos de 2 dígitos (`00`, `11`, `20`, `30`, `32`, `33`, `51`, `91`, `95`) y de 4 (`0650`, `0440`…).
- **Casan por los 2 últimos dígitos**, sin ambigüedad (cada código del histórico encuentra un único estado):
```sql
LEFT JOIN "SIDM_ESTADO_SOLICITUD" e ON RIGHT(e."CDESTADO", 2) = RIGHT(h."CDESTADO", 2)
```
- Los códigos son **texto** (con ceros delante): comparar siempre con comillas, `'01'`, no `1`.
- Coincide con la reunión: Andrés llamaba «98» al 1298 (el único con fecha de baja, 2022).
- **Pendiente:** confirmarlo con Roberto o SIDEMA.

### Lo que se ve en los datos (muestra local, 04/11)
- **La SQL del objeto Solicitud está validada** (sección 9): 100 filas y estado actual con nombre.
- La muestra de `SIDM_SOLICITUD` son las **primeras solicitudes de SIDEMA (mayo–julio de 2007)**, todas en estado 90 (Expediente resuelto).
- `NMSOLICITUD` = año + correlativo (`2007001830`).
- **Tres fechas de inicio distintas:** `FCREGENTRADA` (registro), `FCSOLICITUD` y `FCALTA` (alta en SIDEMA, que puede ser **meses después**). **`FC_FIN_PLAZO` ≈ `FCREGENTRADA` + 6 meses** → el plazo legal de 180 días cuenta desde el **registro de entrada**. Propuesta: que el proceso empiece en el registro (a confirmar con Andrés, que propuso `FCALTA` como evento inicial).
- Columnas vacías en la muestra: `FCBAJA`, `IT_URGENTE`, `IT_TRASLADO`, `NMREVISION`. `CDTIPO` solo tiene «RS» (¿qué es?). `ITEXTINGUIDO` = S/N/vacío. No se quitan hasta ver datos recientes.

## 6. Estados (por código de 2 dígitos) y propuesta de fases

| Cód. | Estado | Fase propuesta |
|---|---|---|
| 01 | Alta de Solicitud | Grabación |
| 03 | Alta Especial | Grabación |
| 60 | Expediente con documentación incompleta | Grabación |
| 30 | Expediente en proceso de subsanación | Grabación |
| 25 | Revisión Documentación | Grabación |
| 55 | Pendiente tratamiento administrativo | Grabación |
| 10 | Plan de Choque | Grabación |
| 09 | Beneficiario de otra CCAA | Grabación |
| 00 | Confirmar pendiente citación valoración | Citación |
| 40 | Pendiente de Citación de valoración | Citación |
| 39 | Pendiente de citación de valoración (geo-referenciar) | Citación |
| 99 | Expediente pendiente de citación | Citación |
| 98 | Pendiente citación por Coordinación (baja 2022) | Citación |
| 06 | Aviso de Citación de Oficio | Citación |
| 41 | Enviado a Citación | Citación |
| 42 | Citación Manual | Citación |
| 43 | Pendiente de Valoración | Valoración |
| 07 | En Proceso de Valoración en Centros | Valoración |
| 11 | Incidencia BVD | Valoración |
| 44 | Pendiente de Aplicación de Baremo | Valoración |
| 45 | Pendiente de realizar Dictamen Técnico | Valoración |
| 48 | Pendiente de generar Dictamen Técnico | Valoración |
| 32 | Pendiente de Revisión Equipo Técnico | Valoración |
| 47 | Pendiente de Comisión de Valoración | Valoración |
| 33 | Pendientes de comisión de valoración RA | Valoración |
| 50 | Pendiente de resolución | Resolución |
| 51 | Trámite de Audiencia | Resolución |
| 35 | Pendiente de notificación RA | Resolución |
| 04 | Pendiente Resolución Fallecimiento | Resolución |
| 70 | Pendiente Resolución Desestimatoria por Incumplir Requisitos (REQUERIDO) | Resolución |
| 71 | Pendiente Resolución Desestimatoria por Incumplir Requisitos (INICIAL) | Resolución |
| 05 | AVC | AVC (¿?) |
| 20 | Pendiente de resolución AVC | AVC (¿?) |
| 15 | Pendiente AVC | AVC (¿?) |
| 90 | Expediente Resuelto | Cierre |
| 02 | Resuelto con Servicios Prestados | Cierre |
| 34 | Resolución No Procede | Cierre |
| 36 | Resuelto No procede Grado III | Cierre |
| 95 | Expediente Resuelto Extinguido | Cierre |
| 08 | Fallecido después del Grado y Nivel | Cierre |
| 91 | Expediente Recurrido | Después del cierre |

- **No hay estados de PIA:** con estas tablas se cubre la solicitud y el reconocimiento del grado (fases 1 y 2 del CU1). El PIA está en otras tablas.
- **Pendiente de validar con Andrés:** la agrupación en fases, qué es **AVC** y qué es **RA**.
- Uso de la muestra (100 cambios): 50 (28), 40 (15), 90 (13), 43 (13), 01 (12), 47 (11), 45 (3), 60 (2), 05 (2), 04 (1).

## 7. Decisiones de modelado (reunión del 28/10 con Andrés y Roberto)

- **Un solo objeto: Solicitud** (de `SIDM_SOLICITUD`). Incluir atributos útiles para filtrar aunque no estén en el mockup.
- **Eventos:** no uno por estado (son demasiados), sino:
  - **Alta de solicitud** (inicial), con `FCALTA` de `SIDM_SOLICITUD`;
  - **Cambio de estado**, genérico, con el estado como atributo (código, descripción y fase), de `SIDM_HIST_ESTADO` + diccionario;
  - **un evento final** (cierre o resolución), a definir con la lista de estados.
- Para ver el proceso por estados, el atributo del estado (y la fase) va en el evento.

## 8. Qué del mockup CU1 sale con estas 3 tablas

| Mockup | ¿Se puede? |
|---|---|
| Vista global de plazos (frente a 180 días), subplazos por fase, evolución mensual | Sí (fases 1 y 2) |
| Indicador de tendencia (entradas frente a salidas por fase) | Sí |
| Plazos fraccionados por hito (citación, valoración en centros, citación manual) | Sí, por expediente |
| Equipo de subsanación | Parcial: «por trabajador» solo si `IDMODI` es el usuario |
| Carga y detalle por trabajador o valorador | No: falta la tabla de asignaciones |
| Variabilidad de grados por valorador | No: falta el grado y el valorador |
| Fase 3 · PIA | No: faltan las tablas del PIA |
| Filtros de territorio y edad | No: falta la tabla de personas |

## 9. SQL del modelo (validadas el 04/11 en «Pruebas Anthony»)

Están en **`dependencia/sql/`**, listas para pegar en Objects & Events:
- `01_objeto_SolicitudDependencia.sql`: objeto (100 filas, estado actual con nombre).
- `02_evento_RegistroEntrada.sql`: evento de inicio con `FCREGENTRADA` (99 filas; la 41 sin fecha).
- `03_evento_CambioEstado.sql`: un evento por fila del histórico, con código, estado, **fase** (`CASE`) y **usuario** (`IDMODI`). 100 filas, todas con fase, sin IDs repetidos.

Convenciones: `ID` y la relación `SolicitudDependencia` siempre con `CAST(... AS VARCHAR)`; prefijos de ID por tipo de evento (`REG_`, `CE_`); `Time` es la fecha del evento.

### Lo que enseña el histórico (muestra: tarde del 28/10/2011, 12:41–16:13)
- **`IDMODI` es el login del usuario** (RBO2, AAG50, GUIJOSA, EGV008, CLF10, MRR91…) → permite la parte «por trabajador» del mockup.
- RBO2 graba altas en serie (equipo de grabación).
- GUIJOSA pasa de 50 (Pendiente de resolución) a 90 (Resuelto) en **2 segundos**.
- EGV008 pasa unas 20 solicitudes a 50 en el mismo segundo (acción masiva).
- ⇒ Hay estados que son clics o lotes, no esperas reales: **medir las fases de entrada a salida de la fase**, no estado por estado.

## 10. Pendientes y preguntas abiertas

- [ ] Roberto o Javier Olmeda: error de Snappy en la extracción.
- [ ] Roberto: ¿los códigos casan por los 2 últimos dígitos en SIDEMA? ¿Puede darnos una muestra **coherente** (el histórico de las mismas solicitudes)?
- [ ] Roberto: ¿existe ya el objeto de solicitud de dependencia en Objects & Events? ¿Qué nombre usar?
- [ ] ¿`IDMODI` es el usuario que hace el cambio?
- [ ] Andrés: qué son AVC y RA; validar las fases; empezar el proceso en `FCREGENTRADA` (el plazo legal cuenta desde ahí: `FC_FIN_PLAZO` ≈ registro + 6 meses) y no en `FCALTA`; qué es `CDTIPO` = «RS».
- [ ] Pedir tablas para lo que falta: personas (edad, municipio), asignaciones o valoradores, grado, PIA.
