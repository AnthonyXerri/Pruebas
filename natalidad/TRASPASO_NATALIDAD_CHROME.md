# Traspaso · Cuadro de mando de Natalidad en Celonis (para una sesión local con Claude in Chrome)

Pega este texto entero como primer mensaje en una sesión de Claude Code **en el ordenador de Anthony**, con la extensión **Claude in Chrome** activa y Celonis abierto en Chrome. Si la sesión tiene el repositorio, trae antes la rama `claude/laughing-darwin-m4vbiv` (`git fetch origin claude/laughing-darwin-m4vbiv && git checkout claude/laughing-darwin-m4vbiv`).

---

## 0. Quién eres y cómo trabajas

Eres el asistente de Anthony (NTT DATA, para Madrid Digital). Trabajáis en el servicio de minería de procesos de la Consejería de Familia, Juventud y Asuntos Sociales de la Comunidad de Madrid. Todo en **español**.

- Anthony **está aprendiendo Celonis**. Puedes manejar el navegador, pero **explica cada paso**: qué haces, por qué y qué esperas ver. Cuando escribas SQL o PQL nuevo, explícalo línea a línea. Avanza paso a paso y para cuando algo no cuadre.
- **Regla de oro de los datos:** son datos de la Comunidad de Madrid.
  - Nunca subas a GitHub ni a nada público (artifacts incluidos) filas de tablas, DNI, nombres, logins de usuarios, números de expediente o de solicitud reales ni ningún dato personal.
  - En el repositorio solo van SQL, PQL, estructura (nombres de tablas y columnas) y decisiones.
  - No copies al chat filas con datos personales; si las ves en pantalla, no las transcribas.
- **Nunca, sin que Anthony diga que Roberto lo ha aprobado:**
  - **Test changes**: carga en el entorno de desarrollo compartido;
  - **Create version** y **Deploy**;
  - borrar nada.
- Guarda siempre como borrador (**Save** o **Save with Validation**).
- **Correos de Anthony:** cortos y claros; empiezan con «Hola a todas.» y terminan con «Muchas gracias, un saludo.».
- **Documentación:** si se decide o se aprende algo importante, actualiza `natalidad/PLAN_CELONIS_NATALIDAD.md` y `natalidad/MEMORIA_NATALIDAD_CELONIS.md`.

## 1. Qué estamos haciendo

Construir en **Celonis Studio** el cuadro de mando de las **ayudas por gestación, nacimiento o adopción** (Natalidad).
- **Modelo a imitar:** el mockup `mockups/MockupNatalidad_v32.html`. Abrirlo en el navegador ayuda mucho. Las cifras del mockup son ficticias.
- **Datos:** de momento solo Atlantix. eReg, Nexus y los campos propios de Natalidad están pedidos (sección 6).
- **Lo que falta de datos:** se deja con «Pendiente de datos», como se hizo en Dependencia (sección 5).

### Orden de trabajo

| Paso | Qué | Estado |
|---|---|---|
| 1 | Objetos y eventos de Natalidad (Objects & Events) | ✅ Hecho, en borrador (sección 2) |
| 2 | **Perspectiva «Natalidad»**: objeto principal `NatExpedientes`, más `NatEtapas` y `NatInteresados`, y event log (por ejemplo `EventosNatalidad`) con los 8 eventos | ▶ Siguiente. Se puede crear y guardar en borrador |
| 3 | **Test changes** solo de esa perspectiva (genera el data model y el Knowledge Model de prueba) | ⛔ Solo si Anthony confirma que Roberto lo aprueba |
| 4 | **Knowledge Model:** KPIs en PQL (sección 4) | Después del paso 3 |
| 5 | **View** que imite el mockup v32 (sección 4) | Después del paso 4 |
| 6 | Create version y Deploy | Con Roberto |

Lo primero: comprobar en Celonis si la perspectiva o el Test changes ya existen (quizá los hizo Roberto) y decirle a Anthony lo que ves antes de tocar nada.

## 2. Lo que ya está hecho en Celonis

- **Pool de trabajo:** «OCPM DataPool VALIDACION y PRODUCCION» → Objects & Events.
- **Etiqueta y prefijo:** etiqueta **Natalidad** (Custom Processes); prefijo **`Nat`**.
- **Data Source de todas las transformaciones:** **«OCPM DataPool IMPLEMENTACION _Conexión Producción PRATLX_RO»** (36 tablas de Atlantix). Por defecto sale «None (Global)», que da «Object … not found».
- **Filtro de Natalidad en todo:** `CDAPLICACION = 'D032' AND CDPROCEDIMIENTO = '3163'` (unos 53.000 expedientes desde 2022). D032 tiene otros procedimientos (partos múltiples, adopción, protección…) que **no** entran.
- **SQL de cada transformación:** `natalidad/sql/01_…` a `11_…`. **Ficha completa** para reconstruir el modelo: `natalidad/MODELO_NATALIDAD_CELONIS.md`.

