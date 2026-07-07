import sys
from pathlib import Path
from typing import List, Optional, Union, Tuple, Dict, Any

# Agregar el directorio raíz del bot al sys.path para importaciones absolutas
DIRECTORIO_BOT = Path(__file__).resolve().parent.parent.parent
if str(DIRECTORIO_BOT) not in sys.path:
    sys.path.append(str(DIRECTORIO_BOT))

import chromadb
from langchain_core.tools import tool
from indexer.config import DIRECTORIO_CHROMA, NOMBRE_COLECCION, MODELO_EMBEDDINGS
from indexer.embedder import GeneradorEmbeddings

# Inicializar recursos a nivel de módulo
_cliente = chromadb.PersistentClient(path=str(DIRECTORIO_CHROMA))
_coleccion = _cliente.get_or_create_collection(
    NOMBRE_COLECCION, 
    metadata={"hnsw:space": "cosine"}
)
_generador_embeddings = GeneradorEmbeddings(nombre_modelo=MODELO_EMBEDDINGS)


@tool(response_format="content_and_artifact")
def recuperar_tramites(
    query: str,
    limit: int = 3,
    tipo: Optional[Union[str, List[str]]] = None,
    dependencia: Optional[str] = None,
    costo: Optional[str] = None,
    homoclave: Optional[str] = None
) -> Tuple[str, Dict[str, Any]]:
    """
    Recupera trámites gubernamentales de la base de datos vectorial Chroma usando búsqueda semántica.
    Opcionalmente aplica filtros exactos en metadatos (tipo, dependencia, costo, homoclave).

    Args:
        query: La consulta semántica del usuario (ej. 'cómo renovar mi pasaporte').
        limit: Número máximo de trámites a recuperar. Por defecto es 3.
        tipo: Opcional. Tipo(s) o modalidad(es) de atención del trámite ('En línea', 'Presencial', 'Medios Alternativos').
        dependencia: Opcional. Dependencia gubernamental específica (ej. 'SEP', 'IMSS', 'SAT').
        costo: Opcional. Filtro por costo del trámite (ej. 'Gratuito', 'Sin costo').
        homoclave: Opcional. Identificador alfanumérico único del trámite.
        
    Returns:
        tuple: Un par (content, artifact) donde:
            - content: Cadena de texto formateada para el consumo directo del LLM.
            - artifact: Diccionario con la respuesta cruda de Chroma (documentos, metadatos, distancias, ids).
    """
    # 1. Generar el embedding para la consulta de entrada
    vectores = _generador_embeddings.generar([query])
    vector_query = vectores[0]

    # 2. Construir cláusulas de filtrado dinámicas para Chroma
    where_clause = {}
    conditions = []

    # Filtrar por tipo (modalidad)
    if tipo:
        tipos_lista = [tipo] if isinstance(tipo, str) else tipo
        # Filtrar valores no nulos y descartar marcadores 'NULL'
        tipos_filtrados = [t for t in tipos_lista if t and str(t).strip().upper() != "NULL"]
        if tipos_filtrados:
            if len(tipos_filtrados) == 1:
                conditions.append({"tipo": tipos_filtrados[0]})
            else:
                conditions.append({"$or": [{"tipo": t} for t in tipos_filtrados]})

    # Filtrar por dependencia
    if dependencia and str(dependencia).strip():
        conditions.append({"dependencia": dependencia.strip()})

    # Filtrar por costo
    if costo and str(costo).strip():
        conditions.append({"costo": costo.strip()})

    # Filtrar por homoclave
    if homoclave and str(homoclave).strip():
        conditions.append({"homoclave": homoclave.strip()})

    # Establecer la estructura final de 'where'
    if len(conditions) == 1:
        where_clause = conditions[0]
    elif len(conditions) > 1:
        where_clause = {"$and": conditions}

    # 3. Consultar la colección en Chroma
    resultados = _coleccion.query(
        query_embeddings=[vector_query],
        n_results=limit,
        where=where_clause if where_clause else None
    )

    # 4. Validar si obtuvimos resultados
    if not resultados or not resultados.get("documents") or not resultados["documents"][0]:
        return "No se encontraron trámites que coincidan con la búsqueda.", resultados

    # 5. Formatear la salida para el LLM (content)
    formatted_docs = []
    for i, (doc, metadata, doc_id) in enumerate(zip(
        resultados["documents"][0],
        resultados["metadatas"][0],
        resultados["ids"][0]
    )):
        distancia = resultados["distances"][0][i] if "distances" in resultados and resultados["distances"] else None
        
        doc_str = f"### [Resultado {i+1}] ID Único: {doc_id}"
        if distancia is not None:
            # Reportar distancia del vector para depuración e información del LLM
            doc_str += f" | Distancia Coseno: {distancia:.4f}"
        
        doc_str += f"\n{doc}\n"
        
        # Citar enlace de fuente oficial si está disponible en metadatos
        link = metadata.get("link") or metadata.get("Link")
        if link:
            doc_str += f"Enlace Oficial: {link}\n"
            
        formatted_docs.append(doc_str)

    content = "\n---\n".join(formatted_docs)
    return content, resultados


if __name__ == "__main__":
    # Prueba de ejecución rápida de la función/herramienta
    print("Iniciando prueba de la herramienta de recuperación...")
    
    consulta = "Solicitar una beca para la secundaria de mi hijo"
    print(f"Consulta: '{consulta}' con límite de 2 resultados.")
    
    contenido, artefacto = recuperar_tramites.func(query=consulta)
    
    print("\n" + "="*30 + " CONTENIDO DE RESPUESTA (Para el LLM) " + "="*30)
    print(contenido)
    print("="*98 + "\n")
    
    print("="*30 + " ARTEFACTO (Para el Sistema) " + "="*30)
    print(f"Total de IDs recuperados: {len(artefacto['ids'][0])}")
    print(f"IDs: {artefacto['ids'][0]}")
    print(f"Distancias obtenidas: {artefacto.get('distances', [[]])[0]}")
    print("="*98)
