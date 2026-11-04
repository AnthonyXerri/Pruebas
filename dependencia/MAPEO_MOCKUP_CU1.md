# Mapeo del mockup CU1 frente a las tablas de SIDEMA

Mockup: `mockups/MockupCU1_v2.html` (= `20261001_MineriaDeProcesos_DependenciaMockup.html`, el mismo archivo).
Inventario sacado el 04/11/2026 con el mockup abierto en un navegador, recorriendo las 3 fases, todos los selectores y botones: 8 filtros, 5 gráficos y 11 tablas.

Tablas disponibles: `SIDM_SOLICITUD`, `SIDM_HIST_ESTADO`, `SIDM_ESTADO_SOLICITUD`.
**✅ Está:** columna o estado presente (comprobado) · **🟡 Se deduce:** sale de nuestras tablas, pero hay que confirmar el significado · **❌ No está** en las 3 tablas.
**Nada está validado aún con datos reales:** las muestras son del entorno de pruebas y no hemos visto recorridos completos.

## Cabecera (todas las fases)
| Elemento | | Con qué / qué falta |
|---|---|---|
| Solicitudes activas (proceso completo) | 🟡 | Hasta la resolución del grado; sin el PIA no es el «proceso completo» |
| Plazo proceso completo (suma de las fases 1→3) | 🟡 | Fases 1 y 2 sí; falta la 3 (PIA) |
| Cumplimiento SLA global (≤180 d) | 🟡 | Igual: solo hasta la resolución del grado |
| Altas / mes | ✅ | `FCALTA` |

## Filtros
| Filtro | | Con qué / qué falta |
|---|---|---|
| Periodo (semanal… rango personalizado) | ✅ | Fechas de las solicitudes y de los eventos |
| Objetivo propuesto (días) | ✅ | Parámetro del cuadro |
| Estado · fase 1 (Alta, Pendiente de subsanación, En bucle de AVC, Completa → valoración) | ✅ | Estados 01, 60/30, 05/20/15 (repetidos) y paso a 40… |
| Estado · fase 2 (pendiente de citación, valoración en centros, citación manual, pendiente de valoración, dictamen, comisión, resolución de grado, grado resuelto) | ✅ | Estados 40, 07, 42, 43, 45, 47, 50 y 90 |
| Estado · fase 3 (propuesta PIA, resolución PIA, PIA resuelto) | ❌ | Estados del PIA |
| Territorio (municipio y mancomunidad) | ❌ | Municipio de la persona |
| Edad (tramos, EVE < 3 años…) | ❌ | Fecha de nacimiento de la persona |
| Tipo de valoración (presencial, telemática, BVD, EVE, inicial) | ❌ / 🟡 | Tipo de valoración. ¿`CDTIPO` («RS», «HE»…) tiene algo que ver? Por confirmar |
| Origen (telemática, ORBE/presencial, papel) | ❌ | Campo «origen» de la solicitud: no está en `SIDM_SOLICITUD` |
| Resolución de grado (grado 0, I–III con PIA, desistimiento, denegatoria, caducidad) | ❌ / 🟡 | Grado reconocido y tipo de resolución. «Denegatoria» quizá con 34/36 (no procede); no hay estados de desistimiento ni de caducidad |
| Tipo de prestación (fase 3) | ❌ | Prestación del PIA |

## Gráficos
| Gráfico | | Con qué / qué falta |
|---|---|---|
| Plazos de tramitación (en plazo / fuera / plazo medio / objetivo, por mes) | ✅ fases 1–2 · ❌ fase 3 | Eventos y fechas |
| Subplazos por fase frente al objetivo | 🟡 | Fases 1 y 2 (según la agrupación de estados); falta la 3 |
| Productividad y carga (trabajadores por rango de carga) | 🟡 fase 1 · ❌ fases 2–3 | Fase 1 con `IDALTA` (quien graba). Fase 2 necesita el valorador; la 3, el tramitador |
| Variabilidad BVD (G0–G3 por valorador) | ❌ | Grado y valorador |
| Variabilidad de prestación (por territorio o técnico) | ❌ | PIA, prestación y territorio |

