"""Chatbot de asistencia por trámite (Epic 3)."""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from config import TRAMITES_POR_ID
from db import get_db
from deps import get_current_user
from knowledge import cargar_conocimiento
from llm import ClienteLLM, construir_system_prompt
from schemas import ChatIn, ChatOut

router = APIRouter(tags=["chat"])

_cliente_llm: ClienteLLM | None = None


def _get_llm() -> ClienteLLM:
    global _cliente_llm
    if _cliente_llm is None:
        _cliente_llm = ClienteLLM()
    return _cliente_llm


@router.post("/tramites/{workspace_id}/chat", response_model=ChatOut)
def chatear(
    workspace_id: int,
    datos: ChatIn,
    db: sqlite3.Connection = Depends(get_db),
    usuario: sqlite3.Row = Depends(get_current_user),
) -> ChatOut:
    ws = db.execute(
        "SELECT id, tramite_id FROM workspaces WHERE id = ? AND usuario_id = ?",
        (workspace_id, usuario["id"]),
    ).fetchone()
    if ws is None:
        raise HTTPException(status_code=404, detail="Trámite no encontrado.")

    tramite = TRAMITES_POR_ID[ws["tramite_id"]]
    conocimiento = cargar_conocimiento(ws["tramite_id"])
    system_prompt = construir_system_prompt(tramite["nombre"], conocimiento)

    historial = [
        {"rol": m["rol"], "contenido": m["contenido"]}
        for m in db.execute(
            "SELECT rol, contenido FROM mensajes WHERE workspace_id = ? ORDER BY id ASC",
            (workspace_id,),
        ).fetchall()
    ]

    mensaje = datos.mensaje.strip()
    try:
        respuesta = _get_llm().responder(system_prompt, historial, mensaje)
    except Exception as exc:  # noqa: BLE001 — RNF-006: error claro si el LLM no está
        raise HTTPException(
            status_code=503,
            detail=f"El asistente no está disponible en este momento: {exc}",
        ) from exc

    # Persiste ambos mensajes solo si la generación tuvo éxito.
    db.execute(
        "INSERT INTO mensajes (workspace_id, rol, contenido) VALUES (?, 'user', ?)",
        (workspace_id, mensaje),
    )
    cur = db.execute(
        "INSERT INTO mensajes (workspace_id, rol, contenido) VALUES (?, 'assistant', ?)",
        (workspace_id, respuesta),
    )
    db.commit()

    fila = db.execute(
        "SELECT rol, contenido, created_at FROM mensajes WHERE id = ?", (cur.lastrowid,)
    ).fetchone()
    return ChatOut(rol=fila["rol"], contenido=fila["contenido"], created_at=fila["created_at"])
