import sys
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

# Configurar path para importaciones absolutas del bot
DIRECTORIO_BOT = Path(__file__).resolve().parent.parent.parent
if str(DIRECTORIO_BOT) not in sys.path:
    sys.path.append(str(DIRECTORIO_BOT))

from app.chatbot.schema import UserPromptRequest, UserPromptResponse
from app.nlu.intentions import analizar_consulta_ciudadana
from app.retriever.retriever import recuperar_tramites
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.core.config import get_llm
from langchain.agents import create_agent
from langchain_core.messages import ToolMessage

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


async def _rag_tramites(payload: UserPromptRequest) -> UserPromptResponse:
    """
    Realiza el flujo RAG de forma agéntica (dinámica) para la consulta de trámites.
    Crea un agente de LangChain con acceso a herramientas de NLU y recuperación de Chroma.
    """
    # 1. Inicializar el LLM
    llm = get_llm(temperature=0.1)
    
    # 2. Configurar el agente con las herramientas requeridas y el prompt del sistema
    agent = create_agent(
        model=llm,
        tools=[analizar_consulta_ciudadana, recuperar_tramites],
        system_prompt=SYSTEM_PROMPT,
        debug=False
    )
    
    logger.info("\n" + "="*80)
    logger.info("INICIO DE EJECUCIÓN AGÉNTICA (RAG)")
    logger.info(f"-> Prompt original del usuario: '{payload.prompt}'")
    logger.info("="*80)
    
    # 3. Invocar al agente de forma asíncrona
    resultado = await agent.ainvoke({
        "messages": [("user", payload.prompt)]
    })
    
    # 4. Procesar y loggear ejecuciones de herramientas durante la conversación
    messages = resultado.get("messages", [])
    for message in messages:
        if isinstance(message, ToolMessage):
            logger.info(f"\n[HERRAMIENTA - '{message.name}'] Ejecutada.")
            if message.name == "recuperar_tramites" and hasattr(message, "artifact") and message.artifact:
                # Loggear los resultados recuperados en formato de tabla
                loggear_tabla_tramites(message.artifact)
            else:
                logger.info(f"-> Argumentos/Resultados: {message.content[:250]}...")
    
    # 5. Obtener respuesta final del asistente
    respuesta_final = ""
    if messages:
        ultimo_mensaje = messages[-1]
        respuesta_final = ultimo_mensaje.content
        
    logger.info("\n" + "="*80)
    logger.info("-> Respuesta generada por el agente:")
    logger.info("-" * 80)
    logger.info(respuesta_final)
    logger.info("-" * 80)
    logger.info("="*80 + "\n")

    return UserPromptResponse(response=respuesta_final)


async def gestionar_conversacion(payload: UserPromptRequest) -> UserPromptResponse:
    """
    Coordina el flujo de conversación RAG:
    1. Clasificación NLU de intenciones para obtener un prompt normalizado.
    2. Extracción de modalidades/filtros estructurados de la intención.
    3. Recuperación de los trámites más relevantes desde Chroma.
    4. Generación de respuesta estructurada usando el LLM y el contexto recuperado.
    """
    return await _rag_tramites(payload)
