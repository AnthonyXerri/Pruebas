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
- `TO_CHAR` no funciona; usar `CAST(... AS VARCHAR)`. **`POSITION` y `CHAR_LENGTH` tampoco** («No match found for function signature …»). Para recortar textos, probar `SUBSTRING(texto FROM n)`; `RIGHT` sí funciona.
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

## 3h3. `PnCEtapaFinalizada` → `NatEtapaFinalizada` (18/11)

- **Igual que `PnCEtapaIniciada`**, con estas diferencias:
  - `Time` = `FCFIN`, o `FCFIN_SISTEMA` si `FCFIN` viene a las 00:00 y es del mismo día. Así sale la **hora real** de salida.
  - Actividad «Finalización de la Etapa - …».
  - `WHERE "FCFIN" IS NOT NULL`: solo las etapas ya cerradas.
- **El ID lleva la fecha de inicio**, no la de fin, para emparejar con la entrada.
- **En PnC no tiene `Fase`.** En Natalidad sí se la ponemos, igual que en `NatEtapaIniciada`.
- **SQL:** `natalidad/sql/04_evento_NatEtapaFinalizada.sql`.
- **18/11: `NatEtapaFinalizada` creado y funcionando.**
  - Atributos con los tipos correctos y relaciones *involves one* con `NatEtapas` y `NatExpedientes`.
  - Preview correcto: `Time` con la hora real de salida (de `FCFIN_SISTEMA`).

**Estado de los eventos:** `NatEtapaIniciada` ✅ y `NatEtapaFinalizada` ✅.
- **Siguiente:** los eventos de solicitud y expediente, para la fase 1 de Entrada (registro → alta) y para la resolución.
- **Después:** actividades, hitos, notificaciones y documentos, revisando antes sus catálogos para encontrar la revisión de conformidad y los pasos de terceros.

## 3h4. Búsqueda de eReg (18/11)

- **El buscador de tablas del editor también busca en los nombres de columna.**
- **En PRATLX_RO no hay ninguna tabla de eReg.** Columnas relacionadas con el registro:
  - `GSTA_V_CEL_EXPEDIENTE.FC_SOL_EREG`;
  - `GSTA_V_EXPEDIENTE.FC_EREG`;
  - `GSTA_REGISTRO_ACTIVIDAD.NM_REGISTRO` / `DS_REGISTRO` (por ver: ¿bitácora o registro?);
  - `PNCA_EXPEDIENTE.IT_ENVIADO_ARCH_REG` (de PnC).
- **Columnas de `GSTA_V_EXPEDIENTE`** (otra vista del expediente, 40 columnas). Las que **no** están en la vista CEL:
  - `CD_ACRONIMO`, `DS_CONVOCATORIA` (¿explica AFN1/AFN2?) y `NM_EJERCICIO`;
  - **`CD_SOLICITUD`** (¿número de solicitud o registro? posible enlace con eReg);
  - `FC_PRES`, `FC_SOLICITUD`, `FC_EREG`;
  - **`DIAS_TRAM`** (¿plazo de tramitación o días transcurridos?) y `DIAS_NOTIF`;
  - `N_INTE` (número de interesados);
  - **`EN_INTERVENCION`**;
  - recursos: `EXP_RECURRIDO`, `EXP_REC_ATLX`, `UNIDAD_RECURRIDO`, `ACTO_RECURRIDO`;
  - convocatoria: `FC_INI_PRESENT_SOL` / `FC_FIN_PRESENT_SOL`, órdenes estatal y de la CM;
  - `GESTOR_ASIGNADO`, `ID_ORGA`, `ID_ORGA_GESTION`;
  - `OBSERVACIONES`: texto libre, puede llevar datos personales, **no usar**.
  - Claves: `CD_EXPEDIENTE`, `CD_APLICACION` (no tiene procedimiento: se filtra con `IN` sobre la vista CEL).
