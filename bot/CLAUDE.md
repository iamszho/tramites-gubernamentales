# Chatbot de Trámites Gubernamentales de México

## Objetivo del proyecto

Chatbot RAG para consultar trámites administrativos del gobierno mexicano. Tres objetivos paralelos:

1. Proyecto de portafolio
2. Aprendizaje de LangChain y arquitecturas RAG
3. Potencial venta comercial

## Postura de CLAUDE

- Toma una postura neutral, objetivo, técnico y profesional
- No busques darme la razon si no la tengo.
- Pregunta siempre que tengas dudas.
- Di "no se" cuando no tengas la informacion.

---

## El dataset

- **Fuente:** CSV/Excel con datos de trámites gubernamentales mexicanos
- **Dimensiones:** 6,376 filas × 15 columnas
- **Columnas:**

| Columna                  | Promedio palabras | Notas                                          |
| ------------------------ | ----------------- | ---------------------------------------------- |
| ID                       | 1.00              | Identificador numérico                         |
| Nombre del tramite       | 13.85             | Campo clave para recuperación                  |
| Dependencia              | 5.90              | Ej: SEP, SAT, IMSS                             |
| Descripcion              | 38.03             | Resumen administrativo del trámite             |
| Tipo                     | 1.34              | Categórico                                     |
| Unidad Administrativa    | 6.29              | Área específica dentro de la dependencia       |
| Homoclave                | 1.01              | Código alfanumérico opaco, sin valor semántico |
| Link                     | 1.00              | URL oficial del trámite                        |
| Requisitos               | 53.46             | Lista numerada, formato multilínea             |
| Como realizar el tramite | 82.28             | Lista numerada, formato multilínea             |
| Costo del tramite        | 2.53              | Normalizado (ver limpieza)                     |
| Vigencia                 | 2.08              | Puede ser "Sin vigencia"                       |
| Tiempo de respuesta      | 2.98              | Puede ser "Sin tiempo de respuesta"            |

### Estado del dataset

- **Todos los nulos fueron reemplazados por placeholders de texto**, no quedan `None` ni `NaN`:
  - Nulos de costo → `"Sin costo"` (incluye ~4,295 nulos + 18 registros corruptos `"$ MXN"`)
  - Otros nulos → `"Sin vigencia"`, `"Sin tiempo de respuesta"`, etc.
- Strings limpiados con `.str.strip()` en todas las columnas
- Columnas con listas numeradas (Requisitos, Como realizar el tramite, Descripcion del pago, Descripcion extra) preservan saltos de línea (`\n`) — se usó `limpiar_lista` en lugar de `limpiar_simple`

---

## Arquitectura RAG: decisiones tomadas

### Arquitectura general: híbrida (filtrado estructurado + búsqueda semántica)

Se eligió arquitectura híbrida porque el dataset tiene naturaleza dual:

- Preguntas semánticas libres: _"¿cómo saco mi acta de nacimiento?"_ → búsqueda por similitud vectorial
- Preguntas con filtros exactos: _"trámites gratuitos de la SEP"_ → filtrado por metadata estructurada

Un sistema solo semántico no puede garantizar filtros exactos (ej. `costo == "Gratuito"`) con precisión binaria.

---

### Modelo de embeddings: `paraphrase-multilingual-mpnet-base-v2`

- Corre en local (Sentence Transformers), sin costo de API
- Soporte multilingüe, adecuado para español
- Vectores de 768 dimensiones (antes se evaluó `paraphrase-multilingual-MiniLM-L12-v2`, 384 dimensiones, mismo límite de tokens — se cambió por mejor calidad semántica a costa de más cómputo)
- **Límite arquitectónico: 128 tokens (~98 palabras en español)** — igual en ambos modelos
- Este límite es del modelo, no de la API — no cambia si se corre local o en nube
- El `page_content` promedio del dataset es ~202 palabras → supera el límite más del doble
- Por esto se adoptó la **Opción B: separar string de embedding del page_content**
- Carga del modelo autenticada con `HF_TOKEN` (variable en `.env`, vía `python-dotenv`) para evitar el rate limit de peticiones anónimas a Hugging Face Hub

---

### Separación embedding / page_content (Opción B)

El `Document` de LangChain tiene dos atributos (`page_content` y `metadata`). Por defecto LangChain embebe el `page_content`. En este proyecto se sobrescribe ese comportamiento:

