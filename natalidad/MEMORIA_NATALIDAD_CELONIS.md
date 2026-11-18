# Natalidad en Celonis · memoria de trabajo

Sin datos: solo estructura, consultas y decisiones (ver CLAUDE.md).

## 1. Qué hay que hacer (daily con Roberto, 18/11/2026)

Crear en **Objects & Events** los objetos y eventos de Natalidad a partir de las tablas de **Atlantix**, que guarda los expedientes de **todos** los procedimientos. Por eso, antes hay que **filtrar y hacer los joins** para quedarnos solo con los de Natalidad.

- **Dónde:** Data → Objects & Events del pool de **validación y producción** → Objects → buscar «natalidad».
- **Ya creado por Roberto:** un objeto de Natalidad sin atributos. Falta crearle los atributos y la transformación.
- **Objetos a replicar:** Procedimiento, Etapa y Documento, copiados de los objetos de Atlantix que ya existen (los de PnC) y adaptados. También hay que hacer el de Expediente o completarlo.
- **Eventos:** copiarlos **todos** de los de Atlantix y adaptarlos igual que los objetos.
- **Prefijo `Nat`** en todos los objetos y eventos nuevos, para distinguirlos.
- **En cada objeto:** atributos, transformación (SQL) y relaciones entre objetos, como en los de Atlantix (por ejemplo, «se relaciona con una etapa» o «incluye un expediente»).
- **No copiar** lo que no hace falta, por ejemplo el atributo «value cluster».
- **Sin Deploy sin Roberto** (como en Dependencia). Si falla un filtro, se revisa con él.

## 2. La regla del filtro (siempre, siempre)

- La **única forma** de saber que un dato es de Natalidad es el **código de aplicación** del expediente.
- Ese código está en la **tabla de expedientes** de Atlantix:
  - Nombre oído en la daily: `GSTA_BC_EXPEDIENTE`.
  - Columnas oídas: `C_APLICACION` (código de aplicación) y `C_EXPEDIENTE` (código de expediente).
  - **Nombres por confirmar** en el esquema.
- **Código de Natalidad:** oído como «D cero 32» (`D032`). **Por confirmar** el valor exacto que pasó Roberto.
- **Los objetos de Atlantix actuales** hacen el join con expedientes, pero solo filtran que el expediente no sea nulo. En los de Natalidad hay que **cambiar ese filtro** por el código de aplicación de Natalidad.
- Si la tabla del objeto **no tiene** el join con expedientes, hay que añadirlo usando el código de expediente. Sin el filtro salen todos los procedimientos y los joins quedan mal.

### Patrón de Roberto (al inicio de cada query)

```sql
WITH exp_nat AS (                         -- lista de expedientes de Natalidad, sin repetidos
    SELECT DISTINCT e."CDEXPEDIENTE"
    FROM "GSTA_V_CEL_EXPEDIENTE" e
    WHERE e."CDAPLICACION" = 'D032'        -- aplicación de Infancia, Familia y Natalidad
      AND e."CDPROCEDIMIENTO" = '3163'     -- ayudas económicas a la natalidad
)
SELECT ...
FROM "<tabla del objeto o evento>" t
INNER JOIN exp_nat n                       -- INNER: solo las filas de expedientes de Natalidad
        ON n."CDEXPEDIENTE" = t."CDEXPEDIENTE"
```

- **`INNER JOIN`:** deja solo las filas que casan con la lista. Con este patrón **no hace falta** repetir el filtro en el `WHERE`.
- **`LEFT JOIN`:** deja todas las filas de la tabla base y deja vacías las que no casan. Si se usa `LEFT JOIN` con la tabla de expedientes, el filtro `C_APLICACION = …` va en el `WHERE`.
- Si una tabla no tiene `C_EXPEDIENTE` (por ejemplo, documentos que cuelgan de una etapa), se llega a él a través de la tabla que sí lo tenga.

## 2b. Data Source de Natalidad (¡en cada transformación nueva!)

- Las tablas de Atlantix (`GSTA_…`) están en **«OCPM DataPool IMPLEMENTACION _Conexión Producción PRATLX_RO»** (36 tablas).
- Cada transformación nueva se abre con **None (Global)**, que es el pool de validación y no tiene esas tablas. Si no se cambia, da el error «Object 'GSTA_V_CEL_EXPEDIENTE' not found».
- **Otras opciones del desplegable (no usar para Natalidad):**
  - OCDM Schema.
  - IMPLEMENTACION _Conexion DISCA - DESARROLLO a DSSOCIAL.
  - IMPLEMENTACION _Conexion PnC PRODUCCION PRSOCIAL.
  - IMPLEMENTACION _ Conexion DISCA PRODUCCION PRSOCIAL.
  - CM-Consejeria Familia y Asuntos Sociales - PNC_global.

