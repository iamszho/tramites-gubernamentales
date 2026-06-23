"""Configuración del backend de TramiteFácil (PoC)."""

from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[1]

# Las claves de LLM (GOOGLE_API_KEY / OPENROUTER_*) viven en bot/.env.
load_dotenv(RAIZ / "bot" / ".env")

# Conocimiento curado por trámite (ADR-001: Markdown en prompt, sin RAG en el MVP).
DIR_KNOWLEDGE = RAIZ / "docs" / "05_Development" / "knowledge-base"

# Base de datos SQLite del PoC.
RUTA_DB = Path(__file__).resolve().parent / "tramitefacil.db"

# Duración de la sesión (token). RNF-005.
DURACION_SESION_HORAS = 24 * 7

# Bloqueo tras intentos fallidos de login. AC-002-3.
MAX_INTENTOS_LOGIN = 5
BLOQUEO_LOGIN_MINUTOS = 5

# Catálogo del MVP: solo los 3 trámites vehiculares (Problem Statement §9).
CATALOGO_TRAMITES = [
    {
        "id": "licencia",
        "nombre": "Licencia de conducir",
        "descripcion": "Obtén o renueva tu licencia para conducir.",
        "icono": "🚗",
        "archivo": "licencia.md",
    },
    {
        "id": "verificacion",
        "nombre": "Verificación vehicular",
        "descripcion": "Revisión de emisiones y holograma de tu vehículo.",
        "icono": "🌫️",
        "archivo": "verificacion.md",
    },
    {
        "id": "cambio-placas",
        "nombre": "Cambio de placas",
        "descripcion": "Canje, reposición o cambio de propietario de placas.",
        "icono": "🔢",
        "archivo": "cambio-placas.md",
    },
]

TRAMITES_POR_ID = {t["id"]: t for t in CATALOGO_TRAMITES}

# Disclaimer obligatorio en la interfaz del chat (RF-017, RN-004, US-011).
DISCLAIMER = (
    "La información de este asistente es de referencia y puede no reflejar cambios "
    "recientes. Los trámites vehiculares son estatales y varían por entidad. "
    "Verifica siempre en el portal oficial de tu estado antes de acudir a un módulo."
)

ORIGENES_CORS = ["http://localhost:3000", "http://127.0.0.1:3000"]
# Acepta cualquier puerto local (localhost o 127.0.0.1) para evitar problemas de origen.
ORIGEN_CORS_REGEX = r"http://(localhost|127\.0\.0\.1)(:\d+)?"
