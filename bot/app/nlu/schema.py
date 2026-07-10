from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class UserIntention(BaseModel):
    user_intention: List[
        Literal[
            "nombre",
            "dependencia",
            "descripcion",
            "tipo",
            "unidad_administrativa",
            "homoclave",
            "link",
            "requisitos",
            "como_realizar_el_tramite",
            "costo",
            "vigencia",
            "tiempo_de_respuesta"
        ]   
    ] = Field(description="Lista de categorías que mejor describen las intenciones presentes en la solicitud del usuario.")

    answer_prompt: str = Field(description= "Describe la intencion del usuario, usando un lenguaje formal y sin errores gramaticales. Corrige ortografia y gramatica si es necesario." )


import json
from pydantic import field_validator

class TramiteInformation(BaseModel):
    tipo: Optional[List[Literal["En línea", "Presencial", "Medios Alternativos", "NULL"]]] = Field(
        None, 
        description="Modalidad o canal de atención deseado para realizar el trámite. Si no se dice explícitamente la modalidad, usa NULL"
    )

    @field_validator("tipo", mode="before")
    @classmethod
    def parse_tipo(cls, v):
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                return [v]
        return v