## 3. Lo aprendido en Dependencia que vale aquí

- Todas estas notas vienen de `dependencia/MEMORIA_DEPENDENCIA_CELONIS.md`, sección 3.
- **El `ID` es obligatorio.**
- Cada columna de la SQL se declara en el objeto con **el mismo nombre** («Add attributes»).
- SQL **sin punto y coma**.
- **Data Source** = None (Global): cada transformación nueva se abre con OCDM Schema y hay que cambiarlo.
- `TO_CHAR` no funciona; usar `CAST(... AS VARCHAR)`.
- **Orden que funciona:** crear el objeto o evento, después la relación (*Related objects*) y por último la transformación. Así la plantilla trae la columna de la relación.

## 3b. Objetos de referencia: etiqueta «PnC ATL» (7 de 17 objetos)

Solo estructura (nombres y tipos de atributos), vista el 18/11:

- **`PnCExpedientes`** (23 + ID):
  - `DescripcionProcedimiento`, `CodigoProcedimiento`, `Aplicacion`, `CodigoExpediente`, `EjercicioConvocatoria`, `CodigoConvocatoria`.
  - `idUnidad`, `DescripcionUnidad`, `idEstado`, `DescripcionEstado`, `UsuarioAsignado`.
  - Fechas: `FechaPresentacionInteresado`, `FechaEntradaSistemaRegistro`, `FechaEntradaRegistroConsejeria`, `FechaInicio`, `FechaFinTramitacion`, `FechaResolucion`, `FechaCierre`, `FechaAnulacion`.
  - **Duplicadas:** `FCINICIO`, `FCRESOLUCION` y `FCFINTRAMITACION` repiten fechas que ya están arriba; no copiarlas sin preguntar.
  - **El objeto ya trae `Aplicacion`**: aquí el filtro de Natalidad es un `WHERE`, sin join.
- **`PnCEtapas`** (3 + ID): `IDEtapa`, `DescripcionEtapa`, `Confiscalizacion`.
- **`PnCExpedienteDetalle`** (21 + ID): datos propios de PnC.
  - Nacionalidad y país de nacimiento.
  - Trasvase y tipo de pensión.
  - Personas en la unidad de convivencia (UEC).
  - Usuarios y códigos de tramitador.
  - Último trámite, estado, registro de entrada, observaciones, número de solicitud y número de expediente.
- **`PnCInteresados`** (16 + ID):
  - Edad y fecha de nacimiento.
  - Es principal.
  - Tipo de notificación.
  - Provincia, municipio y país (de residencia y de notificación).
- **`PnCPropuesta`** (15 + ID):
  - Tipo, código, indicador, origen y estado de la propuesta.
  - Fecha de propuesta y fecha de resolución.
  - Cuantía mensual, cuantía anual, cuantía de tercera persona y atrasos.
  - Usuario y código del tramitador.
  - Es migrada.
- **`PnCRevision`** (21 + ID), propio de PnC (revisiones de la pensión):
  - Número, año, tipo, código de tipo, origen y código de origen de la revisión.
  - Motivo, situación, estado y resultado de la revisión.
  - Motivo sin variación, situación según estado y es migrada.
  - Fechas: apertura, entrada, primera propuesta, resolución, resolución del documento, efecto y última modificación.
- `PnCPropuestaMotivos`: pendiente de ver.

**Ojo:** Roberto habló de Procedimiento, Etapa y Documento, pero en «PnC ATL» no aparecen ni Procedimiento ni Documento. Pueden estar entre los otros 10 objetos o sin etiqueta. Hay que preguntarle cuáles son.

## 3c. La SQL de `PnCExpedientes` (vista el 18/11)

- **Origen confirmado:** la vista **`GSTA_V_CEL_EXPEDIENTE`** (no `GSTA_BC_EXPEDIENTE`, como se oyó en la daily).
  - Columnas clave: **`CDEXPEDIENTE`** (ID), **`CDAPLICACION`** y `CDPROCEDIMIENTO`.
  - PnC filtra con `CDAPLICACION = 'PNCA'`.
- **La vista tiene varias filas por expediente** (una por solicitud o registro):
  - Las fechas de solicitud (`FC_SOL_INTERESADO`, `FC_SOL_EREG`, `FC_SOL_CONS`) y `FCCIERRE` se agregan con `MIN`.
  - El resto de columnas va en el `GROUP BY`, para que salga una sola fila por expediente.
- El nombre del procedimiento sale de un `CASE` con los códigos de PnC (0375, 1922, 3931). En Natalidad habrá que poner los suyos.
- **Las SQL de Natalidad están en `natalidad/sql/`:**
  - `00_comprobar_codigos.sql`: lista las aplicaciones y los procedimientos de la vista, para confirmar el código de Natalidad.
  - `01_objeto_NatExpedientes.sql`: la SQL del objeto `NatExpedientes`.

