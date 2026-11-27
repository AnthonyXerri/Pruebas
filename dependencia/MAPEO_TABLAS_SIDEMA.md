# Mapeo de las tablas de SIDEMA · Dependencia (CU1 y CU2)

24/11/2026. Revisadas las 29 tablas de la extracción «Extraccion Dependencia» (data job «Dependencia VASOCIAL_SIDM», pool «OCPM DataPool IMPLEMENTACION»), que son las mismas que crea el script `VistasSIDMPRODv1`:
- 27 tablas de `DBA_SIDM`;
- 2 de `DBA_SUCA`.

Fuentes, sin guardar nada en Celonis:
- **Configure columns**, para los nombres y tipos;
- **Extraction Preview**, para ver qué contiene cada columna (100 filas del entorno de validación);
- **diálogo «Add Table»** (sin añadir nada), para buscar por nombre qué más tablas hay en el origen (sección 4).

Mockups revisados elemento a elemento:
- `mockups/MockupCU1_v2.html` (CU1, sección 5);
- `mockups/MockupCU2.html` (CU2, sección 6).

Los datos de validación son de prueba y antiguos (2007–2015 casi todos), así que hay columnas vacías en la muestra que pueden venir rellenas en producción.

Resultado: **`dependencia/sql/VistasSIDMPRODv3.sql`**, con 4 bloques:
1. las 29 vistas con lista de columnas;
2. 28 catálogos nuevos;
3. una consulta al diccionario para ver las columnas de las tablas del CU2;
4. una comprobación final.

Los nombres de columna del bloque 1 se han comparado uno a uno con SIDEMA. El generador está en `dependencia/sql/generador/`.

Notación: «I» entero, «S» texto, «D» fecha. Los códigos `CD*` son texto con ceros a la izquierda: se comparan entre comillas (`'01'`).

## 1. Estado de la extracción

**Todas las ejecuciones del job han fallado** (la última, el 20/11). Falla al empezar la primera tabla con este error:

`java.lang.NoClassDefFoundError: Could not initialize class org.xerial.snappy.Snappy`

- Es el mismo error de noviembre. Está en el extractor (conexión «Uplinked», extractor v4.1.3), no en las tablas, así que cambiar las vistas no lo arregla.
- La vista previa sí funciona.
- **Pista para Javier Olmeda (sin comprobar):** este error suele salir cuando la JVM del extractor no puede cargar la librería nativa de Snappy, por ejemplo si su carpeta temporal no permite ejecutar. Se suele arreglar dándole otra carpeta (`-Dorg.xerial.snappy.tempdir=…`) o actualizando el extractor.

Otros puntos de la extracción:
- **Avisos «potential issues»:** hay uno por tabla y todos dicen lo mismo: sin filtro de fecha de cambio, la tabla no puede cargarse en *delta*. Solo importa si se pasa a carga delta.
- **`SIDM_MR_RESOLUCIONES`:** su vista previa no termina, porque guarda el PDF de cada resolución en `DSCONTENIDOFICHERO`. `SIDM_MR_TIPOS_DOCUMENTOS` (`PLANTILLA`) y `SIDM_DICTAMEN_TECNICO` (`LOB_*`) también llevan ficheros. Las vistas los dejan fuera.
- **Filtros de la extracción (27/11):** el *Filter Statement* es Oracle sin funciones (`UPPER`, `TRIM` o `TO_DATE` dan «Error parsing filter»). Las fechas van como texto en formato `DD-MON-RR`: `FCALTA >= '01-JAN-25'`.
- **Cuando la extracción lea las vistas,** las tablas se llamarán `SIDM_V_DEP_*`. Hay que marcar «Rename target table» con el nombre de siempre (`SIDM_SOLICITUD`…) para no tocar las SQL de Objects & Events.

## 2. Claves de unión

| Desde | Hacia | Columnas |
|---|---|---|
| `SIDM_SOLICITUD` | `SIDM_HIST_ESTADO`, `SIDM_DICTAMEN`, `SIDM_DICTAMEN_TECNICO`, `SIDM_MR_RESOLUCIONES`, `SIDM_SUBSANACION_DOCUMENTACION`, `SIDM_VALORACION_BVD`, `SIDM_VALORACION_EVE` | `IDSOLICITUD` (I) |
| `SIDM_SOLICITUD` | `SIDM_RI_PIA`, `SIDM_RI_SOL_REVISION_PIA`, `SIDM_RI_TRASLADO_IN`, `SIDM_RI_TRASLADO_OUT`, `SIDM_RI_URGENCIA` | `IDSOLICITUD` = `ID_SOLICITUD` (I) |
| `SIDM_SOLICITUD` | `SIDM_SOLICITANTE` | `IDSOLICITANTE` (I) |
| `SIDM_SOLICITUD` | `SIDM_BANDEJA_RECEPCIONADOS` | `NMREFERENCIA` (S, 11 cifras) |
| `SIDM_SOLICITUD` | `SIDM_RI_CE_GENERAL` | `NMSOLICITUD` = `NM_SOLICITUD` (S, año + 6 cifras) y `NM_REVISION` |
| `SIDM_RI_PIA` | `SIDM_RI_TRAMITES`, `SIDM_RI_LLAMADA`, `SIDM_RI_SUBS_PIA` | `ID_PIA` (I) |
| `SIDM_RI_PIA` | `SIDM_RI_SOL_REVISION_PIA` | `ID_PIA` = `ID_PIA_REVISADO` |
| `SIDM_VALORACION_BVD/EVE`, `SIDM_DICTAMEN_TECNICO` | `SIDM_DATOS_VALORADOR` | `CDVALORADOR` (S) |
| `SIDM_SOLICITANTE`, `SIDM_DATOS_VALORADOR`, `SIDM_RI_URGENCIA` | `SUCA_MUNICIPIO` | `CDPROV` + `CDMUNI` (S) |