- **Sin canal ni tipo de solicitud.**
- **Comprobación:** `natalidad/sql/00b_comprobar_GSTA_V_EXPEDIENTE.sql`.
- **Resultado (18/11), 3163 por convocatoria:**

  | Código | Convocatoria | Expedientes | Con `CD_SOLICITUD` |
  |---|---|---|---|
  | AFN1 | Ayudas Fomento Natalidad 2022 | 7.189 | 7.066 |
  | AFN2 | Ayudas Fomento Natalidad 2023 | 10.388 | 10.294 |
  | AFN1 | Ayudas Fomento de la Natalidad 2024 | 9.455 | 9.406 |
  | AFN1 | Ayudas Fomento de la Natalidad 2025 | 6.631 | 6.587 |
  | AFN1 | Ayudas Fomento Natalidad 2026 | 19.712 | 19.620 |

  - **AFN1 / AFN2 no son tipos de ayuda:** hay **una convocatoria por año**, y el año está en `DS_CONVOCATORIA` y `NM_EJERCICIO_CONV`. El código se repite entre años. La suma, 53.375, cuadra con el total del 3163.
  - **`CD_SOLICITUD`** está en el 99 % de los expedientes. Es la candidata a **clave para unir con eReg**: hay que confirmar qué es.
  - **`DIAS_TRAM` va de 0 a unos 600:** son **días transcurridos**, no el plazo normativo. El plazo lo tiene que dar la unidad.
  - **`DIAS_NOTIF`** está siempre vacío.
  - **`N_INTE`** va de 0 a 3 (número de interesados del expediente).
  - **2026 tiene casi el triple que 2025:** ¿cambio de convocatoria, de criterio de alta o incluye otros expedientes? Preguntar.

## 3h5. Bitácora y columnas que faltaban (18/11)

- **`GSTA_REGISTRO_ACTIVIDAD` = la bitácora de Atlantix.** Columnas:
  - `NM_REGISTRO`: número de la anotación, no es eReg.
  - **`DS_REGISTRO`**: qué actividad es.
  - `CD_EXPEDIENTE`.
  - `CD_USUARIO`: login, **dato sensible, no sacar**.
  - **`FC_REALIZACION`**: cuándo.
  - **`ID_ETAPA_TRAM`**: en qué etapa.
  - **`ID_ENVIO`**: ¿lote de envío a la Intervención?
  - **`IT_AUTOMATICO`**: si es manual o automática.
  - `IT_SINGULAR`, `ID_ORGA_GESTION`.
  - **Sirve para:** días sin actuación (última `FC_REALIZACION`), actividades del explorador y, quizá, la revisión de conformidad y los pasos de terceros. Catálogo en `natalidad/sql/00c_catalogo_bitacora.sql`.
- **`GSTA_V_CEL_EXPEDIENTE` tiene `REF_SOLICITUD`**, que no está en `NatExpedientes`. ¿Es la referencia o el número de registro de la solicitud? Junto con `CD_SOLICITUD` de `GSTA_V_EXPEDIENTE`, es candidata a unir con eReg.
- **Prueba de que existen tablas propias por aplicación:** `PNCA_EXPEDIENTE` (de PnC) tiene `IT_TIPO_SOLICITUD`, `CD_MES_PRIM_NOMINA` / `CD_ANO_PRIM_NOMINA`, `CD_MES_ULT_NOMINA` / `CD_ANO_ULT_NOMINA`, `NM_CUANTIA_MES`, `FC_EFECTO`, `ID_SITU_EXPE`, `ID_MOTIVO_ARCHIVO`…
  - Es justo lo que le falta a Natalidad: tipo de solicitud, mes de nómina, cuantía, fecha de efectos, bajas.
  - **Hay que pedir a Roberto** las tablas equivalentes de la aplicación de Natalidad (`D032` / AFN) en Atlantix.

## 3h6. Catálogo de la bitácora del 3163 (18/11, las 80 más frecuentes)

- **`DS_REGISTRO` es un texto de catálogo** («Finalización de la Etapa - X», «Informado el hito Y en la etapa Z»…), no texto libre. **`IT_AUTOMATICO` es siempre N**, así que no sirve para separar manual y automático.
- **Lo que hay** (veces / expedientes):
  - **Etapas:**
    - «Finalización de la Etapa - …» de todas las etapas.
    - **«Anulación de la Etapa - …»**: REQUERIMIENTO 26.944 / 25.400; PROPUESTA FAVORABLE 7.360 / 6.234; VALIDACIÓN TERCERO 7.309 / 6.200; PTE. ENVÍO INTERVENCIÓN 3.480 / 3.200; RESOLUCIÓN DENEGACIÓN 1.747 / 1.419; RESOLUCIÓN DESESTIMIENTO 225; PTE.ENVÍO MODIF. SIN REPERC. 273.
  - **Hitos** («Informado el hito …»):
    - Requerimiento Documentación (26.878 / 25.213);
    - CONCESIÓN APROBADA (20.703);
    - Resolución Favorable (9.991);
    - Resolución Desfavorable en DENEGACIÓN (8.635) y en DESESTIMIENTO (1.640 + 1.465);
    - INCIDENCIA APROBADA (3.298);
    - Instrucción en GESTIÓN EXPEDIENTE (2.946).
  - **Envío a la Intervención:** «Envio a Intervencion. Generado indice documental» (42.405 / 38.352), con fecha. ¿`ID_ENVIO` es el lote?
  - **Cambio de unidad de gestión:** a la Sección de Natalidad (233.094 + 95.859 veces) y a la Intervención Delegada FJAS (27.070) o FJPS (15.336). Sirve para ver las idas y vueltas a la Intervención.
  - **Documentos requeridos** («Añadido / Eliminado documento requerido … en/de Revisión administrativa»):
    - qué documentación se pide: libro de familia o certificado de nacimiento, empadronamiento de 10 años, IRPF, titularidad bancaria, DNI/NIE, informe médico de la semana 21 de gestación, Anexos 2, 3 y 4…;
    - y «Adjuntado fichero a documento requerido».
  - **Consultas ICDA** (interoperabilidad): datos de nacimiento, identidad e IRPF, con sus errores.
  - **Cambio de convocatoria:** «Se ha cambiado el expediente a la convocatoria AFN1 - 2026» (4.536) y 2025 (2.775). **Explica en parte el salto de 2026.**
  - Situación de Expedientes (ciudadano): estado Vivo y baja.