**Objetos** (todos con ID String PK):

| Objeto | Atributos | Relación |
|---|---|---|
| `NatExpedientes` | **String:** Aplicacion, CodigoProcedimiento, CodigoConvocatoria, EjercicioConvocatoria, CodigoExpediente, IdEstado, DescripcionEstado, UsuarioAsignado, IdUnidad, DescripcionUnidad, ReferenciaSolicitud, CodigoSolicitud, Convocatoria<br>**Datetime:** FechaInicio (alta), FechaResolucion, FechaFinTramitacion, FechaAnulacion, FechaPresentacionInteresado (solicitud), FechaEntradaSistemaRegistro, FechaEntradaRegistroConsejeria, FechaCierre | Padre |
| `NatEtapas` | IDEtapa, DescripcionEtapa, Confiscalizacion, **Fase** | 1 — N con NatExpedientes |
| `NatInteresados` | TipoInteresado, EsPrincipal, EsSolicitante, TipoDocumento, NacionalidadAprox (por DNI / NIE), TramoEdad, MedioNotificacion, CdProvincia, Provincia, CdMunicipio, Municipio | 1 — N con NatExpedientes |

**Eventos** (ID String PK, Time Datetime; relación «involves one» con NatExpedientes):

| Evento | Qué es | Atributos clave |
|---|---|---|
| `NatSolicitudPresentada` | Presentación de la solicitud (`FC_SOL_INTERESADO`) | Actividad |
| `NatExpedienteAbierto` | Alta del expediente en Atlantix | Actividad |
| `NatEtapaIniciada` / `NatEtapaFinalizada` | Inicio y fin de cada etapa (también con NatEtapas) | Actividad, Etapas, **Fase**, `Fecha Inicio Etapa`, `Fecha Fin Etapa` (con espacios) |
| `NatExpedienteResuelto` | Resolución (por plantilla firmada) | **SentidoResolucion** (favorable, denegación, desistimiento), OrigenFecha, fechas de resolución, generación y firma |
| `NatExpedienteAnulado` | Anulación | Actividad |
| `NatActividadRealizada` | Bitácora de Atlantix: anulaciones de etapa, hitos, envío a la Intervención, cambios de unidad, documentos requeridos, notificaciones, cambio de convocatoria | Actividad (clasificada), DescripcionActividad, IdEtapa, OrdenActividadNum |
| `NatNotificaciones` | Notificaciones con fecha de acuse | **TipoNotificacion** (Requerimiento, resoluciones, Modificación, Baja, Reintegro, Otra), ConAcuse, `Fecha Notificacion`, `Fecha Acuse` |

**Valores de `Fase`** (los del mockup):
- «2. Gestión del expediente»: GESTIÓN EXPEDIENTE, REQUERIMIENTO.
- «3. Validación de terceros»: PROPUESTA FAVORABLE, VALIDACIÓN TERCERO.
- «4. Intervención»: PTE. ENVÍO INTERVENCIÓN, INTERVENCIÓN CONCESIÓN, ACTUACIÓN INTERESADA, DEV A INSTANCIA PROMO.
- «5. Resolución y pago»: FAVORABLE CONCESIÓN, FAVORABLE CON OBS, RESOLUCIÓN FAVORABLE.
- «Fin sin concesión»: denegación y desistimiento.
- Además: «Mantenimiento», «Pago único» y «Sin clasificar».
- La fase 1, «Entrada» (registro → alta), no es una etapa de Atlantix: va de `NatSolicitudPresentada` a `NatExpedienteAbierto`.

