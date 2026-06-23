"""Carga del conocimiento curado por trámite (ADR-001)."""

from functools import lru_cache

from config import DIR_KNOWLEDGE, TRAMITES_POR_ID


@lru_cache(maxsize=None)
def cargar_conocimiento(tramite_id: str) -> str:
    tramite = TRAMITES_POR_ID.get(tramite_id)
    if tramite is None:
        raise KeyError(f"Trámite desconocido: {tramite_id}")
    ruta = DIR_KNOWLEDGE / tramite["archivo"]
    return ruta.read_text(encoding="utf-8")
