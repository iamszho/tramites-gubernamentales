import chromadb
from pathlib import Path
from sentence_transformers import SentenceTransformer

DIRECTORIO_BOT = Path(__file__).resolve().parents[2]
cliente = chromadb.PersistentClient(path=str(DIRECTORIO_BOT / "chroma_db"))
coleccion = cliente.get_or_create_collection("tramites_gubernamentales")

modelo = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")

def conteo_regitros (): 
    print(f"Registros en Chroma: {coleccion.count()}")

def analisis_contenido (texto: str): 
    vector_pregunta = modelo.encode(texto).tolist ()
    resultados = coleccion.query(
        query_embeddings=[vector_pregunta]
        #n_results=3
    )
    for i, doc in enumerate(resultados["documents"][0]):
        print(f"\n── Resultado {i+1} ──────────────────")
        print(doc[:300])  # primeras 300 caracteres del page_content
        print("Metadata:", resultados["metadatas"][0][i])   

def busqueda_con_filtro (): 

    vector_pregunta = modelo.encode("Quiero sacar mi licencia de mi carro").tolist()
    
    resultados = coleccion.query(
        # query_embeddings=[vector_pregunta],
        n_results=3,
        where={
            "tipo": "En línea",
            "dependencia": "Secretaría de Movilidad y Transporte",
        }   # <-- AQUÍ PONES TU FILTRO
    )

    for i, doc in enumerate(resultados["documents"][0]):
        print(f"\n── Resultado {i+1} ──────────────────")
        print(doc[:300])
        print("Metadata:", resultados["metadatas"][0][i])

# busqueda_con_filtro ()
texto = "Ya pasó un año desde que inauguramos la estación de carga de combustible, ¿cómo se reporta la revisión anual obligatoria de mantenimiento ante la ASEA?" 
analisis_contenido (texto)