## 3d. Lo que se ve en `NatExpedientes` (Preview del 18/11, unas 100 filas; sin datos)

- **El filtro funciona:** todo es del procedimiento 3163 y de la Sección de Ayudas Económicas a la Natalidad (`IdUnidad` siempre igual).
- **`DescripcionEstado` no sirve para seguir el proceso:** casi todo sale «Iniciado», aunque tenga fecha de resolución; solo aparece también «Anulado». El avance real del expediente tendrá que salir de etapas e hitos.
- **`IdEstado` no es un código de estado común:** va por convocatoria y ejercicio (un valor distinto por año y por estado). Para estados, usar `DescripcionEstado`.
- **`CodigoConvocatoria`:** AFN1 y AFN2. ¿Qué diferencia hay entre las dos líneas? Preguntar.
- **`EjercicioConvocatoria`** es el año de la convocatoria y puede no coincidir con el año del expediente.
- **Las tres fechas de entrada** (`FechaPresentacionInteresado`, `FechaEntradaSistemaRegistro`, `FechaEntradaRegistroConsejeria`) son **iguales** en la muestra.
- **`FechaInicio`** (alta en Atlantix) llega días o meses después del registro: sirve para medir el tiempo de registro a alta.
- **`FechaResolucion`:**
  - Está vacía en muchos expedientes.
  - Muchas llevan hora 00:00:00 y se repiten los mismos días: parecen resoluciones por lotes o fechas de efecto.
- **Columnas siempre vacías en la muestra:** `FechaCierre`, `FechaFinTramitacion`, `UsuarioAsignado`. En los anulados, solo hay `FechaAnulacion` y no hay fechas de entrada.
- **Lo que cubre el objeto del mockup:**
  - Entradas (fecha de registro).
  - Alta, resolución y anulación.
  - Convocatoria y ejercicio.
- **Lo que falta, por buscar en otras tablas:**
  - Histórico de etapas e hitos.
  - Tipo de solicitud, número de hijos y fechas del menor.
  - Datos de la solicitante.
  - Requerimientos y notificaciones.
  - Revisión de conformidad, propuesta a nómina, Intervención y pagos (Nexus).
  - Tipo de resolución y motivo de denegación.
  - Bajas y modificaciones.

## 3e. Tablas del data source (18/11)

Data source «OCPM DataPool IMPLEMENTACION _Conexión Producción PRATLX_RO», con 36 tablas.

**Atlantix genéricas (`GSTA_`), que valen para Natalidad filtrando por expediente:**

| Tabla | Para qué nos sirve |
|---|---|
| `GSTA_V_CEL_EXPEDIENTE` | Objeto NatExpedientes (hecho) |
| `GSTA_V_CEL_CAT_PROC` | Catálogo de procedimientos: el **nombre** de cada procedimiento, en lugar del `CASE` |
| `GSTA_V_CEL_ETAPA`, `GSTA_V_ETAPAS`, `GSTA_ETAPA` | Etapas e histórico de etapas → objeto NatEtapas y eventos de cambio de etapa |
| `GSTA_V_CEL_HITO` | Hitos con fecha → eventos |
| `GSTA_V_CEL_ACTIVIDAD`, `GSTA_REGISTRO_ACTIVIDAD` | **Bitácora** (actividades con fecha) → eventos. Era una duda del documento funcional |
| `GSTA_V_CEL_NOTIFICACION` | Notificaciones → requerimientos (puesta a disposición y acceso) |
| `GSTA_V_CEL_DOC_APORT_CIUD` | Documentos que aporta la ciudadana (subsanaciones) → Documento |
| `GSTA_V_CEL_DOC_APORT_ADMIN` | Documentos que aporta la administración → Documento |
| `GSTA_V_CEL_DOC_ELABORADA` | Documentos elaborados (requerimientos, resoluciones…) → Documento |
| `GSTA_V_CEL_CAT_DOCREQ` | Catálogo de documentación requerida |
| `GSTA_V_INTERESADOS` | Solicitante → NatInteresados |
| `GSTA_V_EXPEDIENTE` | Otra vista de expediente (por ver qué añade) |
| `SUCA_PAIS`, `CELONIS_CALENDAR` | Catálogo de países y calendario |

**Propias de PnC (`PNCA_`), que no sirven para Natalidad:** expediente, interesado, conviviente, propuesta, revisiones, reclamaciones, causas de denegación y catálogos.

**No hay tablas propias de Natalidad.** Faltan los equivalentes de las `PNCA_`:
- tipo de solicitud, número de hijos y fecha de nacimiento o de parto;
- propuesta a nómina e importes;
- tipo de resolución y motivo de denegación;
- bajas y modificaciones.

