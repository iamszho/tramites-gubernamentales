# TramiteFácil

Plataforma web (PoC) que ayuda a ciudadanos mexicanos a prepararse para **trámites
vehiculares** (licencia de conducir, verificación vehicular y cambio de placas) mediante un
chatbot conversacional, con autenticación y espacios de trabajo por trámite.

El chatbot responde con **conocimiento curado en Markdown** inyectado al prompt del LLM
(sin RAG en el MVP; ver `docs/05_Development/technical_decisions.md`).

> Para el detalle del producto, ver `docs/`. Para el mapeo del PoC a las User Stories y notas
> de arquitectura, ver `POC_README.md`.

## Estructura del proyecto

- `backend/` — API en **FastAPI** (auth, trámites/workspaces, chat). Persistencia con SQLite.
- `frontend/` — Interfaz en **Next.js / React** (login, dashboard, chat por trámite).
- `bot/` — Motor **RAG** sobre trámites federales (no usado por el MVP; se conserva para V2+).
  Aquí viven también el entorno virtual (`bot/venv`) y el archivo de claves (`bot/.env`).
- `docs/` — Documentación del producto (problem statement, BRD, user stories, ADRs).

## Requisitos

- **Python 3.11+**
- **Node.js 18+** y npm

---

## Puesta en marcha en local

### 1. Entorno de Python y dependencias del backend

```bash
# Desde la raíz del repositorio:
python -m venv bot/venv
source bot/venv/bin/activate          # Linux/Mac
# bot\venv\Scripts\activate           # Windows

pip install -r backend/requirements.txt
```

### 2. Configurar las claves de API (archivo `bot/.env`)

El backend lee las claves desde **`bot/.env`**. Crea el archivo a partir de la plantilla:

```bash
cp bot/.env.example bot/.env
```

Edita `bot/.env` y completa según el proveedor de LLM que vayas a usar:

```bash
# Token de Hugging Face (necesario solo si vas a reconstruir la base RAG del bot; opcional para el MVP)
HF_TOKEN=tu_token_de_hugging_face

# --- Opción A: Google Gemini (por defecto) ---
GOOGLE_API_KEY=tu_google_api_key          # https://aistudio.google.com/apikey
# PROVEEDOR_LLM=gemini                     # valor por defecto si se omite
# MODELO_GENERACION=gemini-2.0-flash

# --- Opción B: OpenRouter (para usar otros modelos) ---
PROVEEDOR_LLM=openrouter
OPENROUTER_API_KEY=sk-or-tu-clave         # https://openrouter.ai/keys
OPENROUTER_MODEL=meta-llama/llama-3.3-70b-instruct:free
```

Notas sobre el LLM:

- **Por defecto usa Gemini.** Para cambiar a OpenRouter, pon `PROVEEDOR_LLM=openrouter` y la
  clave `OPENROUTER_API_KEY`.
- **Modelos de OpenRouter** (slugs válidos, cambian con el tiempo — consulta
  https://openrouter.ai/models):
  - Gratis: `meta-llama/llama-3.3-70b-instruct:free`, `qwen/qwen3-next-80b-a3b-instruct:free`
  - De pago (mejor español): `google/gemini-2.5-flash`, `google/gemini-2.5-flash-lite`
- Para usar modelos **`:free`**, OpenRouter exige activar una opción en
  **Settings → Privacy** ("Enable free endpoints…"). Si no, devuelve un error de *data policy*.
- **Importante:** el `.env` se lee al **arrancar** el backend. Si cambias una clave o el
  modelo, **reinicia** el proceso de uvicorn.

### 3. Levantar el backend (FastAPI, puerto 8000)

```bash
cd backend
../bot/venv/bin/uvicorn main:app --reload --port 8000
# (o, con el venv activado: uvicorn main:app --reload --port 8000)
```

Crea automáticamente la base de datos `backend/tramitefacil.db` al iniciar.
Verifica que responde: http://127.0.0.1:8000/health

### 4. Levantar el frontend (Next.js, puerto 3000)

En otra terminal:

```bash
cd frontend
npm install        # solo la primera vez
npm run dev
```

Abre **http://localhost:3000**, regístrate y empieza a usar la plataforma.

> El frontend apunta al backend en `http://127.0.0.1:8000` por defecto. Si lo cambias de
> puerto/host, crea `frontend/.env.local` (ver `frontend/.env.local.example`) con
> `NEXT_PUBLIC_API_URL`. Se usa `127.0.0.1` y no `localhost` a propósito: en muchos sistemas
> Linux `localhost` resuelve a IPv6 (`::1`) y uvicorn solo escucha en IPv4 por defecto.

---

## Limitación conocida

El registro, login, dashboard y persistencia funcionan sin LLM. El **chat** requiere una clave
de LLM con cuota disponible:

- Si Gemini devuelve `429 RESOURCE_EXHAUSTED`, la cuota del free tier está agotada → habilita
  facturación o usa OpenRouter (Opción B de arriba).
- Si el chat falla, el backend responde `503` con el mensaje de error exacto del proveedor para
  facilitar el diagnóstico.

## Documentación adicional

- `POC_README.md` — alcance del PoC y mapeo a las User Stories del BRD.
- `docs/` — problem statement, BRD, user stories y decisiones técnicas (ADRs).