**Catálogos:**

| Columna en la tabla | Catálogo |
|---|---|
| `CDESTADO` | `SIDM_ESTADO_SOLICITUD` |
| `CDMOTALTA` | `SIDM_MOTALTA` |
| `CD_BANDEJA` | `SIDM_CAT_BANDEJA_EREG` |
| `CDTIPODOCUMENTO` | `SIDM_MR_TIPOS_DOCUMENTOS` |
| `CD_ESTADO_PIA` | `SIDM_RI_ESTADOS_PIA` |
| `CD_TPPIA` | `SIDM_RI_TPPIA` |
| `CD_TPPIA_TRANS` | `SIDM_RI_TPPIA_TRANS` |
| `CDPROV` | `SUCA_PROVINCIA` |
| Resto | Ver los catálogos nuevos (sección 4) |

**Ojo con los tipos y los formatos:**
- En este origen, `IDSOLICITUD` es entero en todas las tablas. El objeto de Objects & Events usa `CAST(IDSOLICITUD AS VARCHAR)` como `ID`; los eventos nuevos tienen que hacer lo mismo para enlazar.
- `CDGRADO` es entero en `SIDM_DICTAMEN` y texto en `SIDM_DICTAMEN_TECNICO`. Al compararlos hay que convertir uno de los dos.
- `CDMUNI` viene a veces sin los ceros de la izquierda (`'79'` frente a `'079'`, en `SIDM_DATOS_VALORADOR`). Antes de cruzar con SUCA hay que normalizarlo con `LPAD(CDMUNI, 3, '0')`.
- En validación, `SIDM_ESTADO_SOLICITUD` tiene los códigos de **2 cifras** (la copia local tenía de 4). Además, `CDESTADO_GEST_VAL` viene relleno en una parte de los estados. La regla `RIGHT(…, 2)` de las SQL de noviembre sigue valiendo en los dos casos.
- Las puntuaciones del baremo (`NMBAREMO`, `NMBAREMO_COGNITIVO`, `NMBAREMO_FISICO`) son DOUBLE: en Objects & Events, atributos *Floating point*.
- `SUCA_MUNICIPIO` es de toda España. Hace falta así, porque los traslados traen municipios de otras comunidades.

## 3. Tabla por tabla

### CU1 · Fase 1 (grabación)

**`SIDM_SOLICITUD`** · el objeto
- Sin cambios respecto a v1.

**`SIDM_HIST_ESTADO`** · cambios de estado
- Sin cambios respecto a v1.
- Columnas: `IDSOLICITUD`, `CDESTADO`, `FCMODI` y `IDMODI` (login).

**`SIDM_BANDEJA_RECEPCIONADOS`** · registros de entrada por bandeja
- Sirve para las registradas pendientes de grabar.
- Consulta que dio el cliente: `IT_ESTADO = '1'`, `FCBAJA` nula y sin solicitud con el mismo `NMREFERENCIA`.
- **`DSORIGENDOC` = ORVE / Presencial / Internet**: es el «Origen» que pide el mockup.
- Fechas: `FC_RECEPCION`, `FC_ENVIO_UNIDAD` y `FCALTA`.

**`SIDM_CAT_BANDEJA_EREG`** · catálogo de bandejas

| Código | Bandeja |
|---|---|
| INI | Altas iniciales |
| REVRA | Revisión grado |
| REVPIA | Revisión PIA |
| REVCE | Revisión capacidad económica |
| URG | Tramitación urgencia |
| TRASIN | Traslado desde otra CCAA |
| TRASOUT | Traslado a otra CCAA |
| APORT | Aportación |

**`SIDM_MOTALTA`** · motivo de alta
- Valores: Alta ORVE, Alta Simple y Alta con Servicios.
- Complementa a `DSORIGENDOC`.

