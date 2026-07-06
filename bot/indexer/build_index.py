import argparse

import chromadb

from .config import DIRECTORIO_CHROMA, NOMBRE_COLECCION, RUTA_CSV
from .data_loader import cargar_tramites
from .document_builder import construir_registros
from .embedder import GeneradorEmbeddings
from .validator import validar_muestra


def indexar(limite: int | None = None, solo_validar: bool = False, tamano_muestra: int = 5) -> None:
    df = cargar_tramites(RUTA_CSV)
    if limite is not None:
        df = df.head(limite)

    registros = construir_registros(df)
    print(f"{len(registros)} registros construidos a partir de {RUTA_CSV.name}")

    validar_muestra(registros, n=tamano_muestra)

    if solo_validar:
        print("Modo --solo-validar: no se generaron embeddings ni se indexó en Chroma.")
        return

    generador = GeneradorEmbeddings()
    embeddings = generador.generar([registro.texto_embedding for registro in registros])

    cliente = chromadb.PersistentClient(path=str(DIRECTORIO_CHROMA))
    coleccion = cliente.get_or_create_collection(
        NOMBRE_COLECCION,
        metadata={"hnsw:space": "cosine"},
    )
    coleccion.upsert(
        ids=[registro.id for registro in registros],
        embeddings=embeddings,
        documents=[registro.documento.page_content for registro in registros],
        metadatas=[registro.documento.metadata for registro in registros],
    )
    print(f"{len(registros)} registros indexados en la colección '{NOMBRE_COLECCION}' ({DIRECTORIO_CHROMA})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Indexa trámites gubernamentales en Chroma")
    parser.add_argument("--limite", type=int, default=None, help="Procesar solo las primeras N filas (pruebas)")
    parser.add_argument("--solo-validar", action="store_true", help="Construir y validar muestra sin indexar")
    parser.add_argument("--tamano-muestra", type=int, default=5, help="Cantidad de registros a imprimir en la validación")
    args = parser.parse_args()
    indexar(limite=args.limite, solo_validar=args.solo_validar, tamano_muestra=args.tamano_muestra)


if __name__ == "__main__":
    main()
