from pydantic import BaseModel, Field

class UserPromptRequest(BaseModel):
    prompt: str = Field(
        ..., 
        description="El mensaje o pregunta del ciudadano sobre el trámite gubernamental.",
        examples=["Cómo puedo renovar mi licencia de conducir en línea?"]
    )


class UserPromptResponse(BaseModel):
    response: str = Field(
        ..., 
        description="Respuesta textual generada por el chatbot."
    )
    # En futuras fases se pueden incluir campos adicionales como intenciones, trámites recuperados, etc.
