import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter

# Cargar variables de entorno desde el archivo .env del bot
DIRECTORIO_BOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(DIRECTORIO_BOT / ".env")

def get_llm(temperature: float = 0.1) -> ChatOpenRouter:
    """
    Inicializa y retorna la instancia del modelo de lenguaje (LLM) configurado
    en las variables de entorno para usar en el chatbot o el clasificador.
    """
    proveedor = os.getenv("PROVEEDOR_LLM", "openrouter").lower()
    
    if proveedor == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY")
        model_name = os.getenv("OPENROUTER_MODEL")
        
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY no está configurada en las variables de entorno.")
            
        return ChatOpenRouter(
            model=model_name,
            temperature=temperature,
            api_key=api_key
        )
    else:
        raise ValueError(f"Proveedor de LLM no soportado o desconocido: {proveedor}")