- **⚠ Hallazgo clave: `GSTA_V_CEL_ETAPA` solo trae las etapas NO anuladas.**
  - REQUERIMIENTO: la vista de etapas tiene 6.001 expedientes, pero la bitácora tiene 25.400 con la etapa anulada y unos 25.200 con el hito de requerimiento.
  - PROPUESTA FAVORABLE: 38.368 en la vista frente a 6.234 anuladas.
  - **Consecuencia:**
    - **los requerimientos y los reprocesos** («propuesta deshecha: vuelta a Gestión», del mockup) **hay que sacarlos de la bitácora**: anulaciones de etapa y hitos;
    - con solo los eventos de etapa se quedarían muy cortos.
  - **Preguntar a la unidad:** ¿un requerimiento normal acaba con «Anulación de la Etapa REQUERIMIENTO»?
- **No aparece** (entre las 80 más frecuentes) nada de «revisión de conformidad» ni de «fichero de terceros / Nexus». Se puede buscar con `LIKE '%CONFORMIDAD%'`, `'%TERCERO%'` o `'%REVIS%'`. Otra posibilidad es que la revisión sea la «Revisión administrativa» de los documentos requeridos.
- **Eventos nuevos que salen de aquí** (sobre `GSTA_REGISTRO_ACTIVIDAD`):
  - Anulación de etapa (reprocesos);
  - Hitos;
  - Envío a la Intervención (con lote);
  - Documento requerido añadido (requerimientos);
  - Cambio de convocatoria;
  - Última actuación (días sin actuación).
  - **Antes de crearlos:** ver cómo están hechos los eventos de actividad de PnC.

## 3h7. `PnCExpedienteResuelto` (18/11)

- **`Time`** = `FCRESOLUCION` del expediente; si no hay, la **fecha de generación del documento de resolución** (`GSTA_V_CEL_DOC_ELABORADA.FCGENERACION`).
  - El documento elegido es el primero (`ROW_NUMBER` por `FCGENERACION`) entre las **plantillas de resolución de PnC**: 96255 Aprobada, 96336 Denegatoria, 96333 Abono de impagados, 96353, 96358, 96269.
- **Atributos:**
  - `FechaResolucionExpediente`;
  - `FechaGeneracionResolucion`;
  - **`FechaFirmaRechazoResolucion`** (`FCFIRMARECHAZO`: **firma real**, con hora);
  - `OrigenFecha`;
  - **`SentidoResolucion`** (Denegatoria si la plantilla es 96336 o 96358; si no, Aprobatoria);
  - `CodigoPlantilla`, `DescripcionPlantilla`, `EstadoDocumento` (`ITESTADO`, F = firmado).
- **Columnas de `GSTA_V_CEL_DOC_ELABORADA`:** `CDEXPEDIENTE`, `FCGENERACION`, `FCFIRMARECHAZO`, `CDPLANTILLA`, `DSPLANTILLA`, `ITESTADO`…
- **Para Natalidad hacen falta sus plantillas:** catálogo en `natalidad/sql/00d_catalogo_doc_elaborada.sql`.
  - Con ellas: sentido de la resolución (favorable, denegación o desistimiento), **fecha de firma** («resolución firmada» del mockup) y, quizá, los documentos de requerimiento.

