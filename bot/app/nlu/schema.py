from typing import List, Literal
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

    answer_prompt: str = Field(description= "Describe la intencion del usuario, usando un lenguaje formal y sin errores gramaticales" )