**`SIDM_SUBSANACION_DOCUMENTACION`** · subsanaciones de la solicitud
- `NMSUBSANACION` es el número de la subsanación (1, 2…).
- `CDESTADO_DOCUMENTACION` es un código; su catálogo probable es `SIDM_ESTADO_SUBSANACION` (sección 4).
- `DSTEXTO_LIBRE` es el motivo, en texto libre.
- `FCINICIOSUBSANACION` y `FCDESISTIMIENTO` vienen vacías en la muestra.
- No tiene fechas de alta ni de modificación.

### CU1 · Fase 2 (valoración y grado)

**`SIDM_VALORACION_BVD`** · valoración BVD
- `FCVALORACION` es la visita.
- `CDVALORADOR` es el valorador.
- **`IT_VALORACION_ONLINE`** indica valoración telemática.
- `FCINICIO_SISTEMA` y `FCFIN_SISTEMA` son la grabación de la valoración. Vienen vacías en la muestra.
- `NMBAREMO_COGNITIVO` y `NMBAREMO_FISICO` son las puntuaciones (entran en v3).
- `NMRANGO_EDAD` es el tramo de edad.

**`SIDM_VALORACION_EVE`** · valoración EVE (menores de 3 años)
- Lo mismo que la BVD, más `NMGRADO_DEPENDENCIA`, `NMRANGO_MESES` y las puntuaciones `NMPUNT_*`.
- **El cuestionario de salud en texto (`CUESTIONARIO`, `NOTAS_*`) queda fuera.**

**`SIDM_DICTAMEN_TECNICO`** · grado propuesto
- Grado: `CDGRADO`, `DSGRADO_NIVEL` y la puntuación `NMBAREMO`.
- Valorador: `CDVALORADOR`.
- **Fecha de comisión:** `FCVALIDACION_COMISION`, más `ACTA_COMISION`. Es el hito ⑧.
- `FCREVISION`.
- **No trae la fecha del dictamen** (hito ⑦): sigue saliendo del histórico de estados.

**`SIDM_DICTAMEN`** · grado reconocido
- Grado y nivel: `CDGRADO`, `CDNIVEL` y `DSGRADO_NIVEL`.
- `CDTIPO_BAREMO` (BVD o EVE).
- **No trae una fecha fiable:** `FCALTA` está casi vacía. La fecha de resolución sale de `SIDM_MR_RESOLUCIONES`.

**`SIDM_MR_RESOLUCIONES`** · resoluciones
- **`FCRESOLUCION`** es el hito ⑨, resolución del grado.
- `CDTIPODOCUMENTO` es el tipo de resolución.
- `FC_ENTRADA_ESCRITO_RENUNCIA`.
- `IT_ELA` marca la vía rápida para ELA (entra en v3).

**`SIDM_MR_TIPOS_DOCUMENTOS`** · catálogo de tipos de resolución
- Resolución por grado y nivel, desestimatoria grado 0, desestimatoria por incumplir requisitos, por desistimiento, por caducidad, por fallecimiento, por renuncia y por traslado.
- Además, revisiones, recurso de alzada y «Sin derecho a PIA».
- Es el filtro «Resolución de grado» del mockup.

**`SIDM_DATOS_VALORADOR`** · valoradores
- Nombre: `NOMBRE_VALORADOR` (entra en v3; el mockup lo muestra).
- Perfil: `CDPERFIL_VALORADOR`, con catálogo `SIDM_PERFIL_VALORADOR` (sección 4).
- Turno: `CDTURNO` (M o T).
- Profesión: `ITMEDICO`, `ITPSICOLOGO`, `ITTRABAJADOR_SOCIAL`…
- Zona: `CDZONADEP`, `CDZONADEP2` y `CDZONADEP3`.
- **`IT_VALORADOR_ENCOMIENDA`** probablemente indica propio o externo (por confirmar).
- **`LOGIN`** sirve para cruzar `CDVALORADOR` con los logins del histórico. Viene vacío en la muestra.

### CU1 · Fase 3 (PIA)

**`SIDM_RI_PIA`** · un registro por PIA
- Estado: `CD_ESTADO_PIA` y `FC_ESTADO`.
- Prestación: `CD_TPPIA` y `CD_TPPIA_TRANS`.
- Resolución: `FCRESOLUCION`, `FCRESOLUCION_PIA`, `IT_PIA_RESUELTO` y `CD_MOT_RESOL`.
- `FC_FIN_PLAZO` y `FC_EFECTOS` (fecha de efectos).
- **`FC_TRAMITE_CONS`** es la consulta al beneficiario, inicio del plazo imputable. Viene vacía en la muestra.
- **`FC_PROPUESTA_TEC`** es la propuesta técnica. Viene vacía en la muestra.
- `CD_GRUPO`, con catálogo probable `SIDM_GRUPO_PIA` o `SIDM_RI_GRUPO`.
- Para el CU2: `IT_ESTADO_WEB_EL` (R o B), `FC_ESTADO_WEB_EL` y `DS_MOT_ESTADO_WEB_EL` (motivo de la baja).