## 3h8. Plantillas de documentos elaborados del 3163 (18/11)

- **Los códigos de plantilla (`CDPLANTILLA`) cambian en cada convocatoria**, pero los **nombres** se mantienen, con un número delante. Por eso se clasifica por **nombre** con `UPPER(...) LIKE`.
- **Tipos de plantilla** (expedientes aproximados, sumando todos los códigos):
  - **01- Notificación Requerimiento documentación** ≈ 30.900. Las de 2022 (35024) casi nunca están firmadas.
  - **06- Notificación Resolución Favorable Concesión** (y la 05 «exped. individual» y «Notificación de Resolución Favorable») ≈ 32.200. La resolución favorable parece **colectiva**, y lo individual es la notificación.
  - **02- Resolución Denegatoria por Incumplimiento de Requisitos** ≈ 9.140 (la etapa RESOLUCIÓN DENEGACIÓN tiene 9.232 ✔).
  - **03- Resolución Desestimiento** ≈ 2.990 (la etapa tiene 2.989 ✔).
  - **16 - Notificación Modificación datos de la Ayuda** ≈ 3.560.
  - **14- Notificación Baja** ≈ 190.
  - **18 / 19 - Acuerdo / Resolución de procedimiento de Reintegro** ≈ 60.
  - **Informe RR** (recursos de reposición: incumplimiento, desistimiento, estimatoria, baja…) ≈ 120.
  - «07 -____» es una plantilla en blanco, sin firmar: se ignora.
- **`NatExpedienteResuelto`** (`natalidad/sql/07_evento_NatExpedienteResuelto.sql`):
  - plantillas favorable, denegatoria y desistimiento, sin los Informe RR;
  - **`Time` = firma (si `ITESTADO = 'F'`) > generación > `FCRESOLUCION`**;
  - `SentidoResolucion` = Favorable / Denegación / Desistimiento / Sin documento.
  - Unos 2.600 favorables (por etapa) no tienen documento: se quedan con `FCRESOLUCION`.
- **18/11: `NatExpedienteResuelto` creado y funcionando** (11 atributos, relación con `NatExpedientes`). El Preview cuadra: sentido Favorable / Denegación / Desistimiento y `Time` con la hora de la firma.
- **⚠ Duda de fechas para la unidad:**
  - **Favorables:** `FCRESOLUCION` (00:00, por lotes, por ejemplo 16/03/2026) va **antes** que la firma de la «06- Notificación» (por ejemplo 16/04/2026). Parece que la resolución favorable es **colectiva** (`FCRESOLUCION`) y la notificación individual llega en torno a un mes después.
  - **Denegaciones y desistimientos:** `FCRESOLUCION` lleva hora y va semanas o meses antes de la firma del documento.
  - **Pregunta:** ¿qué fecha cuenta como «resolución» para el plazo, la de `FCRESOLUCION` o la firma del documento? De momento, `Time` = firma. `FechaResolucionExpediente` queda guardada para poder cambiarlo.
  - **2022:** las notificaciones favorables (plantilla 35027) no están firmadas en Atlantix, así que se usa la fecha de generación (00:00).
- **Otros usos de estas plantillas:**
  - **01** → evento de requerimiento (con firma);
  - **16** → modificación;
  - **14** → baja;
  - **18 / 19** → reintegro;
  - **Informe RR** → recursos.

## 3h9. `PNCActividadRealizada` → `NatActividadRealizada` (18/11)

- **PnC usa `GSTA_V_CEL_ACTIVIDAD`**, no `GSTA_REGISTRO_ACTIVIDAD`. Columnas:
  - `CDEXPEDIENTE`;
  - `ORDEN` (número de la anotación dentro del expediente);
  - `IDETAPA`;
  - `FCACTIVIDAD`;
  - `ITAUTOMATICA`;
  - `USUARIO` (login: **sensible**);
  - `DSACTIVIDAD` (texto, **puede llevar DNI y nombres**).
- **SQL de PnC:**
  - `ID = 'ActividadRealizada_' + expediente + ORDEN`;
  - relaciones con la etapa (`'Etapa_' + IDETAPA + expediente`) y con el expediente;
  - **CASE con `LIKE`** que agrupa `DSACTIVIDAD` en unas 40 clases;
  - excluye «Finalización de la Etapa» (ya en el evento) y los errores labelsMessage.
  - Añade el perfil del usuario con tablas `PNCA_` (gestor, especialidad, jefe de sección).
