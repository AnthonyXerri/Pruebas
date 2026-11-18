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
    WHERE e."CDAPLICACION" = 'D032'        -- código de Natalidad (por confirmar)
)
SELECT ...
FROM "<tabla del objeto o evento>" t
INNER JOIN exp_nat n                       -- INNER: solo las filas de expedientes de Natalidad
        ON n."CDEXPEDIENTE" = t."CDEXPEDIENTE"
```

- **`INNER JOIN`:** deja solo las filas que casan con la lista. Con este patrón **no hace falta** repetir el filtro en el `WHERE`.
- **`LEFT JOIN`:** deja todas las filas de la tabla base y deja vacías las que no casan. Si se usa `LEFT JOIN` con la tabla de expedientes, el filtro `C_APLICACION = …` va en el `WHERE`.
- Si una tabla no tiene `C_EXPEDIENTE` (por ejemplo, documentos que cuelgan de una etapa), se llega a él a través de la tabla que sí lo tenga.

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

  - **Pendiente de Roberto o la unidad:** el nombre de cada procedimiento y cuáles entran en el cuadro de Natalidad.
  - **Mientras tanto:** el objeto lleva todos los de `D032`, con `CodigoProcedimiento` como atributo para poder filtrar después.
- **«N columns ignored» en el Preview:** son columnas de la SQL que el objeto aún no tiene declaradas. *Add attributes* abre «Edit attributes», que **no las rellena solo**: se añaden a mano con *+ Add*, con el nombre idéntico al alias de la SQL y su tipo.
- Prefijos de los expedientes de `D032`: AFN, SCP, ANA, GEF. Probablemente corresponden a procedimientos distintos; sirven como pista para saber cuáles son de Natalidad.
- **Truco del editor:** *Preview selection* solo muestra las columnas mapeadas al objeto (el `ID`) y exige que haya columna `ID`. Para ver otras columnas, usar *Execute query selection* o meter la información en el `ID` concatenando con `||`.
- [x] Objeto de Roberto (18/11): **`NatExpedientes`** en «OCPM DataPool VALI…», namespace custom, etiqueta **Natalidad** (Custom Processes), descripción «Expedientes de Natalidad Atlantix». Solo tiene `ID` (PK, String). Los objetos de Atlantix de referencia llevan, probablemente, la etiqueta **«PnC ATL»**.
- [x] `NatExpedientes` (18/11): transformación con `natalidad/sql/01_objeto_NatExpedientes.sql` y 18 atributos declarados a mano (10 String y 8 Datetime). Pendiente de confirmar el Preview sin columnas ignoradas y el Save with Validation.
- [ ] `NatProcedimiento`, `NatEtapa`, `NatDocumento` (y `NatExpediente`): atributos, transformación con el filtro y relaciones.
- [ ] Eventos `Nat…`: todos los de Atlantix, con el mismo filtro.
- [ ] Revisar con Roberto antes de Create version / Deploy.