**`SIDM_RI_TRAMITES`** · histórico de estados del PIA
- Son los eventos de la fase 3.
- Fecha: `FCALTA` (`FC_ESTADO_PIA` viene vacía).
- Estado: `CD_ESTADO_PIA`, `CD_GRUPO` y `CD_ESTADO_UDAI`.
- **Técnico:** `IDALTA`.

**`SIDM_RI_ESTADOS_PIA`** · los 12 estados del PIA

| Código | Estado |
|---|---|
| 00 | Inicio del PIA |
| 01 | Pendiente de Informe Social |
| 04 | Pendiente Resolución Fallecimiento |
| 10 | Consulta al beneficiario |
| 20 | Propuesta Técnica PIA |
| 30 | Pendiente validación Coordinador |
| 40 | Pendiente generar Resolución PIA |
| 50 | Requerimiento de Documentación |
| 60 | Capacidad Económica no completa |
| 70 | Enviada notificación AVC PIA |
| 80 | En proceso de modificación PIA |
| 90 | Expediente resuelto |

El orden de los códigos que no salen juntos en la muestra está por confirmar.

**`SIDM_RI_TPPIA`** y **`SIDM_RI_TPPIA_TRANS`** · catálogos de prestaciones
- `CD_AGRUPACION` da el tipo: centro de día, SAD, teleasistencia, residencia, PECEF, PEVS, PEAP, promoción de la autonomía…
- `CD_AGRUPACION2` indica intensivo o no.
- `CD_AGRUPACION3` indica Comunidad o plaza municipal.
- `IT_SAD` e `IT_TA` sirven para el CU2.

**`SIDM_RI_SUBS_PIA`** · requerimientos del PIA
- `NM_SUBSANACION` y `FCALTA`.
- Sirve para el «% con requerimiento».

**`SIDM_RI_LLAMADA`** · llamadas del PIA
- `NM_LLAMADA`, `FC_LLAMADA` e `IDALTA`.
- Sirve para «llamadas por expediente».

**`SIDM_RI_SOL_REVISION_PIA`** · revisiones del PIA
- Si es de parte o de oficio: `IT_TIPO`.
- Si está aprobada o rechazada: `IT_ESTADO`.
- Motivos: `CD_MOT_REVISION`, `CD_MOT_APROB_REV` y `CD_MOT_RECHAZ_REV`, con sus catálogos `SIDM_RI_MOT_*` (sección 4).
- `FC_SOLICITUD_PARTE` y `FC_VALORACION`.

### CU1 · Circuitos especiales

**`SIDM_RI_URGENCIA`** · tramitación por urgencia
- Fechas: `FC_SOLICITUD`, `FC_SUBCOMISION`, `FC_APROBACION` y `FC_RECHAZO`.
- **`CD_MANCO`** es la mancomunidad. Solo aparece aquí; catálogo probable `SIDM_MANCOMUNIDAD`.
- Centro de servicios sociales: `CD_CENTRO_SS`.
- Técnico: `CD_LOGIN_TECNICO`.

**`SIDM_RI_TRASLADO_IN`** y **`SIDM_RI_TRASLADO_OUT`** · traslados entre comunidades
- Comunidad, provincia y municipio de origen o destino.
- Fechas de registro, consolidación y valoración.
- Indicadores de documentación requerida.
- En v3 entran los motivos (texto) y los códigos externos del expediente (IMSERSO u otra comunidad).

### Territorio y persona

**`SIDM_SOLICITANTE`** · la persona
- **Edad:** `FCNACIMIENTO`.
- Sexo: `ITSEXO`.
- En v3 entran nacionalidad (`CDNACION`, `CDNACION_DOS`), estado civil (`CDECIVIL`) y `ITAUT_CONS_DATOS` (autoriza a consultar sus datos, lo que puede explicar menos subsanaciones).
- **Municipio:** `CDPROV` + `CDMUNI`.
- `CDDISTRITO` (Madrid capital) y `CDZONADEP`.
- `FCFALLEC_INE`, fecha de fallecimiento.
- `ITVALORACION_TARDE`, si pide la valoración de tarde.

**`SUCA_MUNICIPIO`** y **`SUCA_PROVINCIA`** · catálogos de territorio
- No tienen mancomunidad ni zona: ver los catálogos `SUCA_*_SER_SOC` (sección 4).

### CU2 · Lista de espera de SAD y Teleasistencia

**`SIDM_RI_CE_GENERAL`** · capacidad económica
- `NM_CAPACIDAD_ECON` y `NM_CAPACIDAD_ECON_RES` sirven para el orden de prelación.
- Estado: `CD_ESTADO_CE`, con catálogo `SIDM_RI_ESTADOS_CE`.
- Fecha de cálculo: `FC_CALCULO_CE`.
- `CD_EXPEDIENTE` es «número/año»; no lleva DNI.

