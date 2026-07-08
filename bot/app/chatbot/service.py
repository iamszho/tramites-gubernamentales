import sys
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

# Configurar path para importaciones absolutas del bot
DIRECTORIO_BOT = Path(__file__).resolve().parent.parent.parent
if str(DIRECTORIO_BOT) not in sys.path:
    sys.path.append(str(DIRECTORIO_BOT))

from app.chatbot.schema import UserPromptRequest, UserPromptResponse
from app.nlu.intentions import clasificar_mensaje, extraer_informacion_tramite
from app.retriever.tool import recuperar_tramites
from app.generation.prompts.system_prompt import SYSTEM_PROMPT
from app.core.config import get_llm
from langchain_core.prompts import ChatPromptTemplate

# Configurar Logger para el servicio
logger = logging.getLogger("app.chatbot.service")
logging.basicConfig(level=logging.INFO)

def loggear_tabla_tramites(resultados: Dict[str, Any]):
    """
    Formatea y registra en los logs los trámites recuperados en formato de tabla ASCII.
    """
    if not resultados or not resultados.get("ids") or not resultados["ids"][0]:
        logger.info("\n[!] No se recuperaron trámites de la base de datos vectorial.")
        return
    
    ids = resultados["ids"][0]
    metadatas = resultados["metadatas"][0]
    distances = resultados.get("distances", [[]])[0]
    
    headers = ["#", "ID Único", "Nombre del Trámite", "Dependencia", "Tipo", "Distancia Coseno"]
    rows = []
    
    for i in range(len(ids)):
        meta = metadatas[i] if i < len(metadatas) else {}
        dist = f"{distances[i]:.4f}" if i < len(distances) else "N/A"
        
        # Obtener y truncar nombre del trámite
        nombre = meta.get("nombre") or meta.get("Nombre del tramite") or "Sin Nombre"
        if len(nombre) > 40:
            nombre = nombre[:37] + "..."
            
        # Obtener y truncar dependencia
        dep = meta.get("dependencia") or meta.get("Dependencia") or "Sin Dependencia"
        if len(dep) > 25:
            dep = dep[:22] + "..."
            
        tipo = meta.get("tipo") or meta.get("Tipo") or "N/A"
        rows.append([str(i+1), str(ids[i]), nombre, dep, tipo, dist])
        
    # Calcular anchos de columna para alineación
    widths = [len(h) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            widths[idx] = max(widths[idx], len(val))
            
    # Construir líneas de la tabla
    separator = "+" + "+".join(["-" * (w + 2) for w in widths]) + "+"
    header_row = "|" + "|".join([f" {headers[j].ljust(widths[j])} " for j in range(len(headers))]) + "|"
    
    table_lines = [
        "",
        "Trámites Recuperados:",
        separator,
        header_row,
        separator
    ]
    
    for row in rows:
        data_row = "|" + "|".join([f" {row[j].ljust(widths[j])} " for j in range(len(row))]) + "|"
        table_lines.append(data_row)
        
    table_lines.append(separator)
    table_lines.append("")
    
    # Imprimir tabla estructurada
    logger.info("\n".join(table_lines))


async def gestionar_conversacion(payload: UserPromptRequest) -> UserPromptResponse:
    """
    Coordina el flujo de conversación RAG:
    1. Clasificación NLU de intenciones para obtener un prompt normalizado.
    2. Extracción de modalidades/filtros estructurados de la intención.
    3. Recuperación de los trámites más relevantes desde Chroma.
    4. Generación de respuesta estructurada usando el LLM y el contexto recuperado.
    """
    
    # =========================================================================
    # ETAPA 1: CLASIFICACIÓN Y EXTRACCIÓN
    # =========================================================================
    logger.info("\n" + "="*80)
    logger.info("ETAPA 1: CLASIFICACIÓN Y EXTRACCIÓN (NLU)")
    logger.info(f"-> Prompt original del usuario: '{payload.prompt}'")
    
    # Clasificar mensaje del usuario
    clasificacion = clasificar_mensaje(payload.prompt)
    answer_prompt = clasificacion.answer_prompt
    logger.info(f"-> Categorías de intención detectadas: {clasificacion.user_intention}")
    logger.info(f"-> Prompt normalizado (para búsqueda semántica): '{answer_prompt}'")

    # Extraer información estructurada (filtros de modalidad)
    info_tramite = extraer_informacion_tramite(answer_prompt)

    # Determinar filtro de tipo (modalidad) para la base vectorial
    tipo_filtro = None
    if info_tramite and info_tramite.tipo:
        # Filtrar valores válidos descartando marcadores "NULL"
        tipos_validos = [t for t in info_tramite.tipo if t and str(t).strip().upper() != "NULL"]
        if tipos_validos:
            tipo_filtro = tipos_validos
    logger.info(f"-> Filtro por Modalidad (Tipo): {tipo_filtro}")
    logger.info("="*80)

    # =========================================================================
    # ETAPA 2: RECUPERACIÓN (Vector DB)
    # =========================================================================
    logger.info("\n" + "="*80)
    logger.info("ETAPA 2: RECUPERACIÓN (Búsqueda Vectorial)")
    logger.info(f"-> Consultando Chroma con límite de 5 trámites...")
    
    # Recuperar trámites usando búsqueda semántica y filtros
    contexto, resultados = recuperar_tramites.func(
        query=answer_prompt,
        limit=5,  # Límite de 5 documentos
        tipo=tipo_filtro
    )
    
    # Imprimir logs de los resultados recuperados en formato de tabla
    loggear_tabla_tramites(resultados)
    logger.info("="*80)

    # =========================================================================
    # ETAPA 3: GENERACIÓN
    # =========================================================================
    logger.info("\n" + "="*80)
    logger.info("ETAPA 3: GENERACIÓN (LLM)")
    logger.info("-> Generando respuesta contextual estructurada...")
    
    # Inicializar el LLM para la generación final
    llm = get_llm(temperature=0.1)

    # Configurar la plantilla del prompt del sistema
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{pregunta}")
    ])

    # Ejecutar cadena de generación
    chain = prompt_template | llm
    respuesta = await chain.ainvoke({
        "context": contexto,
        "pregunta": payload.prompt
    })
    
    logger.info("-> Respuesta generada por el modelo:")
    logger.info("-" * 80)
    logger.info(respuesta.content)
    logger.info("-" * 80)
    logger.info("="*80 + "\n")

    return UserPromptResponse(response=respuesta.content)