**Hallazgos que importan para los KPIs:**
- **Etapas anuladas:** `GSTA_V_CEL_ETAPA` (la base de los eventos de etapa) **no trae las etapas anuladas**. Los requerimientos y las vueltas atrás completas salen de la bitácora (`NatActividadRealizada`): «Anulación de la Etapa …» e hitos de requerimiento.
- **Resolución favorable:** es **colectiva y mensual**. `FechaResolucion` lleva hora 00:00 y va por lotes; la firma es individual. Hay que decidir cuál cuenta como fecha de resolución; de momento, `NatExpedienteResuelto.Time` (firma, generación o resolución, por ese orden).
- **Respuestas de la Intervención:** se graban por lotes (cientos en el mismo minuto). «No fiscalizable» y «Desfavorable» no aparecen en los datos.
- **Fecha de nacimiento de la solicitante:** solo en torno al 21 % (menos del 10 % en 2022 y 2023). La edad saldrá con mucho «No informado».
- **Municipio:** está en `NatInteresados`, pero no se ha comprobado cuántas lo tienen informado. Consulta: `natalidad/sql/00i_comprobar_municipio.sql`.
- **Convocatorias:** hay una por año (AFN1 / AFN2 no son tipos). Muchas solicitudes de 2025 se pasaron a la convocatoria 2026.
- **Funciones que el motor de validación no admite:** `TO_CHAR`, `POSITION`, `CHAR_LENGTH`. Sí admite `SUBSTRING(x FROM n)`, `LEFT`, `RIGHT`, `CASE`, `||`, `ROW_NUMBER() OVER` y `LIKE`.

## 3. Lecciones de PQL (de la View de Dependencia, `dependencia/TRASPASO_VIEW_CELONIS.md`)

- **`CASE`** siempre en forma completa (`CASE WHEN … THEN … END`).
- **Variables de la View:** `${nombre}`. Si el nombre no existe, da «Syntax error near [$]». Nunca números fijos de objetivo: usar variables, por ejemplo `${plazo_dias}` con 90 por defecto mientras la unidad no confirme el plazo.
- **Nombres en el Knowledge Model:**
  - objeto: `"o_custom_NatExpedientes"`;
  - event log: por ejemplo `"el__EventosNatalidad"`.
  - Comprobar los nombres reales en el KM. Usar siempre el event log de la perspectiva de forma explícita: en Dependencia, las tablas `e_custom_…` sueltas no estaban conectadas.
- **Funciones útiles:**
  - `PU_MIN`, `PU_MAX` y `PU_COUNT` del event log al expediente;
  - `GLOBAL(…)` para porcentajes;
  - para fechas de referencia, el último dato (`PU_MAX(CONSTANT(), …)`) mejor que `TODAY()`.
- **«Pendiente de datos» sin romper el KPI:** comentario `/* Pendiente de datos: … */` más una expresión agregada que da nulo (`AVG(CASE WHEN "o_custom_NatExpedientes"."ID" IS NULL THEN 0.0 END)`). Sale «–».
- **Porcentajes:** formato Rounded con unidad «%» si el PQL ya multiplica por 100.
- **Trucos del editor:**
  - Done no cierra si el Preview dice «Data requirements … not met»: antes, Ctrl+Enter.
  - Un filtro filtra toda la View: configurar Interactions.
  - Un KPI de texto sin agregación devuelve una fila por expediente.
- **En el navegador:** solo el editor visual; leer la View por API lo bloquea el clasificador de permisos.

## 4. El cuadro (mockup v32) y de dónde sale cada cosa

Pestañas del mockup: **Seguimiento del proceso** · **Comparativa de periodos** · **Explorador de procesos**. Filtros de toda la pantalla: Desde / Hasta, Ver por (semana, quincena, mes, trimestre, año), Año de solicitud, Tipo de solicitud, Canal, Plazo de tramitación (días).

### Cabecera (Seguimiento del proceso)

Lógica del mockup:
- **Tramitación:** es un **embudo de las solicitudes presentadas en el periodo**, con su situación a la fecha de corte.
- **Tiempos:** se miden sobre los **resueltos en el periodo**.

| Bloque | KPI | Cálculo con Atlantix | Estado |
|---|---|---|---|
| Fase previa | Entradas en registro, aportaciones, solicitudes recibidas, pendientes de alta | eReg | Pendiente de datos. Las «recibidas» que ya tienen expediente sí salen (`NatSolicitudPresentada`) |
| Tramitación | Expedientes dados de alta | Solicitudes del periodo con alta (`FechaInicio`) hasta la fecha de corte | ✅ |
| Tramitación | Pendientes de resolver | Dados de alta − resueltos, repartidos en «en revisión o requerimiento», «revisados sin proponer» y «ya propuestos» | ✅ el total; ⚠ «revisados sin proponer» pendiente (el campo de revisión de conformidad aún no existe en Atlantix) |
| Tramitación | Expedientes resueltos (% de los de alta) | Con `NatExpedienteResuelto` hasta la fecha de corte | ✅ |
| Tramitación | Denegados o desistidos / Favorables (% de los resueltos) | `SentidoResolucion` | ✅ |
| Tiempos | Tiempo E2E | Resolución − presentación, media de días de los resueltos en el periodo | ✅ |
| Tiempos | Registro → alta | Alta − presentación | ✅ |
| Tiempos | Alta → resolución | Resolución − alta | ✅ |
| Tiempos | Incumplimiento del plazo | % de los resueltos en el periodo que tardan más de `${plazo_dias}` | ✅ (plazo por confirmar; 90 por defecto) |
| Reprocesos | Expedientes con reprocesos (% **de los resueltos**, el mismo número que «Expedientes resueltos») | Resueltos que vuelven a una fase anterior a la que ya habían llegado, una vez por expediente. Sale del orden de `Fase` en los eventos de etapa y de las «Anulación de la Etapa» de la bitácora. Los requerimientos (dentro de la misma fase) no cuentan. El aviso dice desde qué fase vuelven | ✅ |
| Gestión económica | Nuevas altas en nómina, beneficiarias activas, pagos únicos, dejan de cobrar, importe ejecutado y comprometido | Campos de Soluciones (inicio y fin de pagos, baja, importes) y Nexus | Pendiente de datos |