## 4. Lo que hay además en SIDEMA (búsqueda del 24/11, solo nombres)

**Cómo se ha buscado:**
- En la extracción, el diálogo «Add Table» deja buscar tablas del origen por nombre. Se cerró siempre con Cancel, sin añadir nada.
- Del esquema `DBA_SIDM`, el usuario de Celonis solo ve **32 tablas**: las 29 de la extracción y 3 más (`SIDM_AGRUP_PREF_SERV_PREST`, `SIDM_MODALIDADES` y `SIDM_V_CHS_ACTIVADO`).
- El resto aparece solo como **sinónimo público**. Eso quiere decir que existe, pero el usuario de Celonis probablemente no tiene permiso para leerla. Por eso no se pueden ver sus columnas y hace falta que Roberto cree las vistas.

**Catálogos encontrados** (bloque 2 del script, con `SELECT *`):

| Para | Catálogo |
|---|---|
| Citación de la valoración | `SIDM_ESTADO_CITA` |
| Estados de gestión de la valoración (`CDESTADO_GEST_VAL`) | `SIDM_ESTADO_GEST_VAL` |
| Motivo de subsanación (`CDESTADO_DOCUMENTACION`) | `SIDM_ESTADO_SUBSANACION` (por confirmar) |
| Perfil del valorador | `SIDM_PERFIL_VALORADOR` |
| Zona (`CDZONADEP`) | `SIDM_RE_DEMAR_ZONADEP` (por confirmar) |
| Mancomunidad (`CD_MANCO`) | `SIDM_MANCOMUNIDAD` (por confirmar) |
| Territorio de servicios sociales | `SUCA_AREA_SER_SOC`, `SUCA_ZONA_SER_SOC`, `SUCA_DISTRITO_SER_SOC` |
| Distrito de Madrid (`CDDISTRITO`) | `SUCA_DISTRITO` (por confirmar) |
| Grupo del PIA (`CD_GRUPO`) | `SIDM_GRUPO_PIA` o `SIDM_RI_GRUPO` (por confirmar) |
| Motivo de la resolución del PIA (`CD_MOT_RESOL`) | `SIDM_RI_MOT_RESOLUCION` (por confirmar) |
| Revisión del PIA | `SIDM_RI_MOT_REVISION`, `SIDM_RI_MOT_APROB_REV`, `SIDM_RI_MOT_RECHAZ_REV` |
| Urgencia | `SIDM_RI_MOT_APROB_URGENCIA`, `SIDM_RI_MOT_RECHAZO_URGENCIA` |
| Capacidad económica | `SIDM_RI_ESTADOS_CE`, `SIDM_RI_CE_MOTREVISION`, `SIDM_RI_CE_TPMOTREVISION` |
| Estado del envío del traslado | `SIDM_ESTADO_ENVIO` (por confirmar) |
| CU2: estados y bajas del servicio | `SIDM_RI_ESTADOS_SERV`, `SIDM_RI_MOT_BAJA_SERV`, `SIDM_RI_MOT_NOADJUDICA` |
| CU2: incidencias de la lista | `SIDM_LE_TP_INC`, `SIDM_LE_ESTADOINC` |
| CU2: tipo de oficio de la notificación (`CD_TPOFICIO`) | `SIDM_RI_TPOFICIOS` |

**Tablas del CU2 y de la citación** (bloque 3: primero hay que ver sus columnas):
- Lista de espera:
  - `SIDM_V_RI_WEBEL_ALTAS_SAD` y `_TA`;
  - `SIDM_V_RI_WEBEL_BAJAS_SAD` y `_TA`;
  - `SIDM_V_RI_WEBEL_MODI_SAD` y `_TA`.
- Servicio: `SIDM_RI_SAD` y `SIDM_RI_TA`, con su histórico (`SIDM_RI_SAD_HIST`, `SIDM_RI_TA_HIST`). Los históricos dan los eventos de la lista: alta, baja, reingreso.
- Notificación de la resolución del PIA: `SIDM_RI_DOC_GENERADO`.
- Incidencias y bajas de la lista:
  - `SIDM_LE_INCIDENCIAS`;
  - `SIDM_LE_RENUNCIA`;
  - `SIDM_LE_BAJA_ACEPTADA_SAD` y `_TEL`.
- Citación de la valoración: `SIDM_CITAS` y `SIDM_CITA_VALORADOR` (asignación al valorador: «expedientes sin asignar» del mockup).

