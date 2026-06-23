"""Catálogo y espacios de trabajo por trámite (Epic 2)."""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from config import CATALOGO_TRAMITES, DISCLAIMER, TRAMITES_POR_ID
from db import get_db
from deps import get_current_user
from schemas import (
    CrearWorkspaceIn,
    MensajeOut,
    TramiteCatalogo,
    WorkspaceDetalle,
    WorkspaceOut,
)

router = APIRouter(tags=["tramites"])


@router.get("/catalogo", response_model=list[TramiteCatalogo])
def catalogo(usuario: sqlite3.Row = Depends(get_current_user)) -> list[TramiteCatalogo]:
    # US-005: los 3 trámites del MVP.
    return [TramiteCatalogo(**{k: t[k] for k in ("id", "nombre", "descripcion", "icono")}) for t in CATALOGO_TRAMITES]


def _a_workspace_out(fila: sqlite3.Row) -> WorkspaceOut:
    tramite = TRAMITES_POR_ID[fila["tramite_id"]]
    return WorkspaceOut(
        id=fila["id"],
        tramite_id=fila["tramite_id"],
        nombre=tramite["nombre"],
        icono=tramite["icono"],
        created_at=fila["created_at"],
    )


@router.get("/tramites", response_model=list[WorkspaceOut])
def listar_workspaces(
    db: sqlite3.Connection = Depends(get_db),
    usuario: sqlite3.Row = Depends(get_current_user),
) -> list[WorkspaceOut]:
    # US-007: trámites activos del usuario.
    filas = db.execute(
        "SELECT id, tramite_id, created_at FROM workspaces WHERE usuario_id = ? ORDER BY created_at DESC",
        (usuario["id"],),
    ).fetchall()
    return [_a_workspace_out(f) for f in filas]


@router.post("/tramites", response_model=WorkspaceOut, status_code=201)
def crear_workspace(
    datos: CrearWorkspaceIn,
    db: sqlite3.Connection = Depends(get_db),
    usuario: sqlite3.Row = Depends(get_current_user),
) -> WorkspaceOut:
    if datos.tramite_id not in TRAMITES_POR_ID:
        raise HTTPException(status_code=400, detail="Trámite no disponible.")

    # AC-006-2 / RF-012 / RN-001: si ya existe, devuelve el existente.
    existente = db.execute(
        "SELECT id, tramite_id, created_at FROM workspaces WHERE usuario_id = ? AND tramite_id = ?",
        (usuario["id"], datos.tramite_id),
    ).fetchone()
    if existente:
        return _a_workspace_out(existente)

    cur = db.execute(
        "INSERT INTO workspaces (usuario_id, tramite_id) VALUES (?, ?)",
        (usuario["id"], datos.tramite_id),
    )
    db.commit()
    fila = db.execute(
        "SELECT id, tramite_id, created_at FROM workspaces WHERE id = ?", (cur.lastrowid,)
    ).fetchone()
    return _a_workspace_out(fila)


def _workspace_del_usuario(db: sqlite3.Connection, workspace_id: int, usuario_id: int) -> sqlite3.Row:
    fila = db.execute(
        "SELECT id, tramite_id, created_at FROM workspaces WHERE id = ? AND usuario_id = ?",
        (workspace_id, usuario_id),
    ).fetchone()
    if fila is None:
        raise HTTPException(status_code=404, detail="Trámite no encontrado.")
    return fila


@router.get("/tramites/{workspace_id}", response_model=WorkspaceDetalle)
def ver_workspace(
    workspace_id: int,
    db: sqlite3.Connection = Depends(get_db),
    usuario: sqlite3.Row = Depends(get_current_user),
) -> WorkspaceDetalle:
    fila = _workspace_del_usuario(db, workspace_id, usuario["id"])
    tramite = TRAMITES_POR_ID[fila["tramite_id"]]

    # US-012: historial persistente.
    mensajes = db.execute(
        "SELECT rol, contenido, created_at FROM mensajes WHERE workspace_id = ? ORDER BY id ASC",
        (workspace_id,),
    ).fetchall()

    return WorkspaceDetalle(
        id=fila["id"],
        tramite_id=fila["tramite_id"],
        nombre=tramite["nombre"],
        icono=tramite["icono"],
        disclaimer=DISCLAIMER,
        mensajes=[MensajeOut(rol=m["rol"], contenido=m["contenido"], created_at=m["created_at"]) for m in mensajes],
    )


@router.delete("/tramites/{workspace_id}", status_code=204)
def eliminar_workspace(
    workspace_id: int,
    db: sqlite3.Connection = Depends(get_db),
    usuario: sqlite3.Row = Depends(get_current_user),
) -> None:
    # US-008: eliminar trámite y su historial (cascade).
    _workspace_del_usuario(db, workspace_id, usuario["id"])
    db.execute("DELETE FROM workspaces WHERE id = ?", (workspace_id,))
    db.commit()