- **Versión Natalidad** (`natalidad/sql/09_evento_NatActividadRealizada.sql`):
  - **sin usuarios**: el mockup no mide por persona, las tablas de gestores son de PnC y los logins son sensibles;
  - clases propias: Anulación de Etapa, cambio de unidad a o desde la Intervención Delegada, documento requerido añadido o eliminado;
  - excluye también la apertura y la anulación del expediente, que ya son eventos.
- **`DescripcionActividad` no debe mostrarse en las vistas** (DNI, nombres).
- **18/11: `NatActividadRealizada` creado y funcionando.**
  - La clasificación funciona: Anulación de Etapa, Anulación de Hito, hitos con su texto, Envío a Intervención, cambio de unidad a la Intervención o a la Sección, documento requerido añadido o eliminado, notificación, acuse, ICDA, firma…
  - `IdEtapa` viene casi siempre vacío, así que la relación con `NatEtapas` solo existe en unas pocas anotaciones. Es normal.
  - **`DescripcionActividad` contiene DNI y nombres de firmantes:** no pegarla ni mostrarla.
- **Se ve en la muestra:**
  - **El envío a la Intervención** se graba junto con el «Cambio de unidad: Intervención Delegada», en el mismo segundo.
  - **El requerimiento** sigue la secuencia: genera «01- Notificación Requerimiento» → firma → notificación telemática → acuse.
  - **La resolución favorable** aparece como hito con hora 00:00, por lotes.

## 3h10. Notificaciones: `PnCNotificaciones` → `NatNotificaciones` (18/11)

- **`GSTA_V_CEL_NOTIFICACION`:** `CDEXPEDIENTE`, `CDNOTIFICACION`, `TITULO`, `FCNOTIFICACION` (envío o puesta a disposición), `FCACUSE` (acceso o acuse; a veces a las 00:00, ¿papel o postal?).
- **PnC:** un evento por notificación con acuse; `Time` = `FCACUSE`; `ROW_NUMBER` por expediente y notificación.
- **Natalidad** (`natalidad/sql/10_evento_NatNotificaciones.sql`):
  - **todas** las notificaciones, `Time` = `FCNOTIFICACION`, con `Fecha Acuse` y `ConAcuse` como atributos. Así se calcula el **plazo del requerimiento** y se ven las que no tienen acuse.
  - `TipoNotificacion` sale del título: Requerimiento / Resolución favorable / Denegación / Desistimiento / Modificación / Baja / Reintegro / Otra.
  - El acuse como actividad ya está en `NatActividadRealizada`.
- **Catálogo de títulos (18/11, el número de expediente se quita con `SUBSTRING(TITULO FROM 24)`):**
  - **Requerimientos** («REQUERIMIENTO», «REQUERIMIENTO DE DOCUMENTACIÓN», «AEN REQUERIMIENTO …»): unas 20.000 notificaciones, con acuse alrededor del 85 %.
  - **Resoluciones con el sentido en el título:** «AEN RESOLUCION FAVORABLE(S) / FAV <MES> <AÑO>», «AEN RESOLUCION DESISTIMIENTO».
  - **Resoluciones sin sentido en el título:** «RESOLUCIÓN», «RESOLUCIÓN 2022», «AEN RESOLUCIÓN MARZO 2023», «RESOLUCION D.».
  - **Las favorables van por lotes mensuales:** el título lleva el mes y el año. Confirma que la resolución favorable es **colectiva y mensual**.
  - «AEN» parece el prefijo del procedimiento (¿Ayudas Económicas Natalidad?).

## 3h11. Interesados (18/11)

- **`PnCInteresados`:**
  - sale de `GSTA_V_INTERESADOS` (genérica);
  - edad en la fecha de presentación (`YEAR`, `MONTH` y `DAYOFMONTH`, válida entre 16 y 110);
  - residencia y notificación (provincia y municipio), medio de notificación, `IT_PRINCIPAL`;
  - **la nacionalidad sale de `PNCA_INTERESADO` + `SUCA_PAIS`**, que es de PnC.
- **Columnas de `GSTA_V_INTERESADOS`:**
  - **Útiles:** `CD_INTERESADO`, `CD_EXPEDIENTE`, `TIPO`, `DS_TIPO_DOCUMENTO`, `GRUPO_INTE`, `REPRESENTADO`, `FC_NACIMIENTO` (solo para calcular la edad), `CD_MEDIO_NOTIF` / `DS_MEDIO_NOTIF`, `CDPAIS_RESID`, `CDPROV_RESID` / `DSPROV_RESID`, `CDMUNI_RESID` / `DSMUNI_RESID`, `IT_PRINCIPAL`.
  - **No usar (identifican a la persona):** `DS_CIF` (número de documento), nombre y apellidos, teléfonos, email, todo el domicilio (vía, número, portal, piso, puerta, código postal).
  - **No hay nacionalidad ni país de nacimiento.** Aproximación posible: **tipo de documento** (DNI → española; NIE o pasaporte → extranjera). Confirmarlo con la unidad. La nacionalidad real tiene que venir de la tabla propia de Natalidad.