**Sin encontrar:**
- **Lote** del servicio: no hay ninguna tabla de lotes de SAD o teleasistencia.
- **Usuarios** con nombre, tipo y equipo. Candidatas por el nombre: `SIDM_VM_HSTA_USU_PROFESIONALES` y `SIDM_VM_HSTA_USUARIOS`.
- **Municipio → mancomunidad.** Candidatas: `ECSS_MANCOMUNICIPIOS` y `SIDM_V_MANCOMUNIDADL`.
- **Catálogos** de `CD_ESTADO_UDAI` y `CDMOTBAJA`.

## 5. Mockup CU1, elemento a elemento

✅ sale de las tablas · 🟡 sale, pero falta confirmar algo o depende del bloque 2 o 3 · ❌ no está en SIDEMA.

**Cabecera y vista global**

| Elemento | | Con qué |
|---|---|---|
| Solicitudes activas (fases 1 a 3) | ✅ | Sin `FCRESOLUCION_PIA` ni resolución de cierre |
| Plazo del proceso completo y cumplimiento del plazo legal (180 d) | ✅ | `FCREGENTRADA` → `SIDM_RI_PIA.FCRESOLUCION_PIA` |
| Subplazos por fase frente a su objetivo (30 / 120 / 180) | ✅ | Fases del histórico + `SIDM_RI_TRAMITES` |
| Indicador predictivo (entran frente a resuelven) | ✅ | Eventos |

**Filtros**

| Filtro | | Con qué |
|---|---|---|
| Periodo y objetivo | ✅ | Fechas y variables `${…}` |
| Estado (fases 1 y 2) | ✅ | Histórico de estados |
| Estado (fase 3: propuesta, resolución, PIA resuelto) | ✅ | `SIDM_RI_ESTADOS_PIA`: 00–20, 30–40, 90 |
| Territorio: municipio | ✅ | `SIDM_SOLICITANTE` + `SUCA_MUNICIPIO` |
| Territorio: mancomunidad, metropolitana o periferia | 🟡 | Catálogos del bloque 2 y la relación municipio → mancomunidad (sin encontrar) |
| Edad (EVE < 3, 3–6, 7–10, 11–17, > 18, > 90) | ✅ | `FCSOLICITUD` − `FCNACIMIENTO` |
| Tipo de valoración: presencial o telemática | ✅ | `IT_VALORACION_ONLINE` |
| Tipo de valoración: BVD o EVE | ✅ | Tabla de valoración o `CDTIPO_BAREMO` |
| Tipo de valoración: inicial | ✅ | Solicitud sin revisión (`NMREVISION`, `IDSOLICITUD_ORIG_REVISION`) |
| Origen | 🟡 | `DSORIGENDOC`: Internet → Telemática y ORVE → ORBE. Falta decidir dónde va «Presencial»: el mockup tiene «ORBE / presencial» y «Registro / papel» |
| Tipo de prestación | ✅ | `CD_TPPIA` → `CD_AGRUPACION` |
| Resolución de grado (grado 0, I–III con PIA, desistimiento, denegatoria, caducidad) | ✅ | `CDTIPODOCUMENTO` + `SIDM_MR_TIPOS_DOCUMENTOS` y `CDGRADO` |

**Fase 1 · Grabación**

| Elemento | | Con qué |
|---|---|---|
| Grabadas, en plazo, fuera de plazo, plazo medio y gráfico | ✅ | `FCSOLICITUD` → `FCALTA` (ya montado) |
| Pendientes de grabar (bandeja) | ✅ | `SIDM_BANDEJA_RECEPCIONADOS` |
| Personas involucradas, tabla de trabajadores, carga | ✅ | `IDALTA` (login) |
| Nombre, tipo (subcontrata o adscrito) y territorio del trabajador | ❌ | Tabla de usuarios (sin encontrar) |
| Subsanación: tasa, número, días bloqueado | ✅ | Histórico de estados y `SIDM_SUBSANACION_DOCUMENTACION` |
| Subsanación por motivo | 🟡 | `CDESTADO_DOCUMENTACION` + catálogo (bloque 2) o `DSTEXTO_LIBRE` |
| AVC en bucle e iteraciones | ✅ | Histórico (ya montado) |
| Flujo por atributo: territorio, edad, origen | ✅ | Persona, municipio y `DSORIGENDOC` |
| Equipo de subsanación (login) | ✅ | `IDMODI` en los estados de subsanación |
| % del equipo total, efectivos | ❌ | Los da la unidad |

**Fase 2 · Valoración**

