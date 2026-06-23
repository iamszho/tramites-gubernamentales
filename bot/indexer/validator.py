import random

from .document_builder import RegistroIndexable

# Margen bajo el límite de 128 tokens (~98 palabras en español) del modelo de embeddings
LIMITE_PALABRAS_EMBEDDING = 90


def validar_muestra(registros: list[RegistroIndexable], n: int = 5, semilla: int = 42) -> None:
    muestra = random.Random(semilla).sample(registros, min(n, len(registros)))

    for registro in muestra:
        n_palabras = len(registro.texto_embedding.split())
        print("=" * 80)
        print(f"ID: {registro.id}  ({n_palabras} palabras en texto de embedding)")
        if n_palabras > LIMITE_PALABRAS_EMBEDDING:
            print("  ADVERTENCIA: el texto de embedding podría superar el límite de 128 tokens del modelo")
        print("--- texto_embedding ---")
        print(registro.texto_embedding)
        print("--- page_content ---")
        print(registro.documento.page_content)
        print("--- metadata ---")
        print(registro.documento.metadata)
