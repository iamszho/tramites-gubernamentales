# PoC — TramiteFácil

Prueba de concepto funcional de **TramiteFácil**: plataforma web para prepararse para
trámites vehiculares en México (licencia de conducir, verificación vehicular, cambio de
placas), con autenticación, espacios de trabajo por trámite y un chatbot conversacional.

Implementa la mayoría del MVP descrito en `docs/` (BRD + Epics). Stack: **FastAPI** +
**Next.js/React** + **SQLite**.

## Decisión de arquitectura (importante)

El chatbot **no usa RAG**. Su conocimiento son archivos **Markdown curados por trámite**
(`docs/05_Development/knowledge-base/`) inyectados en el system prompt del LLM. Razón
(ADR-001): los 3 trámites del MVP son **estatales** (SEMOVI) y **no existen** en el dataset
federal del motor RAG de `bot/` (verificado: 0 coincidencias). El motor RAG se conserva en
`bot/` para una futura expansión a trámites federales (V2+), pero no alimenta este MVP.

Ver `docs/05_Development/technical_decisions.md`.

## Arquitectura

```
Frontend (Next.js, :3000)
   /login  /register  /dashboard  /tramite/[id]
        │  Authorization: Bearer <token>
        ▼
Backend (FastAPI, :8000)
   /auth/*           registro, login, logout, sesión (SQLite, PBKDF2, token)
   /catalogo         los 3 trámites del MVP
   /tramites         CRUD de espacios de trabajo (workspaces)
   /tramites/{id}/chat   chatbot conversacional con historial
        │
        ▼
   Conocimiento Markdown (docs/05_Development/knowledge-base/) → system prompt → LLM
```

## Cómo ejecutar

### Backend

```bash
cd backend
../bot/venv/bin/pip install -r requirements.txt   # primera vez
../bot/venv/bin/uvicorn main:app --reload --port 8000
```

Crea automáticamente `backend/tramitefacil.db` (SQLite) al arrancar.

### Frontend

```bash
cd frontend
npm install      # primera vez
npm run dev      # http://localhost:3000
```

Si el backend no está en `http://localhost:8000`, crea `frontend/.env.local` con
`NEXT_PUBLIC_API_URL`.

## Funcionalidad cubierta (mapeo a las User Stories del BRD)

| Story | Descripción | Estado |
|---|---|---|
| US-001/002/003 | Registro, login, logout | ✅ |
| US-005/006/007/008 | Catálogo, crear/listar/eliminar workspace | ✅ |
| US-009 | Chat conversacional con historial | ✅ (requiere LLM con cuota) |
| US-010 | Rechazo fuera de dominio | ✅ (en el system prompt) |
| US-011 | Disclaimer visible y permanente | ✅ |
| US-012 | Persistencia del historial de chat | ✅ (SQLite) |
| US-004 | Recuperación de contraseña | 🔲 (requiere envío de correo) |
| US-013/014 | Perfil progresivo (ubicación, editar perfil) | 🔲 |

Reglas de negocio implementadas: contraseña ≥ 8 (AC-001-3), correo único (AC-001-2),
auto-login tras registro (AC-001-4), error genérico de login (AC-002-2), bloqueo tras 5
intentos (AC-002-3), un workspace por trámite (RN-001/AC-006-2), confirmación al eliminar
(AC-008-2), contraseñas hasheadas (RNF-004), sesión con expiración (RNF-005), error claro
si el chatbot no está disponible (RNF-006).

## Limitación conocida

- **Cuota de Gemini agotada**: la `GOOGLE_API_KEY` está en `limit: 0` (free tier). El chat
  responde `503` con un mensaje claro hasta que se habilite facturación o se configure
  OpenRouter en `bot/.env`:
  ```
  PROVEEDOR_LLM=openrouter
  OPENROUTER_API_KEY=...
  OPENROUTER_MODEL=google/gemini-2.0-flash-001
  ```
  Todo lo demás (auth, workspaces, persistencia, disclaimer, UI) es plenamente funcional.

## Notas

- El contenido de los 3 trámites es de referencia general y varía por estado; cada archivo
  y la UI llevan disclaimer. Mantenimiento por eventos (no calendario), fuente primaria gob.mx.
- `docs/CLAUDE.md` raíz y `docker-compose.yml` describen una arquitectura antigua
  (Postgres + Telegram) y siguen desactualizados respecto a este PoC.
