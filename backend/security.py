"""Hashing de contraseñas y generación de tokens, solo con la stdlib (ADR-002)."""

import hashlib
import hmac
import secrets

_ITERACIONES = 200_000


def hash_password(password: str) -> tuple[str, str]:
    """Devuelve (salt_hex, hash_hex) con PBKDF2-HMAC-SHA256. RNF-004."""
    salt = secrets.token_bytes(16)
    derivado = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _ITERACIONES)
    return salt.hex(), derivado.hex()


def verificar_password(password: str, salt_hex: str, hash_hex: str) -> bool:
    salt = bytes.fromhex(salt_hex)
    derivado = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _ITERACIONES)
    return hmac.compare_digest(derivado.hex(), hash_hex)


def generar_token() -> str:
    return secrets.token_urlsafe(32)