### Gráficos y tablas

| Componente | Cálculo con Atlantix | Estado |
|---|---|---|
| Tiempo medio y expedientes resueltos por fase | Días por `Fase` con `NatEtapaIniciada` / `NatEtapaFinalizada`, más los expedientes que hay ahora en cada fase. Selector «Días de» (quién: unidad, solicitante, gestión económica, Intervención, calendario) | ✅ tiempos; ⚠ «Días de» parcial |
| Entradas, salidas y stock | Por mes: altas, resueltos y stock acumulado | ✅ (entradas = solicitudes con expediente) |
| Stock pendiente por fase y antigüedad | Abiertos por fase actual y tramos de 0–30, 31–60, 61–90 y más de 90 días | ✅ |
| Composición (dimensión elegible) | Edad (`TramoEdad`), Nacionalidad (de momento `NacionalidadAprox`), Municipio, Sentido de la resolución, Respuesta de la Intervención (etapas). Tipo de solicitud, Canal, País, Hijos y Requisito incumplido → «Pendiente de datos» | ⚠ parcial |
| Expedientes sin actividad | Abiertos con días sin actuación (último `NatActividadRealizada.Time`), etapa, situación y días desde el registro. Filtro de etapa y umbral (más de 30, 60, 90, 180 días). Exportar a Excel. **No mostrar el gestor asignado** | ✅ (sin «Atrasos» ni «Meses de atraso», que esperan datos) |
| Gestión económica: crédito por línea y anualidad, atrasos por mes de solicitud, altas de una remesa, revisados sin proponer | Nexus y Soluciones | Pendiente de datos |
| Comparativa de periodos | La cabecera en dos periodos, con la diferencia en número y en %. Sin reprocesos ni gestión económica | ✅ |
| Explorador de procesos | Explorador de Celonis sobre el event log | ✅ |

## 5. Datos pedidos (no inventarlos; poner «Pendiente de datos»)

- **Soluciones (equipo de la aplicación Atlantix), campos propios de Natalidad, con tabla y columna:**
  - tipo de solicitud;
  - número de hijos o cuantía mensual;
  - importe propuesto (atrasos y mensualidad) e importe pagado cada mes;
  - motivo de denegación;
  - fecha de nacimiento del menor o de parto previsto;
  - nacionalidad de origen y país de nacimiento.
  - **Además darán:** el último mes-año de pago (cuando el menor cumple dos años) y la fecha de baja (solo en bajas por incidencia).
  - **Primer pago:** es el mes de la propuesta favorable, que ya tenemos.
  - **Revisión de conformidad:** se creará (marca y fecha) cuando haya petición oficial. Se ha pedido que la fecha no se borre al proponer.
- **Andrés (técnico del equipo), vía Madrid Digital:**
  - eReg: asientos, tipo, canal, duplicados y clave con Atlantix (`REF_SOLICITUD` / `CD_SOLICITUD`, por confirmar);
  - Nexus: ADOK por expediente, crédito autorizado, pagos por mes, terceros y clave con el expediente;
  - bandeja de registros de Atlantix.
- **Gestión económica:** fechas de cada mes del CSV de terceros (envío y carga de vuelta).
- **Unidad:** plazo máximo para resolver y plazo de aportación de lo requerido.
- **Detalle y decisiones:** `natalidad/PLAN_CELONIS_NATALIDAD.md`, apartado «Petición de datos».

## 6. Primer mensaje que esperamos de ti

1. **Qué ves:** pool, Objects & Events con los objetos y eventos `Nat…`, si existe la perspectiva «Natalidad» y si hay data model o Knowledge Model de Natalidad.
2. **Propuesta del siguiente paso**, en general crear la perspectiva (paso 2), explicada para Anthony.
3. **Espera su «adelante»** antes de guardar nada.