| Elemento | | Con qué |
|---|---|---|
| Valorados (por fecha de dictamen), en plazo y fuera (120 d desde el alta) | 🟡 | Dictamen = entrada en el estado 47 (no hay columna de fecha) |
| Valoradores activos, carga, sobrecargados | ✅ | `CDVALORADOR` en las valoraciones + `SIDM_DATOS_VALORADOR` |
| Expedientes «sin asignar» | 🟡 | `SIDM_CITA_VALORADOR` (bloque 3) |
| Tabla de trabajadores: nombre, zona, canal y criterio | ✅ / 🟡 | `NOMBRE_VALORADOR`; `CDZONADEP` + catálogo (bloque 2); telemática; grado |
| Variabilidad de criterio BVD (G0–G3 por valorador, > 2σ) | ✅ | `SIDM_DICTAMEN_TECNICO.CDGRADO` por `CDVALORADOR` |
| ① Registro · ② Alta | ✅ | `FCREGENTRADA` · `FCALTA` |
| ③ Pendiente de citación · estado de la citación | ✅ | Estados 40, 07 y 42; `SIDM_ESTADO_CITA` (bloque 2) |
| ④ Citación | 🟡 | `SIDM_CITAS` (bloque 3) o entrada en el estado 43 |
| ⑤ Fecha de valoración (visita) | ✅ | `FCVALORACION` |
| ⑥ Grabación de la valoración | 🟡 | `FCFIN_SISTEMA` (vacía en la muestra; por confirmar frente a `FCFIN`) |
| ⑦ Dictamen | 🟡 | Entrada en el estado 47 |
| ⑧ Comisión | ✅ | `FCVALIDACION_COMISION` |
| ⑨ Resolución del grado | ✅ | `SIDM_MR_RESOLUCIONES.FCRESOLUCION` |
| Valoración individual: tramo imputable (visita → grabación → dictamen) | 🟡 | ⑤, ⑥ y ⑦ |

**Fase 3 · PIA**

| Elemento | | Con qué |
|---|---|---|
| PIA resueltos, en plazo y fuera (180 d) | ✅ | `FCRESOLUCION_PIA` |
| Expedientes activos y «en revisión» | ✅ | `SIDM_RI_PIA` y `SIDM_RI_SOL_REVISION_PIA` |
| Técnico (login) y carga | 🟡 | `SIDM_RI_TRAMITES.IDALTA` |
| Rol del técnico: gestión, elaboración o supervisión | 🟡 | Por el estado que registra: 10 consulta = gestión; 20 propuesta = elaboración; 30 y 40 validación y resolución = supervisión (por confirmar) |
| Plazo imputable: consulta al beneficiario → resolución | ✅ | `FC_TRAMITE_CONS` → `FCRESOLUCION_PIA` (o estados 10 → 90) |
| % con requerimiento · llamadas por expediente | ✅ | `SIDM_RI_SUBS_PIA` (o estado 50) · `SIDM_RI_LLAMADA` |
| Variabilidad de prestación por técnico y por territorio | ✅ / 🟡 | `CD_TPPIA` por login de la propuesta y por municipio |
| Nombre del técnico | ❌ | Tabla de usuarios |

## 6. Mockup CU2, elemento a elemento

El CU2 depende casi entero del **bloque 3**: hasta ver sus columnas, todo lo de la lista de espera es 🟡. La cabecera del mockup dice «SIDEMA · SAP»: lo de la empresa (contacto, visita, instalación) no está en SIDEMA.

**KPIs**

| Elemento | | Con qué |
|---|---|---|
| ① Total en el proceso | 🟡 | PIA con SAD o TA (`SIDM_RI_PIA` + `IT_SAD`/`IT_TA`) y tablas del servicio |
| ② Finalizadas (prestación activa) y altas del periodo | 🟡 | `SIDM_RI_SAD` / `SIDM_RI_TA` y sus históricos |
| ③ En curso (contacto o visita) | ❌ | Empresa o SAP |
| ④ Lista de espera y % | 🟡 | `SIDM_V_RI_WEBEL_ALTAS_*`; mientras tanto, `IT_ESTADO_WEB_EL` de `SIDM_RI_PIA` |
| Tiempo medio notificación → prestación (objetivo 45 d) | 🟡 | `SIDM_RI_DOC_GENERADO` (notificación) → alta del servicio |
| Tiempo medio, mediana y máximo en lista · atascadas (> 90 d) | 🟡 | `FC_INCLUSION_LAU` → alta o baja |
| Grado III con espera > umbral («prelación incumplida») | 🟡 | `SIDM_DICTAMEN.CDGRADO` + días en lista + capacidad económica. Faltan los criterios de prelación |
| Demora atribuible al usuario | 🟡 | `SIDM_LE_INCIDENCIAS` + `SIDM_LE_TP_INC` |
| Tasa de resultado y alta en plazo (≤ 7 d) | 🟡 | Fechas del servicio |

**Filtros**

| Filtro | | Con qué |
|---|---|---|
| Periodo (semanal… acumulado) | ✅ | Fechas |
| Servicio (SAD o teleasistencia) | ✅ | `IT_SAD` / `IT_TA` o la tabla del servicio |
| Lote | ❌ | Municipio → lote del contrato (sin encontrar) |
| Municipio · grado | ✅ | `SIDM_SOLICITANTE` + SUCA · `SIDM_DICTAMEN` |
| Antigüedad (< 45, 45–90, > 90) | 🟡 | Días en lista |

