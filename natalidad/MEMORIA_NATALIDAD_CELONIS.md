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
    SELECT DISTINCT e."C_EXPEDIENTE"
    FROM "GSTA_BC_EXPEDIENTE" e
    WHERE e."C_APLICACION" = 'D032'        -- código de Natalidad (por confirmar)
)
SELECT ...
FROM "<tabla del objeto o evento>" t
INNER JOIN exp_nat n                       -- INNER: solo las filas de expedientes de Natalidad
        ON n."C_EXPEDIENTE" = t."C_EXPEDIENTE"
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

## 4. Estado y pendientes

- [ ] Confirmar el nombre de la tabla de expedientes, de sus columnas y el código de aplicación de Natalidad.
- [ ] Ver qué objeto creó Roberto (nombre) y completar sus atributos.
- [ ] `NatProcedimiento`, `NatEtapa`, `NatDocumento` (y `NatExpediente`): atributos, transformación con el filtro y relaciones.
- [ ] Eventos `Nat…`: todos los de Atlantix, con el mismo filtro.
- [ ] Revisar con Roberto antes de Create version / Deploy.
