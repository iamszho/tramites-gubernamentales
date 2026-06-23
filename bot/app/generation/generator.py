"""Generación de la respuesta final del chatbot (paso de generación del RAG).

Proveedor conmutable por variable de entorno `PROVEEDOR_LLM`:

- "gemini" (por defecto): usa el SDK `google-genai` con `GOOGLE_API_KEY`, igual
  que el componente NLU. "Usar lo que ya se tiene".
- "openrouter": usa el SDK `openai` apuntando a la API compatible de OpenRouter
  (`OPENROUTER_API_KEY`, `OPENROUTER_MODEL`), para poder probar otros modelos
  sin cambiar el resto del pipeline.

La elección del proveedor solo afecta este módulo: el retriever y el NLU no
cambian.
"""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from .prompts.system_prompt import PROMPT_SISTEMA_RESPUESTA, construir_prompt_usuario

load_dotenv()

PROVEEDOR_LLM = os.getenv("PROVEEDOR_LLM", "gemini").strip().lower()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODELO_GEMINI = os.getenv("MODELO_GENERACION", "gemini-2.0-flash")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")


class GeneradorRespuesta:
    def __init__(self, proveedor: str = PROVEEDOR_LLM):
        self._proveedor = proveedor
        if proveedor == "openrouter":
            from openai import OpenAI

            if not OPENROUTER_API_KEY:
                raise RuntimeError(
                    "PROVEEDOR_LLM=openrouter pero falta OPENROUTER_API_KEY en el entorno."
                )
            self._cliente = OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL)
            self._modelo = OPENROUTER_MODEL
        elif proveedor == "gemini":
            self._cliente = genai.Client(api_key=GOOGLE_API_KEY)
            self._modelo = MODELO_GEMINI
        else:
            raise ValueError(
                f"PROVEEDOR_LLM no soportado: '{proveedor}'. Usa 'gemini' u 'openrouter'."
            )

    def generar(self, mensaje: str, contexto: str) -> str:
        prompt_usuario = construir_prompt_usuario(mensaje, contexto)
        if self._proveedor == "openrouter":
            return self._generar_openrouter(prompt_usuario)
        return self._generar_gemini(prompt_usuario)

    def _generar_gemini(self, prompt_usuario: str) -> str:
        respuesta = self._cliente.models.generate_content(
            model=self._modelo,
            contents=prompt_usuario,
            config=types.GenerateContentConfig(
                system_instruction=PROMPT_SISTEMA_RESPUESTA,
            ),
        )
        return respuesta.text

    def _generar_openrouter(self, prompt_usuario: str) -> str:
        respuesta = self._cliente.chat.completions.create(
            model=self._modelo,
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA_RESPUESTA},
                {"role": "user", "content": prompt_usuario},
            ],
        )
        return respuesta.choices[0].message.content
