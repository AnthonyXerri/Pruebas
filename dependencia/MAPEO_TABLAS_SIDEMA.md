# Mapeo de las tablas de SIDEMA · Dependencia (CU1 y CU2)

24/11/2026. Revisadas las 29 tablas de la extracción «Extraccion Dependencia» (data job «Dependencia VASOCIAL_SIDM», pool «OCPM DataPool IMPLEMENTACION»), que son las mismas que crea el script `VistasSIDMPRODv1`:
- 27 tablas de `DBA_SIDM`;
- 2 de `DBA_SUCA`.

Fuentes, sin guardar nada en Celonis:
- **Configure columns**, para los nombres y tipos;
- **Extraction Preview**, para ver qué contiene cada columna (100 filas del entorno de validación).

Los datos de validación son de prueba y antiguos (2007–2015 casi todos), así que hay columnas vacías en la muestra que pueden venir rellenas en producción.

Resultado: **`dependencia/sql/VistasSIDMPRODv2.sql`**, el mismo script con la lista de columnas en cada vista. Los nombres de columna se han comparado uno a uno con SIDEMA y coinciden en las 29.

Notación: «I» entero, «S» texto, «D» fecha. Los códigos `CD*` son texto con ceros a la izquierda: se comparan entre comillas (`'01'`).

## 1. Estado de la extracción

**Todas las ejecuciones del job han fallado** (la última, el 20/11). Falla al empezar la primera tabla con este error:

`java.lang.NoClassDefFoundError: Could not initialize class org.xerial.snappy.Snappy`

- Es el mismo error de noviembre. Está en el extractor (conexión «Uplinked», extractor v4.1.3), no en las tablas, así que cambiar las vistas no lo arregla.
- La vista previa sí funciona.
- **Pista para Javier Olmeda (sin comprobar):** este error suele salir cuando la JVM del extractor no puede cargar la librería nativa de Snappy, por ejemplo si su carpeta temporal no permite ejecutar. Se suele arreglar dándole otra carpeta (`-Dorg.xerial.snappy.tempdir=…`) o actualizando el extractor.

Otros puntos de la extracción:
- **Avisos «potential issues»:** hay uno por tabla y todos dicen lo mismo: sin filtro de fecha de cambio, la tabla no puede cargarse en *delta*. Solo importa si se pasa a carga delta.
- **`SIDM_MR_RESOLUCIONES`:** su vista previa no termina, porque guarda el PDF de cada resolución en `DSCONTENIDOFICHERO`. `SIDM_MR_TIPOS_DOCUMENTOS` (`PLANTILLA`) y `SIDM_DICTAMEN_TECNICO` (`LOB_*`) también llevan ficheros. Las vistas v2 los dejan fuera.
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

**Ojo con los tipos y los formatos:**
- En este origen, `IDSOLICITUD` es entero en todas las tablas. En la copia local de noviembre el histórico lo traía como texto, por eso se usaba `CAST`; ahora no hace falta, pero no estorba.
- `CDGRADO` es entero en `SIDM_DICTAMEN` y texto en `SIDM_DICTAMEN_TECNICO`. Al compararlos hay que convertir uno de los dos.
- `CDMUNI` viene a veces sin los ceros de la izquierda (`'79'` frente a `'079'`, en `SIDM_DATOS_VALORADOR`). Antes de cruzar con SUCA hay que normalizarlo con `LPAD(CDMUNI, 3, '0')`.
- En validación, `SIDM_ESTADO_SOLICITUD` tiene los códigos de **2 cifras** (la copia local tenía de 4). Además, `CDESTADO_GEST_VAL` viene relleno en una parte de los estados. La regla `RIGHT(…, 2)` sigue valiendo en los dos casos.
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
- `CDESTADO_DOCUMENTACION` es un código **sin catálogo**.
- `DSTEXTO_LIBRE` es el motivo, en texto libre.
- `FCINICIOSUBSANACION` y `FCDESISTIMIENTO` vienen vacías en la muestra.
- No tiene fechas de alta ni de modificación.

### CU1 · Fase 2 (valoración y grado)

**`SIDM_VALORACION_BVD`** · valoración BVD
- `FCVALORACION` es la visita.
- `CDVALORADOR` es el valorador.
- **`IT_VALORACION_ONLINE`** indica valoración telemática, que es el tipo de valoración del mockup.
- `FCINICIO_SISTEMA` y `FCFIN_SISTEMA` son la grabación de la valoración. Vienen vacías en la muestra.
- `NMRANGO_EDAD` es el tramo de edad.

**`SIDM_VALORACION_EVE`** · valoración EVE (menores de 3 años)
- Lo mismo que la BVD, más `NMGRADO_DEPENDENCIA` y `NMRANGO_MESES`.
- **Trae el cuestionario de salud en texto (`CUESTIONARIO`, `NOTAS_*`)**: queda fuera.