| Componente              | Contenido                                 | Quién lo usa                            | Se almacena     |
| ----------------------- | ----------------------------------------- | --------------------------------------- | --------------- |
| **String de embedding** | Nombre, Dependencia, Descripción, Requisitos, Cómo realizarlo | Modelo de embeddings → genera el vector | No (desechable) |
| **`page_content`**      | Todos los campos relevantes completos     | El LLM para generar la respuesta        | Sí, en Chroma   |
| **`metadata`**          | Campos estructurados para filtrado + Link | Filtrado híbrido + citar fuente oficial | Sí, en Chroma   |

#### String de embedding (~193 palabras promedio — supera el límite de 128 tokens en la mayoría de los casos, se acepta el truncamiento del modelo a cambio de cubrir Requisitos y Cómo realizarlo en la búsqueda semántica)

```
Nombre del trámite: {Nombre del tramite}
Dependencia: {Dependencia}
Descripción: {Descripcion}
Requisitos: {Requisitos}
Cómo realizarlo: {Como realizar el tramite}
```

#### page_content (completo, lo lee el LLM)

```
Nombre del trámite: {Nombre del tramite}
Dependencia: {Dependencia}
Tipo: {Tipo}
Unidad Administrativa: {Unidad Administrativa}
Descripción: {Descripcion}
Requisitos: {Requisitos}
Cómo realizarlo: {Como realizar el tramite}
Costo: {Costo del tramite}
Vigencia: {Vigencia}
Tiempo de respuesta: {Tiempo de respuesta}
```

#### metadata (diccionario estructurado)

```python
{
    "nombre":      str,  # para filtrado y referencia
    "dependencia": str,  # filtro exacto (ej. dependencia == "SEP")
    "tipo":        str,  # filtro exacto
    "homoclave":   str,  # identificador, no se embebe
    "link":        str,  # se usa en Fase 3 para citar fuente oficial
    "costo":       str,  # filtro exacto (ej. costo == "Gratuito")
    "vigencia":    str,  # filtro exacto
}
```

**Campos excluidos del string de embedding:**

- `Homoclave`, `Link`, `ID` → identificadores opacos, cero valor semántico para recuperación semántica. `Homoclave` y `Link` sí viven en `metadata` (filtrado y cita de fuente); `ID` no se usa ni en metadata ni en embedding (es redundante con `id_unico`, que se usa como ID del documento en Chroma)
- `Tipo`, `Unidad Administrativa`, `Costo del tramite`, `Vigencia`, `Tiempo de respuesta` → van en `page_content` para el LLM, pero no en el string de embedding (son campos cortos y estructurados, no aportan a la similitud semántica de texto libre)

`Requisitos` y `Como realizar el tramite` sí se incluyen completos en el string de embedding (ver más abajo) a pesar de ser los campos más largos del dataset (~135 palabras promedio combinados). Esto fue una decisión explícita: se prioriza que la búsqueda semántica cubra preguntas del tipo "¿qué necesito para...?" / "¿cómo hago...?", aceptando que el modelo trunque a 128 tokens en la mayoría de los registros en vez de mantener el string de embedding corto.

---

### Vector store

| Entorno          | Tecnología | Razón                                        |
| ---------------- | ---------- | -------------------------------------------- |
| Desarrollo local | Chroma     | Embebido, sin infraestructura, gratis        |
| Producción       | Pinecone   | Escalable, administrado, sin servidor propio |

**Sobre la carpeta `chroma_db`:**

- Chroma genera una carpeta local con archivos internos (SQLite + binarios de vectores)
- Esta carpeta **no se sube al repositorio** → agregar `chroma_db/` al `.gitignore`
- Quien clone el repo regenera la base corriendo el script de indexación

---

## Stack tecnológico

| Capa                | Tecnología                                                      |
| ------------------- | --------------------------------------------------------------- |
| Embeddings          | `paraphrase-multilingual-mpnet-base-v2` (Sentence Transformers) |
| Vector store (dev)  | Chroma                                                          |
| Vector store (prod) | Pinecone                                                        |
| Framework RAG       | LangChain                                                       |
| LLM (NLU)           | `gemini-2.0-flash` (Google AI Studio, gratuito)                 |
| Backend             | FastAPI                                                         |
| Frontend            | Next.js                                                         |
| Datos               | CSV/Excel procesado con pandas                                  |

---

