# Problem Statement
**Proyecto:** TramiteFácil  
**Versión:** 0.4 — Arquitectura de conocimiento definida  
**Fecha:** 2026-03-15  
**Autor:** [Tu nombre]  
**Estado:** En revisión

---

## 1. Contexto

Realizar un trámite gubernamental en México representa una de las experiencias más frustrantes para el ciudadano promedio. La información oficial está dispersa entre sitios web desactualizados, oficinas físicas con atención inconsistente y foros informales en redes sociales. No existe un punto de acceso centralizado, confiable y amigable que guíe al ciudadano desde que decide iniciar un trámite hasta que lo concluye.

---

## 2. Declaración del Problema

> **Los ciudadanos mexicanos que necesitan realizar trámites gubernamentales carecen de una fuente centralizada y confiable que les indique exactamente qué documentos necesitan, cómo obtenerlos o llenarlos, y cómo es la experiencia real en los módulos de atención — lo que resulta en visitas fallidas, tiempo perdido y alta frustración.**

---

## 3. Evidencia del Problema

| Síntoma | Impacto |
|---|---|
| Información oficial desactualizada o incompleta | El ciudadano llega al módulo sin los documentos correctos |
| Formularios gubernamentales complejos sin guía | Errores en llenado que generan rechazos y re-visitas |
| Opiniones sobre módulos dispersas en Reddit/foros | No se puede saber dónde es más rápido o eficiente ir |
| Sin retroalimentación ciudadana oficial | Los problemas de atención no se documentan ni mejoran |

---

## 4. A Quién Afecta

El problema impacta a cualquier ciudadano mexicano que deba interactuar con instituciones gubernamentales. Para el **MVP**, el enfoque está acotado a ciudadanos que realizan **trámites vehiculares** en México, con énfasis en:

- Personas que realizan el trámite por primera vez y no saben qué llevar.
- Ciudadanos que han tenido visitas fallidas por documentación incompleta o incorrecta.
- Usuarios que quieren resolver dudas sin tener que llamar a una oficina o buscar en foros.

*(Ver documento: `01_Discovery/user_personas.md` para detalle de perfiles)*

---

## 5. Solución Propuesta

**TramiteFácil** es una plataforma web que centraliza la información necesaria para realizar trámites gubernamentales en México, comenzando por trámites vehiculares. Funciona como un asistente personal: el usuario crea un espacio de trabajo por trámite y accede a un chatbot especializado que le resuelve dudas con información factual y actualizada.

### Propuesta de valor central (MVP):
- **Información confiable y actualizada:** Un chatbot especializado exclusivamente en trámites vehiculares mexicanos (licencia, verificación, cambio de placas), con conocimiento mantenido manualmente por el equipo.
- **Onboarding mínimo:** Solo nombre, correo y contraseña para comenzar. Datos adicionales (ubicación, teléfono) se solicitan de forma progresiva según el trámite.
- **Sin fricciones:** El usuario puede resolver dudas concretas en lenguaje natural sin navegar portales gubernamentales.

### Versiones futuras (fuera del MVP):
- **V2 — Chat Form:** Llenado asistido de formularios PDF con IA.
- **V2 — Sección Documentos:** Catálogo descargable de documentos requeridos por trámite.
- **V3 — Opiniones:** Recopilación de experiencias ciudadanas sobre módulos de atención (fuente de datos a definir).

---

## 6. Lo Que NO Es Esta Solución

Para evitar scope creep, se define explícitamente lo que el producto **no** hace:

- ❌ No es un sistema de agendamiento de citas (no gestiona turnos ni calendarios).
- ❌ No tramita directamente ante instituciones gubernamentales (no hace el trámite por el usuario).
- ❌ No reemplaza los portales oficiales (los complementa).
- ❌ No es una app móvil (web-first en MVP).
- ❌ No cubre trámites fuera del dominio vehicular en MVP (SAT, INE, IMSS, etc. son V2+).
- ❌ El chatbot **no da opiniones sobre módulos de atención** en MVP — solo información factual de trámites. (La fuente de datos de opiniones está pendiente de definir para V3).

---

## 7. Métricas de Éxito (Indicadores a definir antes de lanzamiento)

| Métrica | Descripción |
|---|---|
| Consultas al chatbot | Número de preguntas respondidas por sesión — indica si el usuario encuentra valor |
| Tasa de retención | % de usuarios que regresan para un segundo trámite o sesión |
| Trámites iniciados | Cuántos usuarios crean al menos un trámite en su sesión |
| Tasa de abandono en onboarding | % de usuarios que no completan el registro — indicador de fricción |