**`SIDM_DICTAMEN_TECNICO`** · grado propuesto
- Grado: `CDGRADO` y `DSGRADO_NIVEL`.
- Valorador: `CDVALORADOR`.
- **Fecha de comisión:** `FCVALIDACION_COMISION`, más `ACTA_COMISION`. Es el hito ⑧.
- `FCREVISION`.

**`SIDM_DICTAMEN`** · grado reconocido
- Grado y nivel: `CDGRADO`, `CDNIVEL` y `DSGRADO_NIVEL`.
- `CDTIPO_BAREMO` (BVD o EVE).
- **No trae una fecha fiable:** `FCALTA` está casi vacía. La fecha de resolución sale de `SIDM_MR_RESOLUCIONES`.

**`SIDM_MR_RESOLUCIONES`** · resoluciones
- **`FCRESOLUCION`** es el hito ⑨, resolución del grado.
- `CDTIPODOCUMENTO` es el tipo de resolución.
- `FC_ENTRADA_ESCRITO_RENUNCIA`.

**`SIDM_MR_TIPOS_DOCUMENTOS`** · catálogo de tipos de resolución
- Resolución por grado y nivel, desestimatoria grado 0, desestimatoria por incumplir requisitos, por desistimiento, por caducidad, por fallecimiento, por renuncia y por traslado.
- Además, revisiones, recurso de alzada y «Sin derecho a PIA».
- Es el filtro «Resolución de grado» del mockup.

**`SIDM_DATOS_VALORADOR`** · valoradores
- Perfil: `CDPERFIL_VALORADOR`, sin catálogo.
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
- `FC_FIN_PLAZO`.
- **`FC_TRAMITE_CONS`** es la consulta al beneficiario, inicio del plazo imputable. Viene vacía en la muestra.
- **`FC_PROPUESTA_TEC`** es la propuesta técnica. Viene vacía en la muestra.
- `CD_GRUPO` es un código sin catálogo.
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
- Motivos: `CD_MOT_*`, sin catálogo.
- `FC_SOLICITUD_PARTE` y `FC_VALORACION`.

### CU1 · Circuitos especiales

**`SIDM_RI_URGENCIA`** · tramitación por urgencia
- Fechas: `FC_SOLICITUD`, `FC_SUBCOMISION`, `FC_APROBACION` y `FC_RECHAZO`.
- **`CD_MANCO`** es la mancomunidad. Solo aparece aquí y no tiene catálogo.
- Centro de servicios sociales: `CD_CENTRO_SS`.
- Técnico: `CD_LOGIN_TECNICO`.

**`SIDM_RI_TRASLADO_IN`** y **`SIDM_RI_TRASLADO_OUT`** · traslados entre comunidades
- Comunidad, provincia y municipio de origen o destino.
- Fechas de registro, consolidación y valoración.
- Indicadores de documentación requerida.

### Territorio y edad

**`SIDM_SOLICITANTE`** · la persona
- **Edad:** `FCNACIMIENTO`.
- Sexo: `ITSEXO`.
- **Municipio:** `CDPROV` + `CDMUNI`.
- `CDDISTRITO` (Madrid capital) y `CDZONADEP`.
- `FCFALLEC_INE`, fecha de fallecimiento.
- `ITVALORACION_TARDE`, si pide la valoración de tarde.

**`SUCA_MUNICIPIO`** y **`SUCA_PROVINCIA`** · catálogos de territorio
- No tienen mancomunidad ni zona.

### CU2 · Lista de espera de SAD y Teleasistencia

**`SIDM_RI_CE_GENERAL`** · capacidad económica
- `NM_CAPACIDAD_ECON` y `NM_CAPACIDAD_ECON_RES` sirven para el orden de prelación.
- Estado: `CD_ESTADO_CE`, sin catálogo.
- Fecha de cálculo: `FC_CALCULO_CE`.
- `CD_EXPEDIENTE` es «número/año»; no lleva DNI.

## 4. Qué del mockup CU1 se puede montar ahora (antes ❌)