- **Catálogo de tipos:** `natalidad/sql/00f_catalogo_interesados.sql`.
- **Tipos en el 3163** (recuentos del 18/11):
  - Interesado / principal S: NIF 40.845, NIE 12.462, Otros 52, Pasaporte 4. Son unos 53.360, uno por expediente: **la solicitante**.
  - Representantes: unos 2.200 (NIF, CIF, NIE).
  - Interesados no principales: unos 300.
  - `GRUPO_INTE` está siempre vacío.
- **Aproximación por documento:** unas **23 % de las solicitantes tienen NIE** (extranjeras), según el documento.
- **18/11: `NatInteresados` creado y funcionando.**
  - **Pero `FC_NACIMIENTO` casi no está informada en Natalidad.** Solicitantes con fecha: 2022 7 %, 2023 6 %, 2024 22 %, 2025 26 %, 2026 32 % (en total, alrededor del 21 %).
  - **La edad no sirve para la composición:** pasa a la lista de datos que hay que pedir. `TramoEdad` se queda, con «No informado».
- **`NatInteresados`** (`natalidad/sql/11_objeto_NatInteresados.sql`):
  - `EsSolicitante`, `TipoInteresado`, `TipoDocumento`, `NacionalidadAprox`;
  - `TramoEdad` (menos de 20, 20-24, 25-29, 30-34, 35-39, 40 o más);
  - `MedioNotificacion`, provincia y municipio de residencia;
  - relación 1 — N con `NatExpedientes`.

## 3h12. Búsqueda de revisión de conformidad y terceros (18/11)

Consulta: `natalidad/sql/00h_buscar_revision_terceros.sql`.

- **No hay** anotaciones de «revisión de conformidad», ni de fichero de terceros a gestión económica, ni de tercero creado o rechazado en Nexus.
- **Solo aparecen:**
  - las etapas PROPUESTA FAVORABLE y VALIDACIÓN TERCERO (fin y anulación);
  - el hito «Instrucción» en GESTIÓN EXPEDIENTE (2.651 expedientes).
- **Documentos elaborados a mano** con el mes de nómina en el título (pagos únicos, modificaciones positivas o negativas, bajas, resolución favorable de nómina…). Son pocos, de texto libre, llevan el nombre del gestor y **no sirven para medir**.
- **Decisión:** la revisión de conformidad (fecha y marca), el mes de nómina propuesto y los pasos de terceros en Nexus **se piden a la unidad, a Atlantix (tabla propia) o a Nexus**. No se siguen buscando en la bitácora.

## 3h13. `NatExpedientes` completado (bloque F, 18/11)

- **Atributos nuevos:** `ReferenciaSolicitud` (`REF_SOLICITUD`), `CodigoSolicitud` (`CD_SOLICITUD` de `GSTA_V_EXPEDIENTE`) y `Convocatoria` (`DS_CONVOCATORIA`).
- **`ReferenciaSolicitud` = `CodigoSolicitud`** y tienen formato de **número de registro de eReg** (`NN/NNNNNN.N/AA`). **Es la clave para unir con eReg** cuando lleguen sus datos. Es un dato sensible: no copiarlo fuera de Celonis.
- **El salto de 2026, explicado en parte:** muchas solicitudes **presentadas en 2025** tienen convocatoria **2026**. Encaja con la bitácora («Se ha cambiado el expediente a la convocatoria AFN1 - 2026», unos 4.500).
  - Para comparar años, usar el **año de presentación**, no el de la convocatoria.

## 3h14. Test changes (18/11): no se lanzó

- La ventana pide:
  - un **Target**: «Development (Currently deployed: Draft)»;
  - la casilla «Execute Data Job after deployment»;
  - y **elegir perspectivas**. Solo hay «Name» y «DMPensionesNoContributiva» (la de PnC); **no hay perspectiva de Natalidad**.
- El botón dice **Deploy**: despliega el borrador en el entorno de desarrollo, que es compartido, y ejecuta el data job.
- **Decisión: Cancel.**
  1. Primero se crea la **perspectiva de Natalidad** (borrador).
  2. Después se lanza el Test changes **con Roberto**, para no afectar a PnC ni a Dependencia.

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