Además, Nexus (pagos, Intervención) y eReg (canal, tipo de asiento) tampoco están. **Hay que preguntar a Roberto** si existen las tablas de la aplicación de Natalidad en Atlantix y si se pueden extraer.

## 3f. Qué se copia (objetos y eventos del pool de validación, 18/11)

- **Objetos:** son 17 en total. **No existen** los objetos «Procedimiento» ni «Documento». Lo que Roberto llamó así son, en la práctica:
  - `PnCEtapas`;
  - los **eventos** de documentos;
  - el procedimiento, que es un atributo del expediente.
- **Objetos de otros proyectos** (no se tocan): Cita, Despistaje, Entradas, Expediente, Solicitud, SolicitudDependencia, SolicitudesPnc, TFACS, Usuarios.

**Plan de objetos `Nat`:**

| Objeto PnC | Objeto Nat | Notas |
|---|---|---|
| `PnCExpedientes` | `NatExpedientes` | Hecho |
| `PnCEtapas` | `NatEtapas` | Siguiente |
| `PnCInteresados` | `NatInteresados` | Solo si sale de `GSTA_V_INTERESADOS`; si sale de `PNCA_INTERESADO`, no hay equivalente |
| `PnCExpedienteDetalle`, `PnCPropuesta`, `PnCPropuestaMotivos`, `PnCRevision` | — | Tablas `PNCA_`, propias de PnC |

**Eventos PnC → Nat:** son 54 eventos en total; 23 llevan prefijo PnC.
- **Se copian 21, basados en tablas `GSTA_`:**
  - Actividades: `ActividadInicio`, `ActividadRealizada`, `ActividadResolucion`, `EventosAutomaticos`.
  - Documentos: `DocAportadosConsultadosAdministracion`, `DocumentosAportadosCiudadano`, `DocumentosElaborados`.
  - Etapas y fases: `EtapaIniciada`, `EtapaFinalizada`, `Etapas` (ver qué es), `FaseIniciada`.
  - Hitos y notificaciones: `Hitos`, `Notificaciones`.
  - Expediente: `ExpedienteAbierto`, `ExpedienteAnulado`, `ExpedienteCerrado`, `ExpedienteFinalizado`, `ExpedienteResuelto`.
  - Solicitud: `SolicitudPresentada`, `SolicitudRecibidaConsejeria`, `SolicitudRegistrada`.
- **No se copian:** `PnCRevisionAbierta` y `PnCRevisionPropuesta`, que son propios de PnC.
- **Antes de copiar cada uno:** comprobar en su SQL que lee de tablas `GSTA_` (si lee de `PNCA_`, no se copia).

## 3g. `PnCEtapas` → `NatEtapas` (18/11)

- Hay dos transformaciones con el nombre «PnCEtapas»: la del **objeto** (`PnCEtapas - 2`) y la del **evento** PnCEtapas (`PnCEtapas - 1`).
- **SQL del objeto:** el patrón de Roberto tal cual.
  - CTE `Expedientes` = `SELECT DISTINCT CDEXPEDIENTE FROM GSTA_V_CEL_EXPEDIENTE WHERE CDAPLICACION = 'PNCA'`.
  - Después, `INNER JOIN` de `GSTA_V_CEL_ETAPA` con esa CTE.
- **`ID` = `'Etapa_' || IDETAPA || '_' || CDEXPEDIENTE`:** una fila por cada etapa de cada expediente, no un catálogo de etapas.
- **Atributos:** `IDEtapa` (`IDETAPA`), `DescripcionEtapa` (`DSETAPA`), `Confiscalizacion` (`CONFISCALIZACION`, S/N).
- **Relación:** la columna `"PnCExpedientes"` (= `CDEXPEDIENTE`) es la relación con el objeto expediente; en el Preview sale como `PnCExpedientes_ID`.
- **Los `IDETAPA` son propios de cada procedimiento.** Las de PnC son del tipo alta, propuesta, Intervención, notificación, paso a nómina, archivo y migración. Natalidad tendrá las suyas.
- SQL adaptada: `natalidad/sql/02_objeto_NatEtapas.sql` (filtro D032 + 3163, relación `"NatExpedientes"`).
- **Relaciones de PnC (vistas el 18/11):**
  - `PnCExpedientes` **1 — N** con `PnCEtapas`, `PnCInteresados`, `PnCPropuesta`, `PnCRevision` y `PnCExpedienteDetalle`.
  - En cada una, la **FK se llama `PnCExpedientes`** y está en el objeto hijo (el del lado N).
  - Aparece tanto en el padre como en el hijo.