| Elemento | Ahora | Con qué |
|---|---|---|
| Territorio: municipio | ✅ | `SIDM_SOLICITANTE` + `SUCA_MUNICIPIO` |
| Territorio: mancomunidad y zona | 🟡 | `CDZONADEP` / `CD_MANCO` existen, pero sin catálogo |
| Edad, EVE < 3 años | ✅ | `FCNACIMIENTO`, `SIDM_VALORACION_EVE` |
| Origen (telemática, ORVE/presencial, papel) | ✅ | `DSORIGENDOC` y `SIDM_MOTALTA` |
| Pendientes de grabar (bandeja) | ✅ | `SIDM_BANDEJA_RECEPCIONADOS` |
| Motivo de subsanación | 🟡 | `DSTEXTO_LIBRE` (texto) + código sin catálogo |
| Tipo de valoración (BVD, EVE, telemática) | ✅ | Tabla de valoración + `IT_VALORACION_ONLINE` |
| Valorador por expediente | ✅ | `CDVALORADOR` |
| Perfil y tipo del valorador | 🟡 | `SIDM_DATOS_VALORADOR` (encomienda por confirmar) |
| Hito ⑤ fecha de visita | ✅ | `FCVALORACION` |
| Hito ⑥ grabación de la valoración | 🟡 | `FCINICIO_SISTEMA` / `FCFIN_SISTEMA` (vacías en la muestra) |
| Hito ⑦ dictamen | 🟡 | Sigue saliendo de los estados del histórico |
| Hito ⑧ comisión | ✅ | `FCVALIDACION_COMISION` |
| Hito ⑨ resolución del grado | ✅ | `SIDM_MR_RESOLUCIONES.FCRESOLUCION` |
| Grado propuesto / reconocido | ✅ | `SIDM_DICTAMEN_TECNICO` / `SIDM_DICTAMEN` |
| Variabilidad de grado por valorador | ✅ | Grado propuesto + valorador |
| Tipo de resolución (desistimiento, caducidad, denegatoria…) | ✅ | `CDTIPODOCUMENTO` + catálogo |
| Fase 3: estados, fechas y resolución del PIA | ✅ | `SIDM_RI_PIA` + `SIDM_RI_TRAMITES` + catálogo |
| Fase 3: prestación | ✅ | `CD_TPPIA` + `SIDM_RI_TPPIA` |
| Fase 3: técnico | 🟡 | `SIDM_RI_TRAMITES.IDALTA` (por confirmar) |
| Fase 3: requerimientos y llamadas | ✅ | `SIDM_RI_SUBS_PIA`, `SIDM_RI_LLAMADA` |
| Fase 3: consulta al beneficiario | 🟡 | `FC_TRAMITE_CONS` (vacía en la muestra) |
| Nombre del trabajador en las tablas | ❌ a propósito | Se muestra el login (ver pregunta 3) |
| Efectivos por fase | ❌ | No está en SIDEMA |

## 5. Qué se deja fuera en las vistas v2 y por qué (decisión)

**Regla:** se deja todo lo que sirve para el proceso: claves, códigos, fechas, indicadores S/N y logins de empleados.

Se quita:
- lo que identifica a la persona: nombre, documento, teléfono, correo;
- la dirección y las coordenadas;
- los datos bancarios;
- los textos libres (observaciones);
- la salud de detalle: cuestionario EVE, puntuaciones del baremo, `IT_ELA`;
- el detalle fiscal: renta, patrimonio, tipo de declaración;
- los ficheros y plantillas guardados en la tabla.

El detalle, columna a columna, está en el comentario «Fuera:» de cada vista del script. Las 3 vistas de v1 no cambian.

Celonis también puede seudonimizar columnas al extraer: en «Configure columns» hay una columna «Pseudonymize». Es una alternativa para los logins si el cliente la prefiere.

## 6. Preguntas para Roberto

1. **Error de Snappy:** sigue igual. Ver la pista de la sección 1 para Javier Olmeda.
2. **¿Vale el criterio de columnas de la v2?** Hay cuatro datos personales que se dejan porque hacen falta:
   - `FCNACIMIENTO` (si se prefiere, podría ir solo el mes y el año);
   - `FCFALLEC_INE` (personas fallecidas durante la tramitación);
   - `DSTEXTO_LIBRE` (texto libre, pero el cliente lo dio como motivo de la subsanación);
   - `NM_CAPACIDAD_ECON` (prelación del CU2).
3. El mockup muestra el **nombre** del trabajador o valorador. ¿Lo queremos? Si sí, hay que añadir `NOMBRE_VALORADOR` y pedir una tabla de usuarios.
4. `IT_ELA` (vía rápida para ELA) se ha quitado por ser dato de salud. ¿Se quiere analizar esa vía?
5. Faltan las tablas del **CU2**: `SIDM_V_RI_WEBEL_ALTAS_SAD/TA`, `SIDM_V_RI_WEBEL_BAJAS_SAD/TA`, `SIDM_RI_SAD`, `SIDM_RI_TA` y `SIDM_RI_DOC_GENERADO`.
6. Faltan **catálogos** (lista al final del script). Los más urgentes: zonas y mancomunidades (filtro de territorio), `CDESTADO_DOCUMENTACION` (motivo de subsanación) y `CD_GRUPO` del PIA.
7. Al pasar la extracción a las vistas, marcar «Rename target table» para conservar los nombres de las tablas.
8. Las vistas `SUCA_*` necesitan que el propietario tenga `SELECT WITH GRANT OPTION` sobre `DBA_SUCA`.