## 5. El cuadro en Studio (23/11)

Lo construido y su PQL está en `MAPA_DATOS_CUADRO_NATALIDAD.md`, sección 7. Aquí, lo aprendido del editor.

**Montaje**
- **Para crear la View hace falta un KM.** El formulario *Create View* pide un Knowledge Model existente.
  - En Dependencia ya existía cuando se creó el paquete.
  - Aquí hubo que crear antes **«Natalidad KM»** y una variable de paquete (Package Settings → Variables → Perspective) que apunta a `test:perspective_custom_Natalidad`.
- **Variables de la View:** icono *Variables* de la barra del editor → **VIEW** → «+» → nombre, tipo (*Number*) y valor por defecto. En el PQL se usan como `${plazo_dias}`.
- **Filtros guardados en el KM:** pestaña *Filters* del KM → *Create Knowledge* → *Filter*.
  - Se escriben en PQL: `FILTER …;`.
  - **Global Filter apagado.** Encendido se aplicaría a todo el KM.
  - En un componente se usan con el embudo de *Data* → *Add Filter* → *Saved filters*.
  - Es la única forma de filtrar por algo calculado, como la fecha de resolución.
- **Attribute filter de un componente:** marcar un valor lo **incluye**. Para quitar los vacíos hay que marcar todos los demás valores. La lista queda fija.

**PQL**
- **`RUNNING_TOTAL(agregación)`** funciona para acumulados por mes, por ejemplo el stock.
- **Gráficos con dos fechas** (altas y resoluciones en el mismo eje): usar el **event log** como tabla común. Cada métrica cuenta su tipo de evento. La primera resolución se reconoce con `TIMESTAMP = PU_MIN(…)`.
- **«Pendiente de datos»:** con `/* Pendiente de datos: … */` + `AVG(CASE WHEN "o_custom_NatExpedientes"."ID" IS NULL THEN 0.0 END)` el KPI muestra «–». Así queda listo para cambiar solo la fórmula.
- **Filtros y funciones `PU_`.** Las `PU_` (`PU_MIN`, `PU_LAST`…) agregan solo las filas que dejan los filtros. Es el comportamiento documentado de PQL; aquí no se probó, se evitó.
  - Un filtro de **eventos** (p. ej. «solo eventos de las fases 2–5») haría que `RES` no viera los eventos de resolución. Todos parecerían pendientes.
  - Un filtro de **expedientes**, como «Expedientes pendientes», quita expedientes enteros. A los que quedan no les quita eventos, así que no rompe nada.
- **Quitar la categoría «null» de un gráfico sin filtrar:** no hay opción para ocultarla, y sigue saliendo aunque todas sus métricas sean NULL.
  - La solución es un **«cubo»**: la dimensión manda lo sobrante a una categoría que sí se muestra (`ELSE '1. Entrada…'`).
  - Cada métrica excluye esas filas con su propio `CASE`.
- **Dejar vacío un punto de la línea en vez de 0:** `CASE WHEN COUNT(…) = 0 THEN NULL ELSE COUNT(…) END`. `COUNT` nunca da NULL; `AVG` sobre todo NULL, sí.
- Los comentarios `/* … */` también funcionan dentro de métricas y dimensiones de gráficos.

**Componentes**
- **KPI list:** «Add data or drag it here» solo se ve con el componente seleccionado. Cada KPI nuevo baja el siguiente hueco unos 55 px.
- **Column and line:** una métrica de columnas y varias líneas.
- **Grouped column:** varias métricas de columnas.
  - En el engranaje de una métrica → *Data settings* → *Mark type* = *Line* (y *Show on secondary axis*), esa métrica pasa a línea en el eje derecho.
  - Si solo queda una columna más una línea, Studio lo convierte en *Column and line*.
- **Stacked bar:** una dimensión y varias métricas apiladas, una por tramo.
- **Colores:** sección *Coloring*, al final de *Settings*. El círculo junto al nombre de la métrica abre su PQL Editor, no el color.
  - Solo hay tokens de la paleta, sin hex libre: Primary, Secondary, Context, tres Custom, Negative, Warning y Positive.
  - **Context (20) = #464C6A**, el gris pizarra del mockup.
  - El lápiz del final **no es color a medida: es Transparent**.
- **Color mapping** (pestaña del selector de color): colorea por valores de la dimensión.
  - Regla con nombre, categorías con su color y un color para el resto (*Not Mapped*).
  - La leyenda pasa a mostrar las categorías de la regla, no el nombre de la métrica. Se le puede quitar el título con *Show legend title*.
