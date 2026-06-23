# Decisiones Técnicas (ADRs)

**Proyecto:** TramiteFácil
**Estado:** Vivo

---

## ADR-001 — Arquitectura de conocimiento del chatbot: Markdown en prompt, no RAG (MVP)

**Fecha:** 2026-06-23
**Estado:** Aceptada
**Contexto de origen:** Problem Statement §9, README "Decisiones Tomadas en MVP", BRD M3.

### Contexto

En paralelo al MVP de TramiteFácil existía una línea de trabajo (`bot/`) que construyó
un sistema **RAG** completo (Chroma + embeddings `paraphrase-multilingual-mpnet-base-v2`
+ retriever híbrido) sobre un dataset de **4,507 trámites federales** de gob.mx
(la "tramitoteca").

Surgió la pregunta de si el chatbot del MVP debía apoyarse en ese RAG.

### Evidencia decisiva

Se verificó el dataset del RAG contra los 3 trámites del MVP:

| Búsqueda en el dataset | Coincidencias |
|---|---|
| "licencia de conducir" | 0 |
| "verificación vehicular" | 0 |
| "cambio de placas" | 0 |
| "conducir" | 0 |
| Dependencias SEMOVI / Movilidad / Tránsito | 0 |

Los 3 trámites del MVP son **estatales** (SEMOVI / autoridades de movilidad de cada
entidad). El dataset del RAG es **federal**. **El corpus del RAG no contiene los
trámites del MVP**, por lo que un chatbot basado en ese RAG no podría responder las
preguntas centrales del producto.

### Decisión

Para el MVP, el conocimiento del chatbot son **archivos Markdown curados por trámite**
(`docs/05_Development/knowledge-base/`) inyectados en el system prompt del LLM. **Sin
RAG ni base vectorial en el MVP**, tal como ya anticipaba el Problem Statement.

El motor RAG (`bot/`) **se conserva** en el repositorio como base para una futura
expansión a trámites federales (V2+), pero no alimenta el chatbot del MVP.

### Consecuencias

- ✅ El contenido del MVP es exactamente el que se necesita (3 trámites vehiculares),
  curado y mantenido por el equipo, con fuente primaria gob.mx / portales estatales.
- ✅ Sin infraestructura de embeddings ni vector store para el MVP → más simple de operar.
- ✅ Control total sobre el contenido → menor riesgo de alucinación (RNF-007): el LLM
  solo dispone del Markdown del trámite activo.
- ⚠️ El contenido es estático y se actualiza por eventos (no por calendario) — riesgo
  Crítico aceptado conscientemente (Problem Statement §8). Mitigación: disclaimer visible
  (RF-017) + recomendación de verificar en portal oficial (RN-003).
- ⚠️ El contenido varía por estado; los archivos Markdown documentan el caso general y
  marcan explícitamente lo que cambia por entidad.

---

## ADR-002 — Stack del PoC: FastAPI + SQLite (stdlib) + Next.js

**Fecha:** 2026-06-23
**Estado:** Aceptada

### Decisión

- **Backend:** FastAPI. Persistencia con **SQLite vía `sqlite3` de la stdlib** (sin ORM):
  evita dependencias pesadas y problemas de wheels en Python 3.14 para un PoC.
- **Auth ligera:** contraseñas con **PBKDF2-HMAC-SHA256 + salt** (`hashlib`, stdlib;
  RNF-004), sesiones con **token opaco aleatorio** (`secrets`) almacenado en tabla
  `sessions` con expiración (RNF-005). Sin dependencias de JWT/bcrypt.
- **LLM:** Gemini 2.0 Flash por defecto (`GOOGLE_API_KEY`), conmutable a OpenRouter
  (`PROVEEDOR_LLM=openrouter`). Ver `bot/.env.example`.
- **Frontend:** Next.js 15 (App Router) + React 19, TypeScript.

### Consecuencias

- ✅ Cero dependencias nativas frágiles; arranque simple.
- ⚠️ SQLite y sesiones en token opaco son suficientes para PoC; producción requeriría
  Postgres, rotación de secretos y, posiblemente, JWT/refresh tokens.
- 🔲 Recuperación de contraseña (US-004) requiere envío de correo → fuera del PoC,
  pendiente para una iteración posterior.
