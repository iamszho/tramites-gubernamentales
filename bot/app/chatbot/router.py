from fastapi import APIRouter, HTTPException, status
from app.chatbot.schema import UserPromptRequest, UserPromptResponse
from app.chatbot.service import gestionar_conversacion

router = APIRouter(
    prefix="/api",
    tags=["Chatbot"]
)


@router.post(
    "/user-prompt", 
    response_model=UserPromptResponse,
    status_code=status.HTTP_200_OK,
    summary="Procesar consulta del usuario",
    description="Recibe la consulta del ciudadano, analiza la intención, busca trámites en la base vectorial y genera una respuesta."
)
async def procesar_user_prompt(payload: UserPromptRequest):
    """
    Endpoint principal para recibir y procesar el prompt del usuario.
    Invoca la función de servicio para orquestar el flujo de conversación.
    """
    try:
        return await gestionar_conversacion(payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al procesar el prompt: {str(e)}"
        )