- **Axis settings:** etiquetas de Y, X e Y secundario. Aceptan variables (`${ver_por}`).
- **Data settings de una dimensión:** solo nombre, unidad, formato y PQL. No hay opción para ocultar nulos.

**Filtros y parámetros de pantalla**
- **Filter dropdown:** aplica un **filtro real** a toda la View. Sin nada elegido, muestra el nombre de la dimensión como etiqueta.
- **Input dropdown:** **no filtra**, solo escribe una variable de la View.
  - Con *Manual input → Free text*, cada opción tiene un texto visible y un valor.
  - El «Label» de *Style* es solo un placeholder y desaparece al elegir un valor. Para que se lea qué es, la etiqueta va dentro del texto de cada opción («Plazo: 90 días»).
- **Date range:** filtra por defecto. En *Style* hay selecciones rápidas, uno o dos calendarios y texto del placeholder.
- **Input box:** se puede dejar vacío, y entonces el PQL que use la variable falla. Para números con pocas opciones, mejor un Input dropdown.
- **Button**, interacciones posibles:
  - *Add Action* (Action Flow o correo);
  - *Switch container tabs*;
  - *Open linked view*;
  - *Go to view or URL* (pide una URL fija, que cambia entre entornos);
  - *Update variable* (varias reglas variable = valor);
  - *Open message*.

  **No hay acción «quitar filtros».** El ✕ solo devuelve las variables a su valor inicial.
- **Open linked view → Create view** crea una View nueva en el paquete:
  - mismo KM;
  - se abre como *Modal overlay* o *Side panel*;
  - *Sync view filters*: *Forwards* (de la principal a la nueva), *Both* o *Backwards*;
  - queda oculta en la navegación (ojo tachado).

  Es la forma de tener «otra página» sin URLs fijas.

**Editor**
- **Mover componentes:** con el componente seleccionado sale «Click & drag to arrange components».
  - Arrastrarlo **desde su centro** funciona también en saltos largos (hasta 72 filas), si origen y destino se ven a la vez en pantalla. Antes, subir o bajar el lienzo.
  - Con el asa (⠿) solo iban bien los saltos cortos.
  - La rejilla tiene 36 columnas y filas de 8 px. La posición exacta se lee en el `grid-area` del DOM (`.bp-board__grid .grid-items`).
- **Redimensionar** arrastrando las asas laterales sí funciona, incluso en arrastres largos.
- **Componentes nuevos:** caen centrados en el cursor y estrechan a los vecinos de la fila.
  - El *Text box* nace con 3 filas de alto y se monta sobre lo que haya.
  - Si algo sale mal, el **Undo** de la barra del editor deshace paso a paso.
- **⚠ Ctrl+A con el foco fuera de un campo selecciona todos los componentes del lienzo** («12 Selected»), y lo que se escriba va al lienzo. Para vaciar un campo, triple clic dentro.
- **Campos ya rellenos** (p. ej. el valor de *Update variable*): triple clic antes de escribir, o el texto se suma («MesMes»).
- **En modo lectura el lienzo se estira** al ancho de la ventana, y un desplegable puede salirse de su celda y montarse sobre el vecino. Revisar siempre la View fuera del editor.
- **Vista previa del PQL Editor:** se corta en unas 50 filas.
- **Leer o probar PQL sin teclear:** los editores son Monaco. `window.monaco.editor.getModels()` da el texto de cada uno desde la consola.
  - Para escribir: `editor.executeEdits(…)` dentro de un `setTimeout`. Llamado directo, la consola se quedó colgada.
  - Después, **Ctrl+Enter** ejecuta la vista previa.
- **PQL Editor de un gráfico:** la vista previa enseña todas las columnas, pero solo se edita la que se abrió. Las métricas («MET») se abren desde su campo.
  - ⚠ El ⋮ de cada cabecera tiene «Remove Column».
- **Tras un apagado:** la View puede abrir en «Read only Mode! This View is already opened in a different tab». Se arregla con *Exit Edit mode* y volviendo a `/edit`, o cerrando las otras pestañas de Celonis.
- **`scrollIntoView` desde la consola mueve la página entera** (`.ce-burger-content__body-container`) y el lienzo desaparece. Se arregla volviendo su `scrollTop` a 0.
- En modo lectura sale a veces una **encuesta de Celonis** abajo a la derecha. Se cierra con la ✕, sin contestar.

**Hallazgos de datos (preguntas para la unidad):** MAPA, sección 7.
