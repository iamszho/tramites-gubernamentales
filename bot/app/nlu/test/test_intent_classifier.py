import sys
from pathlib import Path

DIRECTORIO_BOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(DIRECTORIO_BOT))

from app.nlu.intent_classifier import ClasificadorIntencion

clasificador = ClasificadorIntencion()


def clasificar_ejemplo(mensaje: str):
    resultado = clasificador.clasificar(mensaje)
    print(f"\n── Mensaje: {mensaje} ──────────────────")
    print(resultado)


clasificar_ejemplo("¿Cómo saco mi acta de nacimiento?")
clasificar_ejemplo("Trámites gratuitos de la SEP")
clasificar_ejemplo("Quiero saber qué necesito para mi pasaporte en el SAT")