## Fases del proyecto

### Fase 1 — Preparación de datos ✅ completada

1. Exploración (shape, columnas, nulos)
2. Limpieza (strip, normalización de costos, `limpiar_simple` vs `limpiar_lista`)
3. Diseño del documento (plantilla `page_content` + string de embedding + metadata)
4. Generación de 6,376 `Document` objects de LangChain
5. Validación manual de muestra

### Fase 2 — Vector store (en curso)

1. Instalar dependencias (`langchain`, `chromadb`, `sentence-transformers`, `pandas`)
2. Construir Documents con `page_content` completo + string de embedding separado
3. Validar muestra antes de indexar
4. Generar embeddings e indexar en Chroma
5. Probar el retriever con consultas de prueba

**Código en `bot/indexer/`:**

| Módulo               | Responsabilidad                                                              |
| --------------------- | ----------------------------------------------------------------------------- |
| `config.py`           | Rutas (CSV, persistencia de Chroma), nombre de colección, modelo de embeddings |
| `data_loader.py`      | Lee el CSV, valida columnas requeridas y ausencia de nulos                   |
| `document_builder.py` | Construye `texto_embedding`, `page_content` y `metadata` por fila (Opción B) |
| `validator.py`        | Imprime una muestra aleatoria y advierte si el texto de embedding excede ~90 palabras |
| `embedder.py`         | Envuelve `SentenceTransformer` para generar los vectores en lote; se autentica a Hugging Face Hub con `HF_TOKEN` (`.env`) |
| `build_index.py`      | Orquesta el flujo y hace `upsert` en Chroma; CLI: `python -m indexer.build_index [--limite N] [--solo-validar] [--tamano-muestra N]` |

La indexación usa el cliente `chromadb` directo (no el wrapper `Chroma` de LangChain), porque ese wrapper siempre embebe el mismo texto que almacena — no permite separar el string de embedding del `page_content`. Se generan los vectores con `sentence-transformers` a partir del string corto y se insertan con `collection.upsert(ids, embeddings, documents, metadatas)`, donde `documents` es el `page_content` completo. `id_unico` (columna del CSV, sin duplicados) se usa como `id` del documento en Chroma.

### Fase 3 — Construcción del bot con LangChain (en curso)

- Retriever híbrido: similitud vectorial + filtrado por metadata
- El campo `Link` de metadata se usa para citar la fuente oficial en cada respuesta

**Componente 1 — NLU (`bot/app/nlu/`):**

| Módulo                      | Responsabilidad                                                        |
| ---------------------------- | ------------------------------------------------------------------------ |
| `intent_classifier.py`       | Llama a `gemini-2.0-flash` y fuerza un tool call (`function_calling_config=ANY`) para extraer `consulta_semantica` + filtros (`dependencia`, `costo`, `tipo`) del mensaje del usuario |
| `prompts/system_prompt.py`   | Instrucciones fijas que limitan el rol del modelo a clasificar/extraer, no a responder en texto libre |

Usa el SDK `google-genai` directo (no `langchain-google-genai`), por la misma razón que el indexador usa `chromadb` directo en vez del wrapper de LangChain: se necesita control total sobre la declaración de la función y forzar el tool call, sin que un wrapper genérico limite esa configuración.

Esto resuelve la decisión pendiente de **self-querying retriever vs filtros manuales** a favor de un clasificador de intención propio: el LLM no traduce la consulta a un filtro de Chroma directamente (como haría el self-querying retriever de LangChain), sino que extrae campos estructurados vía tool call: un componente NLU separado, antes del retriever híbrido.

**Componente 2 — Retriever híbrido (`bot/app/retriever/`):**

| Módulo         | Responsabilidad                                                                 |
| -------------- | --------------------------------------------------------------------------------- |
| `retriever.py` | `RecuperadorHibrido`: embebe la `consulta_semantica` (reusa `GeneradorEmbeddings`), consulta Chroma con `collection.query` y aplica filtros de metadata |

Filtrado **best-effort, alineado con los datos reales** (no con el diseño teórico de metadata):

