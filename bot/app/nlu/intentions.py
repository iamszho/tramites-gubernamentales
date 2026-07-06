import sys
from pathlib import Path

# Agregar el directorio raíz del bot al sys.path para importaciones absolutas
DIRECTORIO_BOT = Path(__file__).resolve().parent.parent.parent
if str(DIRECTORIO_BOT) not in sys.path:
    sys.path.append(str(DIRECTORIO_BOT))

from langchain_core.prompts import ChatPromptTemplate
from app.core.config import get_llm
from app.nlu.schema import UserIntention
from app.nlu.prompts.system_prompt import SYSTEM_PROMPT_CLASSIFIER

def clasificar_mensaje(mensaje: str) -> UserIntention:
    """
    Clasifica las intenciones del usuario a partir de su mensaje y retorna el esquema estructurado UserIntention.
    """
    # 1. Obtener el LLM con temperatura baja para clasificación
    llm = get_llm(temperature=0.1)
    
    # 2. Configurar la salida estructurada con el esquema UserIntention
    llm_estructurado = llm.with_structured_output(UserIntention)
    
    # 3. Definir el prompt para la clasificación
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT_CLASSIFIER),
        ("human", "{mensaje}")
    ])
    
    # 4. Construir y ejecutar la cadena
    chain = prompt | llm_estructurado
    return chain.invoke({"mensaje": mensaje})



if __name__ == "__main__":
    # Prueba rápida de clasificación
    mensaje_prueba = "Como se llama el tramite para sacar mi beca de secundaria y cual es la modalidad"
    print(f"Mensaje de prueba: '{mensaje_prueba}'\n")
    
    resultado = clasificar_mensaje(mensaje_prueba)
    
    print(f"Resultado completo: {resultado}")
    print(f"Intenciones detectadas: {resultado.user_intention}")
    print(f"Moldeo de respuesta: {resultado.answer_prompt}")
