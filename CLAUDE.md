# Configuración del Proyecto con Claude

## Configuración del Entorno

### Variables de Entorno
Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:

```
# Backend
BACKEND_PORT=5000
BACKEND_HOST=localhost

# Base de datos
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tramites_db
DB_USER=usuario
DB_PASSWORD=contraseña

# API Keys
OPENAI_API_KEY=tu_api_key_aqui
GOOGLE_API_KEY=tu_google_api_key_aqui

# Bot
BOT_TOKEN=tu_token_de_telegram
BOT_WEBHOOK_URL=https://tu-dominio.com/webhook

# Frontend
FRONTEND_PORT=3000
FRONTEND_HOST=localhost
```

### Configuración de Docker
El archivo `docker-compose.yml` ya está configurado para usar estas variables de entorno.

## Configuración de Claude

### Prompt Engineering para Trámites
- Usar prompts específicos para cada tipo de trámite
- Incluir contexto gubernamental y normativas
- Validar respuestas con fuentes oficiales

### Ejemplo de Prompt para Claude:
```
Eres un asistente especializado en trámites gubernamentales en México. 
Tu tarea es ayudar a los ciudadanos a entender y completar sus trámites.

Instrucciones:
1. Siempre verifica la información con fuentes oficiales
2. Proporciona pasos claros y numerados
3. Incluye enlaces a formularios oficiales cuando sea posible
4. Indica tiempos estimados de procesamiento
5. Menciona costos asociados si los hay
```

## Integración con APIs

### API de Trámites Gubernamentales
- Endpoint: `https://api.tramites.gob.mx/v1`
- Documentación: `https://developer.tramites.gob.mx`

### API de Verificación de Documentos
- Endpoint: `https://api.verificacion.gob.mx/v1`
- Documentación: `https://developer.verificacion.gob.mx`

## Comandos de Desarrollo y Pruebas

### Bot (Directorio `bot/`)
Para realizar tareas y pruebas en el módulo del bot, ingresa al directorio `bot/` o ejecuta a través de su entorno virtual:
- **Ejecutar Clasificación de Intenciones y NLU:** `python app/nlu/intentions.py` (o desde la raíz: `bot/venv/bin/python bot/app/nlu/intentions.py`)
- **Indexar Base de Datos (Chroma):** `python -m indexer.build_index`
- **Probar Base de Datos de Vectores (Chroma):** `python indexer/test/test_coleccion.py`