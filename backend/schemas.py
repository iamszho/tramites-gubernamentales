"""Modelos de entrada/salida (Pydantic)."""

from pydantic import BaseModel, EmailStr, Field


class RegistroIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=200)  # AC-001-3


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UsuarioOut(BaseModel):
    id: int
    nombre: str
    email: str


class TokenOut(BaseModel):
    token: str
    usuario: UsuarioOut


class TramiteCatalogo(BaseModel):
    id: str
    nombre: str
    descripcion: str
    icono: str


class WorkspaceOut(BaseModel):
    id: int
    tramite_id: str
    nombre: str
    icono: str
    created_at: str


class CrearWorkspaceIn(BaseModel):
    tramite_id: str


class MensajeOut(BaseModel):
    rol: str
    contenido: str
    created_at: str


class WorkspaceDetalle(BaseModel):
    id: int
    tramite_id: str
    nombre: str
    icono: str
    disclaimer: str
    mensajes: list[MensajeOut]


class ChatIn(BaseModel):
    mensaje: str = Field(min_length=1, max_length=2000)


class ChatOut(BaseModel):
    rol: str
    contenido: str
    created_at: str