**Embudo, tablas y bloques de abajo**

| Elemento | | Con qué |
|---|---|---|
| Inicio: resolución del PIA | ✅ | `FCRESOLUCION_PIA` (y la notificación, bloque 3) |
| Alta en lista de espera y excluidos | 🟡 | `FC_INCLUSION_LAU`; bajas de `WEBEL_BAJAS_*` y `LE_BAJA_ACEPTADA_*` |
| Gestión y contacto · asignación de servicio | ❌ / 🟡 | Empresa o SAP; quizá en los históricos |
| Reingresos | 🟡 | Históricos `SIDM_RI_SAD_HIST` / `SIDM_RI_TA_HIST` |
| Alta del servicio | 🟡 | Tablas del servicio |
| Tabla por territorio (municipio, servicio, en espera, G3, tiempo medio, % excluidos, atascadas, tendencia) | 🟡 | Todo sale con el bloque 3, menos el lote |
| Tabla por persona: expediente, municipio, servicio, grado | ✅ | Ya están |
| Tabla por persona: estado y última acción con fecha de efectos | 🟡 / ❌ | Lista y demora en SIDEMA; contacto, visita y firma en la empresa |
| Motivos de exclusión: traslado | ✅ | `SIDM_RI_TRASLADO_OUT` |
| Motivos de exclusión: ingreso en residencia | ✅ | PIA nuevo con prestación de residencia |
| Motivos de exclusión: renuncia, no localizado, demora del usuario, datos de contacto incorrectos | 🟡 | `SIDM_LE_RENUNCIA`, `SIDM_LE_INCIDENCIAS`, `SIDM_RI_MOT_BAJA_SERV` |
| «Requiere verificación» frente a «exclusión directa» | ❌ | Definición de la unidad |
| Tiempo medio por grado frente al objetivo | 🟡 | Grado ✅ + días en lista; objetivo con variable `${…}` |
| Evolución: entradas, activaciones, exclusiones y reingresos | 🟡 | Históricos del servicio |

## 7. Qué columnas van en las vistas (v3)

**Regla:** se deja todo lo que puede explicar el proceso, y solo se quita lo que identifica a la persona o no aporta nada al análisis.

Se deja:
- claves, códigos, fechas, indicadores S/N y logins;
- motivos (aunque sean texto);
- puntuaciones del baremo e `IT_ELA`;
- nacionalidad, estado civil y fecha de nacimiento;
- nombre del valorador.

Se quita:
- nombre, documento, tarjeta sanitaria, teléfono y correo de la persona;
- la dirección completa y las coordenadas;
- los datos bancarios;
- las observaciones libres;
- el cuestionario de salud de la EVE;
- la renta y el patrimonio (se deja la capacidad económica);
- los ficheros y plantillas guardados en la tabla.

Lo sensible que se deja va marcado con «Ojo» en cada vista. El detalle, columna a columna, está en los comentarios del script.

Si el cliente lo prefiere, Celonis puede seudonimizar columnas al extraer: en «Configure columns» hay una columna «Pseudonymize». Así se cuentan y se cruzan sin verlas (por ejemplo, el DNI con Atlantix o eReg).

## 8. Preguntas para Roberto

1. **Error de Snappy:** sigue igual. Ver la pista de la sección 1 para Javier Olmeda.
2. **¿Vale el criterio de columnas de la v3?** Lo sensible que se deja está marcado con «Ojo» en cada vista.
3. **Bloque 3:** ¿puede ejecutar la consulta y pasarnos el resultado? Solo trae nombres y tipos de columna. Con eso hacemos la v4 con las vistas del CU2 y de la citación.
4. **Bloque 2:** ¿se confirman los catálogos marcados «por confirmar»? ¿Le parece bien crearlos con `SELECT *`, al ser solo códigos?
5. **Usuarios:** ¿hay una tabla con nombre, tipo (propio, subcontrata, empresa externa) y equipo de quien graba, subsana y tramita el PIA?
6. **Lote y mancomunidad:** ¿de dónde sale el municipio → lote del contrato de SAD y teleasistencia? ¿Y el municipio → mancomunidad?
7. **CU2 fuera de SIDEMA:** contacto, visita, firma del acuerdo e instalación, ¿están en SAP o en las empresas? ¿Se pueden pedir?
8. Al pasar la extracción a las vistas, marcar «Rename target table». ¿Quién ejecuta el script en PROD? Las vistas `SUCA_*` necesitan que el propietario tenga `SELECT WITH GRANT OPTION` sobre `DBA_SUCA`.

**Para la unidad (Andrés):**
- dónde va el origen «Presencial»;
- los roles del PIA según el estado que registra cada técnico;
- los criterios de prelación;
- qué motivos de exclusión «requieren verificación»;
- los objetivos del CU2 (45 días y alta en 7 días).
