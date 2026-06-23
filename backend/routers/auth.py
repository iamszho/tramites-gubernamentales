"""Autenticación: registro, login, logout, sesión actual (Epic 1)."""

import sqlite3
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException

from config import BLOQUEO_LOGIN_MINUTOS, DURACION_SESION_HORAS, MAX_INTENTOS_LOGIN
from db import get_db
from deps import get_current_user
from schemas import LoginIn, RegistroIn, TokenOut, UsuarioOut
from security import generar_token, hash_password, verificar_password

router = APIRouter(prefix="/auth", tags=["auth"])


def _crear_sesion(db: sqlite3.Connection, usuario_id: int) -> str:
    token = generar_token()
    expira = datetime.now(timezone.utc) + timedelta(hours=DURACION_SESION_HORAS)
    db.execute(
        "INSERT INTO sesiones (token, usuario_id, expira_en) VALUES (?, ?, ?)",
        (token, usuario_id, expira.strftime("%Y-%m-%d %H:%M:%S")),
    )
    db.commit()
    return token


@router.post("/register", response_model=TokenOut, status_code=201)
def registrar(datos: RegistroIn, db: sqlite3.Connection = Depends(get_db)) -> TokenOut:
    existe = db.execute(
        "SELECT 1 FROM usuarios WHERE email = ?", (datos.email,)
    ).fetchone()
    if existe:  # AC-001-2
        raise HTTPException(status_code=409, detail="Ese correo ya está registrado.")

    salt, ph = hash_password(datos.password)
    cur = db.execute(
        "INSERT INTO usuarios (nombre, email, salt, password_hash) VALUES (?, ?, ?, ?)",
        (datos.nombre.strip(), str(datos.email), salt, ph),
    )
    db.commit()
    usuario_id = cur.lastrowid

    token = _crear_sesion(db, usuario_id)  # AC-001-4: auto-login
    return TokenOut(
        token=token,
        usuario=UsuarioOut(id=usuario_id, nombre=datos.nombre.strip(), email=str(datos.email)),
    )


def _esta_bloqueado(db: sqlite3.Connection, email: str) -> bool:
    fila = db.execute(
        "SELECT bloqueo_hasta FROM intentos_login WHERE email = ?", (email,)
    ).fetchone()
    if fila and fila["bloqueo_hasta"]:
        bloqueo = datetime.strptime(fila["bloqueo_hasta"], "%Y-%m-%d %H:%M:%S")
        return bloqueo > datetime.now(timezone.utc).replace(tzinfo=None)
    return False


def _registrar_fallo(db: sqlite3.Connection, email: str) -> None:
    fila = db.execute(
        "SELECT fallos FROM intentos_login WHERE email = ?", (email,)
    ).fetchone()
    fallos = (fila["fallos"] if fila else 0) + 1
    bloqueo_hasta = None
    if fallos >= MAX_INTENTOS_LOGIN:  # AC-002-3
        bloqueo = datetime.now(timezone.utc) + timedelta(minutes=BLOQUEO_LOGIN_MINUTOS)
        bloqueo_hasta = bloqueo.strftime("%Y-%m-%d %H:%M:%S")
        fallos = 0  # reinicia el contador tras bloquear
    db.execute(
        """
        INSERT INTO intentos_login (email, fallos, bloqueo_hasta) VALUES (?, ?, ?)
        ON CONFLICT(email) DO UPDATE SET fallos = ?, bloqueo_hasta = ?
        """,
        (email, fallos, bloqueo_hasta, fallos, bloqueo_hasta),
    )
    db.commit()


def _limpiar_intentos(db: sqlite3.Connection, email: str) -> None:
    db.execute("DELETE FROM intentos_login WHERE email = ?", (email,))
    db.commit()


@router.post("/login", response_model=TokenOut)
def login(datos: LoginIn, db: sqlite3.Connection = Depends(get_db)) -> TokenOut:
    email = str(datos.email)
    if _esta_bloqueado(db, email):
        raise HTTPException(
            status_code=429,
            detail=f"Demasiados intentos. Espera {BLOQUEO_LOGIN_MINUTOS} minutos e inténtalo de nuevo.",
        )

    usuario = db.execute(
        "SELECT id, nombre, email, salt, password_hash FROM usuarios WHERE email = ?",
        (email,),
    ).fetchone()

    # AC-002-2: error genérico, no revela qué campo falló.
    if usuario is None or not verificar_password(datos.password, usuario["salt"], usuario["password_hash"]):
        _registrar_fallo(db, email)
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos.")

    _limpiar_intentos(db, email)
    token = _crear_sesion(db, usuario["id"])
    return TokenOut(
        token=token,
        usuario=UsuarioOut(id=usuario["id"], nombre=usuario["nombre"], email=usuario["email"]),
    )


@router.post("/logout", status_code=204)
def logout(
    db: sqlite3.Connection = Depends(get_db),
    usuario: sqlite3.Row = Depends(get_current_user),
) -> None:
    # Invalida todas las sesiones del usuario actual (logout simple para el PoC).
    db.execute("DELETE FROM sesiones WHERE usuario_id = ?", (usuario["id"],))
    db.commit()


@router.get("/me", response_model=UsuarioOut)
def me(usuario: sqlite3.Row = Depends(get_current_user)) -> UsuarioOut:
    return UsuarioOut(id=usuario["id"], nombre=usuario["nombre"], email=usuario["email"])
