import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.chatbot.router import router as chatbot_router

app = FastAPI(
    title="Chatbot de Trámites Gubernamentales",
    description="API del Chatbot RAG para consultar trámites administrativos en México.",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modificar en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir el router del chatbot
app.include_router(chatbot_router)

@app.get("/", tags=["General"])
async def root():
    return {
        "mensaje": "API del Chatbot de Trámites Gubernamentales funcionando correctamente.",
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
