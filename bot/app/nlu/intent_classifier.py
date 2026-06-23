import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from .prompts.system_prompt import PROMPT_SISTEMA_NLU

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODELO_NLU = "gemini-2.0-flash"

_FUNCION_CLASIFICAR_CONSULTA = types.FunctionDeclaration(
    name="clasificar_consulta",
    description=(
        "Clasifica la consulta del usuario sobre trámites gubernamentales y extrae "
        "filtros estructurados para la búsqueda híbrida."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "consulta_semantica": {
                "type": "string",
                "description": "Consulta reformulada para búsqueda semántica vectorial.",
            },
            "dependencia": {
                "type": "string",
                "description": (
                    "Dependencia mencionada explícitamente (ej. SAT, IMSS, SEP). "
                    "Cadena vacía si no aplica."
                ),
            },
            "costo": {
                "type": "string",
                "description": (
                    "Filtro de costo mencionado explícitamente (ej. 'Gratuito'). "
                    "Cadena vacía si no aplica."
                ),
            },
            "tipo": {
                "type": "string",
                "description": "Tipo de trámite mencionado explícitamente. Cadena vacía si no aplica.",
            },
        },
        "required": ["consulta_semantica"],
    },
)

_HERRAMIENTA_NLU = types.Tool(function_declarations=[_FUNCION_CLASIFICAR_CONSULTA])


class ClasificadorIntencion:
    def __init__(self, modelo: str = MODELO_NLU):
        self._cliente = genai.Client(api_key=GOOGLE_API_KEY)
        self._modelo = modelo

    def clasificar(self, mensaje_usuario: str) -> dict:
        respuesta = self._cliente.models.generate_content(
            model=self._modelo,
            contents=mensaje_usuario,
            config=types.GenerateContentConfig(
                system_instruction=PROMPT_SISTEMA_NLU,
                tools=[_HERRAMIENTA_NLU],
                tool_config=types.ToolConfig(
                    function_calling_config=types.FunctionCallingConfig(mode="ANY")
                ),
            ),
        )
        llamada = respuesta.candidates[0].content.parts[0].function_call
        return dict(llamada.args)
