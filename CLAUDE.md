# Contexto para Claude

Repositorio de trabajo de Anthony (Madrid Digital): servicio de minería de procesos para la Consejería de Familia, Juventud y Asuntos Sociales de la Comunidad de Madrid. Todo en español.

## Antes de nada
- **Datos de la Comunidad de Madrid: nunca subir datos sensibles a GitHub ni a nada público** (artifacts incluidos). Eso abarca filas de tablas de los sistemas (SIDEMA, Atlantix, eReg, Nexus…), logins de usuarios, DNIs, números de solicitud o de expediente reales y cualquier dato personal. En el repositorio solo van consultas SQL, estructura (nombres de tablas y columnas), decisiones y documentación sin datos. Los ficheros con datos (INSERT, CSV, extractos) van solo al scratchpad.
- **Dependencia en Celonis** (en curso): lee **`dependencia/TRASPASO_VIEW_CELONIS.md`** (dónde nos quedamos con la View) y **`dependencia/MEMORIA_DEPENDENCIA_CELONIS.md`**. Tiene las tablas de SIDEMA, la regla del join de estados, las fases, las decisiones de modelado y los pendientes. **Actualízala** cada vez que se aprenda o se decida algo importante.
- **Anthony está aprendiendo Celonis:** guía paso a paso. En cada paso, qué hacemos, por qué y qué esperamos ver; explica el SQL nuevo línea a línea. Un paso cada vez.

## Proyectos del repositorio
- **Natalidad** (ayudas por gestación, nacimiento o adopción; Atlantix, eReg, Nexus): mockups `mockups/MockupNatalidad_vNN.html` (la última es la v27). Se generan con scripts de parche sobre la versión anterior. Word: `mockups/Peticiones_sesion_27-10_Natalidad.docx` y `mockups/Documento_funcional_Natalidad.docx` (introducción y datos técnicos que necesitamos). Datos necesarios: `mockups/Datos_necesarios_cuadro_Natalidad_v9.xlsx`.
- **Acogimiento** (prestación por acogimiento familiar; AME): mockups y decks en `mockups/` y `deck/`.
- **Dependencia** (SIDEMA): mockup `mockups/MockupCU1_v2.html`, pain points en `deck/PainPoints_Dependencia_Discapacidad.pptx`, memoria en `dependencia/`.

## Estilo
- Textos para la unidad o para correos: cortos y claros; correos con «Hola a todas.» y «Muchas gracias, un saludo.».
- Las cifras de los mockups son ficticias.
