import sys
from pathlib import Path
from typing import List, Optional

# Configurar path para importaciones absolutas del bot
DIRECTORIO_BOT = Path(__file__).resolve().parent.parent.parent
if str(DIRECTORIO_BOT) not in sys.path:
    sys.path.append(str(DIRECTORIO_BOT))

from app.chatbot.schema import UserPromptRequest, UserPromptResponse
from app.nlu.intentions import clasificar_mensaje, extraer_informacion_tramite
from app.retriever.tool import recuperar_tramites
from app.generation.prompts.system_prompt import SYSTEM_PROMPT
from app.core.config import get_llm
from langchain_core.prompts import ChatPromptTemplate

async def gestionar_conversacion(payload: UserPromptRequest) -> UserPromptResponse:
    """
    Coordina el flujo de conversación RAG:
    1. Clasificación NLU de intenciones para obtener un prompt normalizado.
    2. Extracción de modalidades/filtros estructurados de la intención.
    3. Recuperación de los trámites más relevantes desde Chroma.
    4. Generación de respuesta estructurada usando el LLM y el contexto recuperado.
    """
    # 1. Clasificar mensaje del usuario
    clasificacion = clasificar_mensaje(payload.prompt)
    answer_prompt = clasificacion.answer_prompt

    # 2. Extraer información estructurada (filtros de modalidad)
    info_tramite = extraer_informacion_tramite(answer_prompt)

    # 3. Determinar filtro de tipo (modalidad) para la base vectorial
    tipo_filtro = None
    if info_tramite and info_tramite.tipo:
        # Filtrar valores válidos descartando marcadores "NULL"
        tipos_validos = [t for t in info_tramite.tipo if t and str(t).strip().upper() != "NULL"]
        if tipos_validos:
            tipo_filtro = tipos_validos

    # 4. Recuperar trámites usando búsqueda semántica y filtros
    contexto, _ = recuperar_tramites.func(
        query=answer_prompt,
        limit=5,  # Un límite óptimo de documentos recuperados
        tipo=tipo_filtro
    )

    # 5. Inicializar el LLM para la generación final
    llm = get_llm(temperature=0.1)

    # 6. Configurar la plantilla del prompt del sistema
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{pregunta}")
    ])

    # 7. Ejecutar cadena de generación
    chain = prompt_template | llm
    respuesta = await chain.ainvoke({
        "context": contexto,
        "pregunta": payload.prompt
    })

    return UserPromptResponse(response=respuesta.content)
