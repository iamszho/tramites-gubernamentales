"""Generación conversacional del chatbot a partir del conocimiento curado.

ADR-001: el conocimiento del trámite (Markdown) se inyecta en el system prompt; no hay
RAG en el MVP. ADR-002: proveedor conmutable Gemini (por defecto) / OpenRouter.

El system prompt impone los límites del producto:
- Responder SOLO con el conocimiento del trámite activo (RNF-007, no alucinar).
- Rechazar temas fuera de dominio y redirigir al portal oficial (RF-015, US-010).
- Declarar cuando no tiene información suficiente (RF-016).
- Tono conversacional, sin jerga (RF-019).
- Recomendar verificar la fuente oficial (RN-003).
"""

import os

from config import DISCLAIMER

PROVEEDOR_LLM = os.getenv("PROVEEDOR_LLM", "gemini").strip().lower()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODELO_GEMINI = os.getenv("MODELO_GENERACION", "gemini-2.0-flash")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")


def construir_system_prompt(tramite_nombre: str, conocimiento_md: str) -> str:
    return f"""Eres el asistente de TramiteFácil, especializado EXCLUSIVAMENTE en el trámite \
"{tramite_nombre}" (trámite vehicular en México).

Tu CONOCIMIENTO es únicamente el siguiente contenido. No uses información externa ni \
inventes datos que no estén aquí:

--- INICIO DEL CONOCIMIENTO ---
{conocimiento_md}
--- FIN DEL CONOCIMIENTO ---

Reglas estrictas:
1. Responde solo preguntas sobre "{tramite_nombre}". Si el usuario pregunta por otro \
trámite (otro trámite vehicular, SAT, INE, IMSS, pasaporte, etc.) o un tema ajeno, dile \
con amabilidad que en esta versión solo puedes ayudar con "{tramite_nombre}" y sugiérele \
consultar el portal oficial correspondiente.
2. Responde ÚNICAMENTE con base en el conocimiento de arriba. Si la pregunta es sobre el \
trámite pero el conocimiento no contiene la respuesta, dilo explícitamente ("no tengo esa \
información con precisión") en vez de inventar. Nunca presentes datos inventados como \
ciertos.
3. Recuerda que requisitos, costos y procesos varían por estado; cuando des cifras o \
listas, aclara que pueden variar por entidad y recomienda verificar en el portal oficial.
4. Usa un tono cercano, claro y conversacional, en español, sin lenguaje burocrático. \
Sé conciso y, cuando ayude, usa listas o pasos numerados.
5. Si procede, cierra recomendando verificar en el portal oficial del estado.

Recuerda este aviso al usuario cuando sea pertinente: {DISCLAIMER}"""


class ClienteLLM:
    def __init__(self):
        self._proveedor = PROVEEDOR_LLM
        if self._proveedor == "openrouter":
            from openai import OpenAI

            if not OPENROUTER_API_KEY:
                raise RuntimeError("PROVEEDOR_LLM=openrouter pero falta OPENROUTER_API_KEY.")
            self._cliente = OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL)
            self._modelo = OPENROUTER_MODEL
        elif self._proveedor == "gemini":
            from google import genai

            self._genai = genai
            self._cliente = genai.Client(api_key=GOOGLE_API_KEY)
            self._modelo = MODELO_GEMINI
        else:
            raise ValueError(f"PROVEEDOR_LLM no soportado: '{self._proveedor}'.")

    def responder(
        self, system_prompt: str, historial: list[dict], mensaje: str
    ) -> str:
        """`historial` es una lista de {'rol': 'user'|'assistant', 'contenido': str}."""
        if self._proveedor == "openrouter":
            return self._responder_openrouter(system_prompt, historial, mensaje)
        return self._responder_gemini(system_prompt, historial, mensaje)

    def _responder_gemini(self, system_prompt, historial, mensaje) -> str:
        from google.genai import types

        contents = []
        for m in historial:
            rol = "model" if m["rol"] == "assistant" else "user"
            contents.append(
                types.Content(role=rol, parts=[types.Part(text=m["contenido"])])
            )
        contents.append(types.Content(role="user", parts=[types.Part(text=mensaje)]))

        respuesta = self._cliente.models.generate_content(
            model=self._modelo,
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=system_prompt),
        )
        return respuesta.text

    def _responder_openrouter(self, system_prompt, historial, mensaje) -> str:
        mensajes = [{"role": "system", "content": system_prompt}]
        for m in historial:
            rol = "assistant" if m["rol"] == "assistant" else "user"
            mensajes.append({"role": rol, "content": m["contenido"]})
        mensajes.append({"role": "user", "content": mensaje})

        respuesta = self._cliente.chat.completions.create(
            model=self._modelo, messages=mensajes
        )
        return respuesta.choices[0].message.content
