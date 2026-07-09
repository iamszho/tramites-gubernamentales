import sys
from pathlib import Path

# Agregar el directorio raíz del bot al sys.path para importaciones absolutas
DIRECTORIO_BOT = Path(__file__).resolve().parent.parent.parent
if str(DIRECTORIO_BOT) not in sys.path:
    sys.path.append(str(DIRECTORIO_BOT))

from langchain_core.prompts import ChatPromptTemplate
from app.core.config import get_llm
from app.nlu.schema import UserIntention, TramiteInformation
from app.prompts.system_prompt import SYSTEM_PROMPT_CLASSIFIER, SYSTEM_PROMPT_EXTRACTOR

def clasificar_mensaje (mensaje: str) -> UserIntention:
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

def extraer_informacion_tramite(answer_prompt: str) -> TramiteInformation:
    """
    Analiza la descripción del mensaje del usuario (answer_prompt) para extraer información estructurada
    como la modalidad de atención (tipo) deseada.
    """
    # 1. Obtener el LLM con temperatura baja para la extracción de información estructurada
    llm = get_llm(temperature=0.1)
    
    # 2. Configurar la salida estructurada con el esquema TramiteInformation
    llm_estructurado = llm.with_structured_output(TramiteInformation)
    
    # 3. Definir el prompt de extracción
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT_EXTRACTOR),
        ("human", "{answer_prompt}")
    ])
    
    # 4. Construir y ejecutar la cadena
    chain = prompt | llm_estructurado
    return chain.invoke({"answer_prompt": answer_prompt})


if __name__ == "__main__":
    # Prueba 1: Con modalidad explícita (Presencial)
    mensaje_prueba_1 = "Como se llama el tramite para sacar mi beca de secundaria y si puedo hacerlo en linea"
    print(f"--- PRUEBA 1 ---")
    print(f"Mensaje original: '{mensaje_prueba_1}'\n")
    
    res_clasificacion_1 = clasificar_mensaje(mensaje_prueba_1)
    print(f"Intenciones detectadas: {res_clasificacion_1.user_intention}")
    print(f"Moldeo de respuesta (answer_prompt): '{res_clasificacion_1.answer_prompt}'\n")
    
    res_info_1 = extraer_informacion_tramite(res_clasificacion_1.answer_prompt)
    print(f"Información extraída (tipo): {res_info_1.tipo}")
    print(f"Diccionario filtrado: {res_info_1.model_dump(exclude_none=True)}\n")
    
    print("=" * 60)
    
    # Prueba 2: Sin modalidad explícita (Debería retornar ["NULL"] o similar según la regla)
    mensaje_prueba_2 = "Quiero saber los requisitos para el acta de nacimiento"
    print(f"\n--- PRUEBA 2 ---")
    print(f"Mensaje original: '{mensaje_prueba_2}'\n")
    
    res_clasificacion_2 = clasificar_mensaje(mensaje_prueba_2)
    print(f"Intenciones detectadas: {res_clasificacion_2.user_intention}")
    print(f"Moldeo de respuesta (answer_prompt): '{res_clasificacion_2.answer_prompt}'\n")
    
    res_info_2 = extraer_informacion_tramite(res_clasificacion_2.answer_prompt)
    print(f"Información extraída (tipo): {res_info_2.tipo}")
    print(f"Diccionario filtrado: {res_info_2.model_dump(exclude_none=True)}\n")

