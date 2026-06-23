# TramiteFácil — Documentación del Proyecto

**Descripción:** Plataforma web de asistencia integral para trámites gubernamentales en México.  
**Estado actual:** Discovery / Levantamiento de requerimientos  
**Última actualización:** 2026-03-15

---

## Estructura de Carpetas

```
TramiteFácil/
├── README.md                          ← Este archivo (índice general)
│
├── 00_Project_Charter/
│   └── problem_statement.md           ✅ v0.4
│
├── 01_Discovery/
│   └── user_personas.md               ✅ v0.2 — sin validar
│
├── 02_Requirements/
│   ├── BRD.md                         ✅ v1.0 — Draft
│   ├── epics_and_stories.md           ✅ v1.0 — 14 historias
│   └── non_functional_requirements.md 🔲 Pendiente
│
├── 03_Design/
│   ├── architecture/                  🔲 Pendiente
│   ├── database_schema/               🔲 Pendiente
│   ├── wireframes/                    🔲 Pendiente
│   └── api_contracts/                 🔲 Pendiente
│
├── 04_Planning/
│   ├── roadmap.md                     🔲 Pendiente
│   └── backlog.md                     🔲 Pendiente
│
├── 05_Development/
│   ├── technical_decisions.md         ✅ ADR-001 (sin RAG) · ADR-002 (stack PoC)
│   └── knowledge-base/               ✅ Contenido poblado (3 trámites)
│       ├── licencia.md               ✅
│       ├── verificacion.md           ✅
│       └── cambio-placas.md          ✅
│
├── 06_QA/
│   └── test_plan.md                   🔲 Pendiente
│
└── 07_Deploy/
    └── environments.md                🔲 Pendiente
```

---

## Estado del Proyecto

| Fase | Artefacto | Estado |
|---|---|---|
| Charter | Problem Statement | ✅ v0.4 |
| Discovery | User Personas | ✅ v0.2 — sin validar |
| Discovery | Entrevistas con usuarios | ⏸ No planeado para MVP |
| Requirements | BRD | ✅ v1.0 — Draft |
| Requirements | Epics & User Stories | ✅ v1.0 — 14 historias definidas |
| Requirements | Non-functional requirements | 🔲 Pendiente |
| Development | Knowledge Base (contenido) | ✅ 3 trámites poblados |
| Development | ADR — arquitectura del chatbot | ✅ ADR-001 / ADR-002 |
| Development | PoC funcional (backend + frontend) | ✅ Ver `POC_README.md` (raíz) |
| Design | Arquitectura técnica | 🔲 Pendiente |
| Planning | Roadmap / Backlog | 🔲 Pendiente |

---

## Decisiones Tomadas en MVP

| Decisión | Resolución |
|---|---|
| Dominio inicial | Solo trámites vehiculares: licencia, verificación, cambio de placas |
| Onboarding | Solo nombre, correo y contraseña. Datos adicionales de forma progresiva |
| Chat Form | Postergado a V2 |
| Sección Opiniones | Postergada a V3 (fuente de datos pendiente) |
| Chatbot — alcance de respuestas | Solo información factual de los 3 trámites vehiculares. No da opiniones sobre módulos de atención en MVP |
| Fuente de conocimiento del chatbot | Archivos Markdown por trámite (`/knowledge-base/`), alimentados con gob.mx como fuente primaria. SEMOVI y portales estatales como complemento aspiracional no confirmado para MVP |
| Arquitectura del conocimiento | **Archivos Markdown estáticos inyectados en system prompt.** Sin RAG ni vector database en MVP. El contenido de cada trámite cabe completo en el contexto del LLM |
| Actualización del contenido | Estático en MVP. Disparada por eventos (cambio regulatorio, reporte de usuario) — no por calendario. ⚠️ Riesgo aceptado conscientemente — ver §8 del Problem Statement |

## Decisiones Pendientes

*(Ninguna bloqueante para avanzar al BRD)*

---

## Cómo Usar Esta Documentación con LLMs

Para dar contexto a un LLM sobre este proyecto, proporcionar en este orden:
1. `README.md` — visión general y estado
2. `00_Project_Charter/problem_statement.md` — qué problema resuelve y qué NO es
3. `01_Discovery/user_personas.md` — para quién
4. `02_Requirements/BRD.md` — qué debe hacer (cuando esté disponible)

Para tareas de diseño o arquitectura, agregar además:
- `03_Design/architecture/` (cuando esté disponible)

---

*Este README debe actualizarse cada vez que se agrega o modifica un artefacto.*
