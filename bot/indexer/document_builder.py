from dataclasses import dataclass

import pandas as pd
from langchain_core.documents import Document


@dataclass
class RegistroIndexable:
    id: str
    texto_embedding: str
    documento: Document


def construir_texto_embedding(fila: pd.Series) -> str:
    return (
        f"Nombre del trámite: {fila['Nombre del tramite']}\n"
        f"Dependencia: {fila['Dependencia']}\n"
        f"Descripción: {fila['Descripcion']}"
        f"Requisitos: {fila['Requisitos']}"
        f"Cómo realizarlo: {fila['Como realizar el tramite']}"
    )


def construir_page_content(fila: pd.Series) -> str:
    return (
        f"Nombre del trámite: {fila['Nombre del tramite']}\n"
        f"Dependencia: {fila['Dependencia']}\n"
        f"Tipo: {fila['Tipo']}\n"
        f"Unidad Administrativa: {fila['Unidad Administrativa']}\n"
        f"Descripción: {fila['Descripcion']}\n"
        f"Requisitos: {fila['Requisitos']}\n"
        f"Cómo realizarlo: {fila['Como realizar el tramite']}\n"
        f"Costo: {fila['Costo del tramite']}\n"
        f"Vigencia: {fila['Vigencia']}\n"
        f"Tiempo de respuesta: {fila['Tiempo de respuesta']}"
    )


def construir_metadata(fila: pd.Series) -> dict:
    return {
        "nombre": fila["Nombre del tramite"],
        "dependencia": fila["Dependencia"],
        "tipo": fila["Tipo"],
        "homoclave": fila["Homoclave"],
        "link": fila["Link"],
        "costo": fila["Costo del tramite"],
        "vigencia": fila["Vigencia"],
    }


def construir_registro(fila: pd.Series) -> RegistroIndexable:
    documento = Document(
        page_content=construir_page_content(fila),
        metadata=construir_metadata(fila),
    )
    return RegistroIndexable(
        id=fila["id_unico"],
        texto_embedding=construir_texto_embedding(fila),
        documento=documento,
    )


def construir_registros(df: pd.DataFrame) -> list[RegistroIndexable]:
    return [construir_registro(fila) for _, fila in df.iterrows()]
