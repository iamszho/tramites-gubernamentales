from pathlib import Path

DIRECTORIO_BOT = Path(__file__).resolve().parent.parent

RUTA_CSV = DIRECTORIO_BOT / "data" / "DB_tramitoteca.csv"
DIRECTORIO_CHROMA = DIRECTORIO_BOT / "chroma_db"
NOMBRE_COLECCION = "tramites_gubernamentales"

MODELO_EMBEDDINGS = "paraphrase-multilingual-mpnet-base-v2"
TAMANO_LOTE_EMBEDDINGS = 64
