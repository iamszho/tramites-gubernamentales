from sentence_transformers import SentenceTransformer
import os 
from .config import MODELO_EMBEDDINGS, TAMANO_LOTE_EMBEDDINGS
from dotenv import load_dotenv

load_dotenv ()

HF_TOKEN = os.getenv("HF_TOKEN")

class GeneradorEmbeddings:
    def __init__(self, nombre_modelo: str = MODELO_EMBEDDINGS):
        self._modelo = SentenceTransformer(nombre_modelo, token=HF_TOKEN)

    def generar(self, textos: list[str], tamano_lote: int = TAMANO_LOTE_EMBEDDINGS) -> list[list[float]]:
        vectores = self._modelo.encode(
            textos,
            batch_size=tamano_lote,
            show_progress_bar=True,
            convert_to_numpy=True,
        )
        return vectores.tolist()
