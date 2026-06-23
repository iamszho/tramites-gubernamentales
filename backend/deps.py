"""Dependencias compartidas: autenticación por token de sesión."""

import sqlite3

from fastapi import Depends, Header, HTTPException

from db import get_db


def get_current_user(
    authorization: str | None = Header(default=None),
    db: sqlite3.Connection = Depends(get_db),
) -> sqlite3.Row:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="No autenticado.")
    token = authorization[7:].strip()

    fila = db.execute(
        """
        SELECT u.id, u.nombre, u.email
        FROM sesiones s
        JOIN usuarios u ON u.id = s.usuario_id
        WHERE s.token = ? AND s.expira_en > datetime('now')
        """,
        (token,),
    ).fetchone()

    if fila is None:
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada.")
    return fila