---

## 8. Riesgos e Incógnitas Conocidas

| Riesgo | Nivel | Estado | Notas |
|---|---|---|---|
| Contenido del chatbot desactualizado | **Crítico** | ⚠️ Aceptado conscientemente | Contenido estático en MVP. Las actualizaciones se disparan por eventos (cambio regulatorio, reporte de usuario), no por calendario. Fuente de verdad: gob.mx como primaria. **Mitigación mínima obligatoria: disclaimer visible en la UI.** Si el MVP se extiende más de 3 meses sin revisión, programar auditoría de los 3 archivos de knowledge base contra fuentes oficiales. |
| Fuente de conocimiento incompleta | Medio | Activo | SEMOVI y portales estatales no están confirmados para MVP. El chatbot responde solo con lo que tiene en su base. Debe reconocer explícitamente cuando no tiene información suficiente. |
| Calidad del contenido del chatbot | Alto | Activo | Respuestas incorrectas sobre trámites = daño real al usuario. El chatbot debe tener límites claros: solo responde sobre los 3 trámites vehiculares del MVP y declara cuando no sabe. |
| Scope creep en el chatbot | Medio | Activo | Sin delimitación explícita en el prompt del LLM, el chatbot puede intentar responder sobre trámites fuera del MVP. Documentar restricciones en `05_Development/technical_decisions.md`. |
| Fuentes de opiniones/reseñas | Alto | ⏸ Pausado | Scraping descartado. Estrategia de datos a definir antes de V3. |
| Adopción inicial sin tráfico orgánico | Medio | Activo | Proyecto personal sin estrategia de adquisición definida aún. |

---

## 9. Alcance del MVP — Confirmado

**Dominio:** Trámites vehiculares únicamente.  
**Trámites cubiertos:** Licencia de conducir · Verificación vehicular · Cambio de placas

### Incluido en MVP:
1. **Autenticación básica** — registro con nombre, correo y contraseña. Sin datos adicionales en onboarding.
2. **Creación de trámite** — el usuario selecciona uno de los 3 trámites disponibles y se crea su espacio de trabajo.
3. **Chatbot de trámites** — LLM con conocimiento acotado a los 3 trámites vehiculares del MVP. Responde preguntas factuales: qué documentos llevar, costos, ubicaciones, horarios, requisitos. **No da opiniones sobre módulos de atención.**
4. **Perfil progresivo** — datos como ubicación o teléfono se solicitan contextualmente dentro del flujo de un trámite, no en el registro.

### Fuera del MVP (versiones futuras):
| Feature | Versión | Bloqueador |
|---|---|---|
| Chat Form (llenado asistido de PDFs) | V2 | Complejidad técnica de extracción y escritura en PDF |
| Catálogo de documentos descargables | V2 | Depende de acuerdo de mantenimiento de archivos |
| Sección de Opiniones | V3 | Fuente de datos pendiente de definir |
| Trámites no vehiculares (SAT, INE, etc.) | V2+ | Expansión de base de conocimiento del chatbot |

---

## 10. Próximos Pasos

- [x] ~~Definir los trámites iniciales del catálogo~~ → Licencia, Verificación, Cambio de placas
- [x] ~~Resolver estrategia de fuente de datos para Opiniones~~ → Pausado hasta V3
- [x] ~~Definir proceso de mantenimiento del catálogo~~ → Disparado por eventos, fuente primaria gob.mx
- [x] ~~Definir arquitectura del conocimiento del chatbot~~ → Markdown estático inyectado en system prompt, sin RAG en MVP
- [x] ~~Escribir BRD con Epics y User Stories~~ → `02_Requirements/BRD.md` + `epics_and_stories.md`
- [x] ~~Poblar los 3 archivos de knowledge base~~ → `05_Development/knowledge-base/` (licencia, verificación, cambio-placas)
- [x] ~~Documentar decisión de arquitectura del chatbot como ADR~~ → `05_Development/technical_decisions.md` (ADR-001: Markdown en prompt, sin RAG; confirmado por evidencia: los 3 trámites del MVP son estatales y no están en el dataset federal del RAG)
- [ ] PoC funcional construido (auth + workspaces + chat). Pendiente: clave LLM con cuota disponible (Gemini free tier agotado), recuperación de contraseña (US-004), perfil progresivo (US-013/014)

---

*Este documento es un artefacto vivo. Actualizar versión y fecha ante cualquier cambio significativo.*
