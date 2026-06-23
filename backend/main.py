"""Backend FastAPI de TramiteFácil (PoC).

Plataforma de asistencia para trámites vehiculares: autenticación, espacios de trabajo
por trámite y chatbot conversacional con conocimiento curado en Markdown (ADR-001).

El motor RAG previo vive en `bot/app/` y no se usa en este MVP (ver ADR-001); se conserva
para una futura expansión a trámites federales.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import ORIGEN_CORS_REGEX, ORIGENES_CORS
from db import init_db
from routers import auth, chat, tramites


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="TramiteFácil — PoC", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES_CORS,
    allow_origin_regex=ORIGEN_CORS_REGEX,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tramites.router)
app.include_router(chat.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