## Fase 1 · Grabación
| Elemento | | Con qué / qué falta |
|---|---|---|
| Solicitudes grabadas (por fecha de grabación) | ✅ | `FCALTA` |
| Tiempo E2E / plazo medio (solicitud → grabación, ≤30 d) | ✅ | `FCSOLICITUD` → `FCALTA` |
| Grabadas en plazo / fuera de plazo | ✅ | Igual |
| Pendientes de grabar (bandeja) | ❌ | Registradas que aún no están en SIDEMA (no pueden estar en SIDEMA) |
| Personas involucradas | 🟡 | Logins distintos de `IDALTA` (si es la persona) |
| … 18 empresa externa / 32 propios | ❌ | Tipo de vínculo del usuario |
| % del equipo total | ❌ | Efectivos de cada fase |
| Previsión de carga (entran frente a resuelven por semana) | ✅ | Eventos |
| Tabla de trabajadores: trabajador, tipo, territorio, expedientes, carga, plazo medio, vs equipo, subsanaciones, estado | 🟡 | Expedientes, plazo, vs equipo y carga por `IDALTA` sí. Nombre, tipo y territorio no |
| Subsanaciones y AVC: tasa, número en bucle, iteraciones/AVC | ✅ | Estados 60/30/25 y 05/20/15 y sus repeticiones |
| Tabla «Nº de vueltas AVC» (exp., %, plazo +) | ✅ | Histórico |
| Tabla «Motivo» de subsanación | ❌ | Motivo o documentación requerida |
| Tablas por territorio, edad u origen (exp., % sub., plazo +, días bloqueado) | ❌ | Municipio, edad y origen (los días sí salen del histórico) |
| Equipo de subsanación: trabajador, tipo, exp. subsanados, subsanaciones/día, AVC en bucle, carga | 🟡 | Con `IDMODI` en los estados de subsanación y AVC (si es la persona); falta el tipo |

## Fase 2 · Valoración
| Elemento | | Con qué / qué falta |
|---|---|---|
| Tiempo E2E (≤120 d desde el alta) | 🟡 | Alta → resolución del grado (estado 90/34/36), según las fases |
| Expedientes valorados (por fecha de **dictamen**) / en plazo / fuera | 🟡 | Fecha de dictamen ≈ salida de 45/48 hacia 47 (por confirmar) |
| Previsión de carga | ✅ | Eventos |
| Personas involucradas / total trabajadores / media por persona / sobrecargados (valoradores) | ❌ | Valorador de cada expediente |
| Tabla de trabajadores (zona de geolocalización, variabilidad de criterio…) | ❌ | Valorador, zona y grado |
| Variabilidad BVD: valoradores activos, criterio sesgado, % alineación, tabla G0–G3 | ❌ | Grado propuesto y valorador |
| **Ver por expediente · 9 hitos:** ① Registro | ✅ | `FCREGENTRADA` |
| ② Alta | ✅ | `FCALTA` |
| ③ Pendiente de citación | ✅ | Estados 40/39/99/00 |
| ④ Citación (pendiente de valoración) | ✅ | Estado 43 (y 41/42/06) |
| ⑤ Fecha de valoración (visita) | ❌ | Fecha de la visita del valorador |
| ⑥ Grabación de la valoración | ❌ / 🟡 | ¿Entrada en 44/45? Por confirmar |
| ⑦ Dictamen | 🟡 | Salida de 45/48 hacia 47 |
| ⑧ Comisión | 🟡 | Estados 47/33 → 50 |
| ⑨ Resolución del grado | 🟡 | Entrada en 90/34/36 |
| Columnas Expediente / Estado citación / Total E2E | ✅ | |
| Columna Valorador | ❌ | Valorador |
| **Valoración individual (imputable):** citación, fecha de valoración, días a grabación, días a dictamen, total imputable | ❌ / 🟡 | Sin la fecha de la visita no se separa lo no imputable; falta también el valorador |

## Fase 3 · PIA
Todo ❌: PIA resueltos, en plazo y fuera, tiempo E2E (≤180 d), técnicos (personas, media, sobrecarga), tabla de trabajadores, variabilidad de prestación por territorio (territorios clave, atípicos, mayor dispersión) y por técnico, y tabla de tramitadores (plazo imputable, % con requerimiento, llamadas por expediente, perfil). Faltan: **estados y fechas del PIA, prestación, login de quien propone, requerimientos y llamadas del PIA, y territorio**.

## Qué hay que confirmar para que los 🟡 pasen a ✅
1. `IDALTA` es quien graba, e `IDMODI` es quien hace cada cambio de estado (personas, no procesos).
2. `FCMODI` del histórico es la fecha de **entrada** en el estado.
3. El histórico trae **todos** los cambios de cada solicitud, también el inicial.
4. La agrupación de estados en fases (y qué son AVC y RA).
5. Qué estado marca «dictamen emitido», «comisión» y «grado resuelto».
6. Qué es `CDTIPO`.

## Qué hay que pedir para los ❌
Personas (municipio, nacimiento) · campo origen o canal · valoración (tipo, valorador, fechas de cita, visita y grabación, grado propuesto, zona) · resolución del grado (grado, tipo de resolución: desistimiento, caducidad, denegatoria) · motivo de subsanación · bandeja de registro pendiente de grabar · usuarios y equipos (tipo propio/externo, equipo, efectivos por fase) · asignación expediente → valorador · PIA completo (estados, fechas, prestación, login, requerimientos, llamadas).