- **Para Natalidad:** `NatExpedientes` **1 — N** `NatEtapas`, con la FK `NatExpedientes`.
- `NatEtapas` está **creado** (18/11): etiqueta Natalidad y 3 atributos String (`IDEtapa`, `DescripcionEtapa`, `Confiscalizacion`).

## 3h. Etapas de Natalidad (Preview de NatEtapas, 18/11)

- **La transformación funciona** con el data source PRATLX_RO, y la relación sale como `NatExpedientes_ID`.
- **`IDEtapa` cambia según la convocatoria o el año.** La misma etapa tiene un ID distinto cada año: por ejemplo, VALIDACIÓN TERCERO aparece como 42759, 55399, 70897 y 100598. **Para fases y actividades se usa `DescripcionEtapa`**, no el ID.
- **Etapas vistas en la muestra** (nombres de catálogo, en orden lógico):
  1. GESTIÓN EXPEDIENTE
  2. VALIDACIÓN TERCERO (alta del tercero en Nexus)
  3. PROPUESTA FAVORABLE
  4. FAVORABLE CONCESIÓN / FAVORABLE INCIDENCIA
  5. PTE. ENVÍO INTERVENCIÓN
  6. INTERVENCIÓN CONCESIÓN (`Confiscalizacion = 'S'`)
  7. RESOLUCIÓN FAVORABLE
  - **Salidas:** RESOLUCIÓN DENEGACIÓN, RESOLUCIÓN DESESTIMIENTO.
  - **Después de conceder:** MODIFICACIÓN CONCESIÓN, INTERVENCION PAGO UNICO (`S`).
- **El objeto no tiene fechas.** Cuándo empieza y termina cada etapa saldrá de los eventos `EtapaIniciada` y `EtapaFinalizada`.
- **Catálogo completo** (18/11). Expedientes del 3163 que pasan por cada etapa (`DSETAPA`, todos los años):

| Etapa | Exp. | Grupo inicial (sustituido por `Fase`, ver abajo) |
|---|---|---|
| GESTIÓN EXPEDIENTE | 52.983 | 1. Gestión |
| REQUERIMIENTO | 6.001 | 1. Gestión |
| VALIDACIÓN TERCERO | 38.368 | 2. Propuesta |
| PROPUESTA FAVORABLE | 38.368 | 2. Propuesta |
| PTE. ENVÍO INTERVENCIÓN | 37.792 | 3. Intervención |
| INTERVENCIÓN CONCESIÓN | 37.790 | 3. Intervención |
| FAVORABLE CONCESIÓN | 34.105 | 3. Intervención (respuesta) |
| FAVORABLE CON OBS CONCESIÓN | 764 | 3. Intervención (respuesta) |
| ACTUACIÓN INTERESADA CONCESIÓN | 156 | 3. Intervención (respuesta) |
| DEV A INSTANCIA PROMO CONCESIÓN | 14 | 3. Intervención (respuesta) |
| RESOLUCIÓN FAVORABLE | 34.869 | 4. Resolución |
| RESOLUCIÓN DENEGACIÓN | 9.232 | 4. Resolución |
| RESOLUCIÓN DESESTIMIENTO | 2.989 | 4. Resolución |
| MODIFICACIÓN CONCESIÓN | 15.241 | 5. Mantenimiento |
| FAVORABLE INCIDENCIA | 3.725 | 5. Mantenimiento |
| RESOLUCIÓN MODIFICACIÓN | 3.590 | 5. Mantenimiento |
| PTE.ENVÍO MODIFICACIÓN ECONÓM. NEGATIVA / INTERV INCIDEND. NEGATIVA | 2.619 | 5. Mantenimiento |
| PTE.ENVÍO MODIFICACIÓN ECONÓM. POSITIVA / INTERV INCIDEND. POSITIVA | 973 | 5. Mantenimiento |
| PTE.ENVÍO BAJA DE LA AYUDA / INTERV INCIDEND. BAJA AYUDA | 195 | 5. Mantenimiento |
| RESOLUCIÓN BAJA | 192 | 5. Mantenimiento |
| DEV A INSTANCIA PROMO INCIDENCIA | 109 | 5. Mantenimiento |
| PTE.ENVÍO MODIFICACIÓN SIN REPERC. ECONÓM. / INTERV SIN VARIAC. IMP. AYUDA | 72 | 5. Mantenimiento |
| FAVORABLE CON OBS INCIDENCIA | 42 | 5. Mantenimiento |
| ACTUACIÓN INTERESADA INCIDENCIA | 11 | 5. Mantenimiento |
| PTE. ENVIO INTERV. PAGO UNICO / INTERVENCION PAGO UNICO | 573 | 6. Pago único |

