"""Acceso a datos con SQLite de la stdlib (ADR-002, sin ORM)."""

import sqlite3

from config import RUTA_DB

_ESQUEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre        TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE COLLATE NOCASE,
    salt          TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sesiones (
    token      TEXT PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    expira_en  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS intentos_login (
    email        TEXT PRIMARY KEY COLLATE NOCASE,
    fallos       INTEGER NOT NULL DEFAULT 0,
    bloqueo_hasta TEXT
);

CREATE TABLE IF NOT EXISTS workspaces (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    tramite_id TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (usuario_id, tramite_id)
);

CREATE TABLE IF NOT EXISTS mensajes (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    rol          TEXT NOT NULL,
    contenido    TEXT NOT NULL,
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def conectar() -> sqlite3.Connection:
    # check_same_thread=False: FastAPI ejecuta los endpoints síncronos en un
    # threadpool, por lo que la conexión que abre la dependencia get_db puede
    # usarse y cerrarse en un hilo distinto al que la creó. Es seguro porque cada
    # petición tiene su propia conexión y no se comparte ni se usa en paralelo.
    conn = sqlite3.connect(RUTA_DB, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = conectar()
    try:
        conn.executescript(_ESQUEMA)
        conn.commit()
    finally:
        conn.close()


def get_db():
    """Dependencia de FastAPI: abre una conexión por petición y la cierra al terminar."""
    conn = conectar()
    try:
        yield conn
    finally:
        conn.close()
