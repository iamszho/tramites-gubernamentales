"""Orquestación del pipeline RAG: NLU -> retriever híbrido -> generación.

Es la fachada que consume el backend FastAPI. Mantiene la lógica de negocio en
`bot/app/` (junto al NLU ya existente) y deja el backend como una capa HTTP
delgada.
"""

from dataclasses import dataclass

from app.generation.generator import GeneradorRespuesta
from app.nlu.intent_classifier import ClasificadorIntencion
from app.retriever.retriever import RecuperadorHibrido, TramiteRecuperado


@dataclass
class Fuente:
    nombre: str
    dependencia: str
    link: str


@dataclass
class RespuestaChat:
    respuesta: str
    fuentes: list[Fuente]
    intencion: dict


class PipelineRAG:
    def __init__(self, k: int = 4):
        self._clasificador = ClasificadorIntencion()
        self._recuperador = RecuperadorHibrido(k=k)
        self._generador = GeneradorRespuesta()

    def _formatear_contexto(self, tramites: list[TramiteRecuperado]) -> str:
        bloques = []
        for i, t in enumerate(tramites, start=1):
            bloques.append(f"[Trámite {i}]\n{t.contenido}\nLink: {t.link}")
        return "\n\n".join(bloques)

    def responder(self, mensaje: str) -> RespuestaChat:
        intencion = self._clasificador.clasificar(mensaje)

        tramites = self._recuperador.recuperar(
            consulta_semantica=intencion.get("consulta_semantica", mensaje),
            dependencia=intencion.get("dependencia", ""),
            costo=intencion.get("costo", ""),
            tipo=intencion.get("tipo", ""),
        )

        if not tramites:
            return RespuestaChat(
                respuesta=(
                    "No encontré trámites relacionados con tu consulta. "
                    "¿Puedes reformularla con más detalle?"
                ),
                fuentes=[],
                intencion=intencion,
            )

        contexto = self._formatear_contexto(tramites)
        texto = self._generador.generar(mensaje, contexto)

        fuentes = [
            Fuente(nombre=t.nombre, dependencia=t.dependencia, link=t.link) for t in tramites
        ]
        return RespuestaChat(respuesta=texto, fuentes=fuentes, intencion=intencion)