- **Lectura:**
  - El camino de la concesión es Gestión → Validación del tercero y Propuesta → envío a la Intervención → respuesta de la Intervención (favorable, favorable con observaciones, actuación interesada o devolución) → Resolución.
  - Las salidas son la denegación (9.232) y el desistimiento (2.989).
  - El **mantenimiento** (modificaciones positivas o negativas, bajas, sin variación) también pasa por la Intervención.
- **Cubre del mockup:**
  - Requerimientos.
  - Envío a la Intervención y tipo de respuesta.
  - Tipo de resolución (favorable, denegación o desistimiento).
  - Modificaciones y bajas.
  - Pago único.
- **El mockup SÍ tiene fases** (v31, `const FASES`). Su catálogo dice «etapas administrativas de Atlantix (**procedimiento 3163**, documento E2E)», lo que **confirma el filtro 3163**.
  - Las fases del mockup son:
    1. Entrada (registro → alta), que no es una etapa de Atlantix.
    2. Gestión del expediente.
    3. Validación de terceros.
    4. Intervención.
    5. Resolución y pago.
  - Las modificaciones van en mantenimiento.
- **Atributo `Fase` en `NatEtapas`** (CASE sobre `DSETAPA`, en `natalidad/sql/02_objeto_NatEtapas.sql`):
  - **2. Gestión del expediente:** GESTIÓN EXPEDIENTE, REQUERIMIENTO.
  - **3. Validación de terceros:** PROPUESTA FAVORABLE, VALIDACIÓN TERCERO. En el mockup, tras la propuesta favorable el expediente pasa a terceros.
  - **4. Intervención:** PTE. ENVÍO INTERVENCIÓN, INTERVENCIÓN CONCESIÓN, ACTUACIÓN INTERESADA y DEV A INSTANCIA PROMO (respuestas no favorables).
  - **5. Resolución y pago:** FAVORABLE CONCESIÓN, FAVORABLE CON OBS, RESOLUCIÓN FAVORABLE. El primer pago vendrá de Nexus.
  - **Fin sin concesión:** RESOLUCIÓN DENEGACIÓN, RESOLUCIÓN DESESTIMIENTO.
  - **Mantenimiento:** modificaciones, bajas e incidencias.
  - **Pago único.**
  - Lo que no case queda como «Sin clasificar».
- **18/11: `Fase` añadido a `NatEtapas`** y comprobado en el Preview. Los 30 nombres del catálogo están todos en el CASE (comprobado contra la lista), así que no debería salir ninguno «Sin clasificar».
- **Etapas del mockup que no aparecen en los datos del 3163:** «No Fiscalizable Concesión» y «Desfavorable Concesión».

## 3h2. Eventos de etapa: `PnCEtapaIniciada` → `NatEtapaIniciada` (18/11)

- **Atributos de PnC:** `ID`, `Time` (Datetime), `Actividad`, `Etapas`, `Fecha Inicio Etapa` y `Fecha Fin Etapa` (Datetime, **con espacios** en el nombre), `Fase`.
- **Relaciones:** *Involves one* `PnCEtapas` (relationship name `PnCEtapas`) e *Involves one* `PnCExpedientes` (`PnCExpedientes`).
- **Columnas de `GSTA_V_CEL_ETAPA` que usa:** `FCINICIO`, `FCFIN`, `FCINICIO_SISTEMA`, `FCFIN_SISTEMA`.
- **`ID` = `'EtapaIniciada_' + expediente + etapa + FCINICIO + rn`:** cada entrada en una etapa es un evento distinto. **Esto resuelve los reprocesos.**
  - `rn` = `ROW_NUMBER()`, que desempata dos filas con la misma etapa y la misma fecha de inicio.
- **`Time`:** `FCINICIO`, salvo cuando viene a las 00:00:00. En ese caso usa `FCINICIO_SISTEMA` si es del mismo día, para tener la hora real.
- **La `Fase` de PnC** es un CASE con `LIKE` sobre sus etapas. En Natalidad usamos las fases del mockup, igual que en `NatEtapas`.
- **SQL de Natalidad:** `natalidad/sql/03_evento_NatEtapaIniciada.sql`.
- **18/11: `NatEtapaIniciada` creado y funcionando.**
  - Etiqueta Natalidad, 7 atributos y relaciones *involves one* `NatEtapas` y `NatExpedientes`.
  - Preview correcto: `Time` con hora y `Fase` asignada.
  - **Ojo:** al crear `Fecha Inicio Etapa` y `Fecha Fin Etapa` quedaron como String y la validación falló («Expected VARCHAR… analyzed TIMESTAMP»). Se corrigieron a Datetime. **Revisar siempre el tipo al crear atributos.**