- `dependencia`: la metadata guarda el nombre oficial largo ("Comisión Federal para la Protección contra Riesgos Sanitarios") pero el NLU extrae siglas ("SEP"). Un `where` exacto nunca acierta → la dependencia se **incorpora al texto de la consulta semántica**, no se filtra de forma dura.
- `costo`: son montos crudos ("$ 231.64 MXN") + el placeholder "Sin costo". Solo se filtra el caso binario gratuito → `costo == "Sin costo"`.
- `tipo`: en la metadata es la **modalidad** (3 valores: 'En línea', 'Presencial', 'Medios Alternativos'), no el tipo de trámite. Solo se filtra si el valor coincide con una modalidad.
- Si un filtro duro deja 0 resultados, se reintenta sin filtro (degradación elegante).

**Componente 3 — Generación (`bot/app/generation/`):**

| Módulo                       | Responsabilidad                                                            |
| ---------------------------- | --------------------------------------------------------------------------- |
| `generator.py`               | `GeneradorRespuesta`: lee los `page_content` recuperados y redacta la respuesta citando el `Link` oficial. Proveedor conmutable por `PROVEEDOR_LLM`: `gemini` (por defecto, reusa `GOOGLE_API_KEY`) u `openrouter` (SDK `openai` apuntando a la API compatible) |
| `prompts/system_prompt.py`   | Prompt de sistema RAG: responder solo con base en el contexto, pasos numerados, citar fuente oficial |

**Orquestación (`bot/app/pipeline.py`):** `PipelineRAG` encadena NLU → retriever → generación y devuelve `respuesta` + `fuentes` (nombre/dependencia/link) + `intencion`. Es la fachada que consume el backend.

### Fase 4 — Backend y frontend ✅ PoC funcional

- **FastAPI** (`backend/`, raíz): capa HTTP delgada que importa `PipelineRAG` (añade `bot/` al path). Endpoints `GET /health` y `POST /chat`. CORS para el frontend. Degrada a `503` con mensaje claro si el LLM falla (ej. cuota de Gemini).
- **Next.js/React** (`frontend/`, raíz): interfaz de chat (App Router, TypeScript) que consume `POST /chat`, muestra fuentes oficiales como enlaces y la intención detectada (debug).
- Cómo ejecutar: ver `POC_README.md` en la raíz.

### Fase 5 — Despliegue

- Migración de Chroma a Pinecone
- Deploy de FastAPI y Next.js

---

## Decisiones pendientes

- ~~**Self-querying retriever vs filtros manuales**~~ → **Resuelto**: clasificador de intención propio (`bot/app/nlu/intent_classifier.py`) con `gemini-2.0-flash` y tool call forzado, en vez del self-querying retriever de LangChain o filtros completamente manuales
- ~~**Ajuste del string de embedding**~~ → **Resuelto**: se incluyeron `Requisitos` y `Como realizar el tramite` completos en el string de embedding. Se acepta que el modelo trunque a 128 tokens en la mayoría de los registros (el string promedio ya supera el límite, no solo los outliers de COFEPRIS) a cambio de cubrir semánticamente preguntas tipo "¿qué necesito para...?"
- **Redacción de placeholders en respuestas del LLM**: el LLM va a leer literalmente "Vigencia: Sin vigencia" — decidir si se traduce a lenguaje más natural en el prompt de Fase 3 (mitigado en parte en `prompts/system_prompt.py` de generación, pero no resuelto del todo)
- **Desalineación NLU ↔ metadata para filtrado exacto**: el NLU extrae siglas/etiquetas coloquiales ("SEP", "Gratuito") que no coinciden con los valores almacenados (nombre oficial largo, montos crudos, modalidad). Hoy se mitiga con filtrado best-effort (ver Componente 2). Para filtrado duro real haría falta: normalizar `dependencia` (siglas → nombre oficial), redefinir qué significa `tipo`, y normalizar `costo` a una etiqueta categórica (Gratuito/De pago) en la indexación.
- **Conteo de documentos indexados**: la colección Chroma tiene ~4,507 documentos, no 6,376 como indica la sección "El dataset". Revisar si el indexador perdió filas (duplicados de `id_unico`, filas descartadas) o si el CSV vigente trae menos registros.

---

## Principios de diseño

- **Entender el "por qué" antes del "cómo"** — las decisiones arquitectónicas se fundamentan antes de implementar
- **Validar antes de indexar** — muestra manual de Documents antes de gastar tiempo en embeddings masivos
- **Separación clara de responsabilidades** — string de embedding para recuperación, `page_content` para generación, `metadata` para filtrado
- **Iterativo** — decisiones como el string de embedding se pueden ajustar si la recuperación no es suficiente