- **Lo que se ve en los datos:**
  - **`Fecha Fin Etapa` (`FCFIN`) viene sin hora** (00:00:00, a menudo del día siguiente). Para medir duraciones, mejor usar el inicio de la etapa siguiente, que sí lleva hora.
  - Las respuestas de la Intervención (FAVORABLE CONCESIÓN, FAVORABLE CON OBS) se graban **por lotes**: cientos de expedientes en el mismo minuto.

## 3i. Revisión del mockup v31 frente a los datos (18/11)

Esta lista es la base de la tabla final de lo que falta (Atlantix, eReg, Nexus y unidad). Estados posibles:
- ✅ lo tenemos;
- 🔍 puede estar en el pool, hay que mirarlo;
- ❌ no está en el pool.

**Afecta ya al modelado en Celonis:**
1. **Reprocesos y stock por fase:** `NatEtapas` usa `SELECT DISTINCT` con ID = etapa + expediente, así que si un expediente vuelve a la misma etapa se queda en una sola fila. Las vueltas atrás (de Terceros o de Intervención a Gestión) tienen que salir de los **eventos** `EtapaIniciada` y `EtapaFinalizada`, una fila por cada vez. Hay que comprobar en su SQL que el ID lleva la fecha o una secuencia.
2. **Revisión de conformidad** («revisados sin proponer», un KPI clave de la cabecera): **no es una etapa** en los datos. 🔍 Buscarla en actividades o hitos (`GSTA_V_CEL_ACTIVIDAD`, `GSTA_V_CEL_HITO`).
3. **Dentro de Validación de terceros:** fichero mensual a gestión económica, tercero creado o rechazado en Nexus, y carga en Atlantix. 🔍 Actividades o hitos.
4. **Requerimientos:**
   - notificación (puesta a disposición y acceso): 🔍 `GSTA_V_CEL_NOTIFICACION`;
   - aportación de la solicitante: 🔍 `GSTA_V_CEL_DOC_APORT_CIUD`;
   - **plazo de aportación**, para «plazo vencido»: 🔍.
5. **Días sin actuación** (tabla de expedientes sin actividad): fecha de la última actuación. 🔍 Bitácora (`GSTA_V_CEL_ACTIVIDAD`, `GSTA_REGISTRO_ACTIVIDAD`).
6. **Datos de la solicitante** (edad en tramos, nacionalidad, país de nacimiento, municipio): 🔍 `GSTA_V_INTERESADOS` → `NatInteresados`.
7. **Nombre del procedimiento:** 🔍 `GSTA_V_CEL_CAT_PROC`. Es opcional.

**No está en el pool:**
- **Atlantix, tablas propias de Natalidad ❌:**
  - **tipo de solicitud** (nacimiento, gestación, adopción, otros), que es un **filtro global** del mockup;
  - hijos por solicitud y fecha de nacimiento o de parto (para extinciones y pagos únicos);
  - **mes de nómina propuesto** e **importe propuesto por anualidad** (atrasos y mensualidades);
  - **requisito incumplido** o motivo de denegación;
  - **bandeja de registros:** entrada, alta y **descarte por duplicada**.
- **eReg ❌:**
  - asientos (solicitudes y aportaciones), **canal** (sede, oficina, ORVE) y tipo de documento;
  - las solicitudes **pendientes de alta**: hoy solo vemos las que ya tienen expediente (`FC_SOL_EREG`);
  - número de registro, para unir con Atlantix.
- **Nexus ❌:**
  - tercero creado o rechazado, **primer pago (ADOK)**;
  - nóminas: altas en nómina, beneficiarias activas, pagos únicos y rectificaciones, beneficiarias que dejan de cobrar (extinción o baja);
  - **A / D / OK** por línea y anualidad, y documento D.
- **NOTE:** la notificación del requerimiento puede estar en `GSTA_V_CEL_NOTIFICACION` (🔍); si no, ❌.
- **Unidad:** calendario mensual de nómina, plazo de tramitación (parámetro de 90 días por defecto) y quién mueve cada situación («Depende de»: Unidad, Solicitante, Gestión económica, Intervención, Calendario).
- **Otros:**
  - `FechaResolucion` lleva hora 00:00 y se repite: ¿es la de firma o la de efectos?
  - `AFN1` / `AFN2`: ¿qué diferencia hay?
  - Etapas del mockup que **no aparecen** en los datos: «No Fiscalizable Concesión» y «Desfavorable Concesión».

## 4. Estado y pendientes

- [x] Tabla y columnas: `GSTA_V_CEL_EXPEDIENTE`, `CDAPLICACION`, `CDEXPEDIENTE`.
- [x] **`D032` existe** en `GSTA_V_CEL_EXPEDIENTE` (18/11). Roberto ya había pegado en `NatExpedientes` la SQL de PnC con `CDAPLICACION = 'D032'`; está guardada y su Data Source es OCPM DataPool IMPLEMENTA…
  - Aplicaciones en la vista: `BSTE` (1 procedimiento: 2906, ¿Bono Social Térmico?), `PNCA` (0375, 1922) y `D032`.
  - **`D032` tiene 12 procedimientos:** 0296, 1246, 3163, 3224, 3252, 3331, 3356, 3559, 3630, 3656, 4068, 4074. Falta saber si **todos son de Natalidad** o si `D032` abarca más ayudas de la Consejería.
  - Tamaño y fechas de inicio (18/11). Solo recuentos, sin datos personales:

    | Proc. | Expedientes | Primer inicio | Último inicio | Lectura |
    |---|---|---|---|---|
    | **3163** | **53.375** | 01/2022 | 11/2026 | **El grueso, activo** |
    | **3331** | 4.681 | 09/2022 | 11/2026 | Activo |
    | 3630 | 1.299 | 01/2024 | 11/2026 | Activo |
    | 3559 | 1.233 | 09/2023 | 11/2026 | Activo |
    | 3356 | 522 | 10/2022 | 04/2024 | Cerrado |
    | 1246 | 420 | 04/2018 | 06/2026 | Antiguo |
    | 0296 | 272 | 01/2024 | 06/2026 | — |
    | 3224 | 57 | 03/2024 | 10/2026 | — |
    | 3252 | 43 | 07/2022 | 09/2022 | Puntual |
    | 3656 | 16 | 11/2024 | 11/2024 | Puntual |
    | 4068 | 10 | 10/2026 | 11/2026 | Nuevo |
    | 4074 | 2 | 10/2026 | 11/2026 | Nuevo |

  - **18/11: `D032` NO es solo Natalidad.** Es la aplicación de la Consejería (FJAS) para Infancia, Familia y Natalidad. Unidad que tramita cada procedimiento y prefijo del expediente:

    | Proc. | Prefijo | Unidad |
    |---|---|---|
    | **3163** | **AFN** | **Sección de Ayudas Económicas a la Natalidad** |
    | 3331 | SCP | Sección de Subvención de partos múltiples (7 expedientes en la DG) |
    | 3630 | ANA | Sección de Subvención de partos múltiples |
    | 1246 | SRM | D.G. de Infancia, Familia y Fomento de la Natalidad |
    | 0296, 3224 | 029, 322 | Área de Adopción y Acogimiento Familiar (**pista para Acogimiento**) |
    | 3252, 3356, 3559 | IN3, ATM, GEF | Subdirección General de Protección a la Infancia |
    | 3656, 4068, 4074 | CDI, VSM, 407 | Subdirección General de Infancia y Adolescencia |

  - **Decisión propuesta: Natalidad = `CDPROCEDIMIENTO = '3163'`**, además de `CDAPLICACION = 'D032'`.
  - **Por confirmar con Roberto o la unidad:** si partos múltiples (3331, 3630) entra en el cuadro y qué es 1246.
  - **Mientras tanto:** el objeto lleva todos los de `D032`, con `CodigoProcedimiento` como atributo para poder filtrar después.
- **«N columns ignored» en el Preview:** son columnas de la SQL que el objeto aún no tiene declaradas. *Add attributes* abre «Edit attributes», que **no las rellena solo**: se añaden a mano con *+ Add*, con el nombre idéntico al alias de la SQL y su tipo.
- Prefijos de los expedientes de `D032`: AFN, SCP, ANA, GEF. Probablemente corresponden a procedimientos distintos; sirven como pista para saber cuáles son de Natalidad.
- **Truco del editor:** *Preview selection* solo muestra las columnas mapeadas al objeto (el `ID`) y exige que haya columna `ID`. Para ver otras columnas, usar *Execute query selection* o meter la información en el `ID` concatenando con `||`.
- [x] Objeto de Roberto (18/11): **`NatExpedientes`** en «OCPM DataPool VALI…», namespace custom, etiqueta **Natalidad** (Custom Processes), descripción «Expedientes de Natalidad Atlantix». Solo tiene `ID` (PK, String). Los objetos de Atlantix de referencia llevan, probablemente, la etiqueta **«PnC ATL»**.
- [x] `NatExpedientes` (18/11): transformación con `natalidad/sql/01_objeto_NatExpedientes.sql` y 18 atributos declarados a mano (10 String y 8 Datetime). Preview correcto, filtro 3163 añadido, guardado con Save with Validation (sin Deploy). **Hecho.**
- [ ] `NatProcedimiento`, `NatEtapa`, `NatDocumento` (y `NatExpediente`): atributos, transformación con el filtro y relaciones.
- [ ] Eventos `Nat…`: todos los de Atlantix, con el mismo filtro.
- [ ] Revisar con Roberto antes de Create version / Deploy.
