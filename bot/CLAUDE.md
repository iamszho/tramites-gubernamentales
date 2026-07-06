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
- **Dimensiones:** 4,507 filas × 14 columnas (13 columnas de datos + `id_unico` como identificador generado, usado como ID del documento en Chroma; verificado 2026-07-03)
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
- Actualizado desde `paraphrase-multilingual-MiniLM-L12-v2` (384 dim) — mpnet-base-v2 usa 768 dim, generalmente mejor calidad de recuperación
- Similitud nativa del modelo: **coseno** (`model.similarity_fn_name == "cosine"`, verificado 2026-07-03)
- **Límite arquitectónico: 128 tokens (`model.max_seq_length`, verificado 2026-07-03; ~98 palabras en español)**
- Este límite es del modelo, no de la API — no cambia si se corre local o en nube
- El `page_content` promedio del dataset es ~202 palabras → supera el límite más del doble
- Por esto se adoptó la **Opción B: separar string de embedding del page_content**

---

### Separación embedding / page_content (Opción B)

El `Document` de LangChain tiene dos atributos (`page_content` y `metadata`). Por defecto LangChain embebe el `page_content`. En este proyecto se sobrescribe ese comportamiento:

| Componente              | Contenido                                 | Quién lo usa                            | Se almacena     |
| ----------------------- | ----------------------------------------- | --------------------------------------- | --------------- |
| **String de embedding** | Nombre, Dependencia, Descripción          | Modelo de embeddings → genera el vector | No (desechable) |
| **`page_content`**      | Todos los campos relevantes completos     | El LLM para generar la respuesta        | Sí, en Chroma   |
| **`metadata`**          | Campos estructurados para filtrado + Link | Filtrado híbrido + citar fuente oficial | Sí, en Chroma   |

#### String de embedding (corto, ~57 palabras promedio)

```
Nombre del trámite: {Nombre del tramite}
Dependencia: {Dependencia}
Descripción: {Descripcion}
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
- `Requisitos`, `Como realizar el tramite` → van en `page_content` para el LLM, pero no en el string de embedding (demasiado largos, ~135 palabras promedio combinados)

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

**Métrica de distancia: coseno (`hnsw:space: cosine`)**

- Corregido 2026-07-03: la colección se creaba sin especificar `hnsw:space`, por lo que Chroma usaba L2 por defecto — un desajuste con un modelo entrenado para similitud coseno, que degradaba el ranking de resultados sin dar error.
- La métrica de una colección Chroma queda fija al crearse: no se puede cambiar en una colección existente, hay que borrar `chroma_db/` y reindexar.
- `build_index.py` ahora crea la colección con `get_or_create_collection(NOMBRE_COLECCION, metadata={"hnsw:space": "cosine"})`.

---

## Stack tecnológico

| Capa                | Tecnología                                                      |
| ------------------- | --------------------------------------------------------------- |
| Embeddings          | `paraphrase-multilingual-mpnet-base-v2` (Sentence Transformers) |
| Vector store (dev)  | Chroma                                                          |
| Vector store (prod) | Pinecone                                                        |
| Framework RAG       | LangChain                                                       |
| LLM candidato       | (por definir)                                                   |
| Backend             | FastAPI                                                         |
| Frontend            | Next.js                                                         |
| Datos               | CSV/Excel procesado con pandas                                  |

---

## Fases del proyecto

### Fase 1 — Preparación de datos ✅ completada

1. Exploración (shape, columnas, nulos)
2. Limpieza (strip, normalización de costos, `limpiar_simple` vs `limpiar_lista`)
3. Diseño del documento (plantilla `page_content` + string de embedding + metadata)
4. Generación de 4,507 `Document` objects de LangChain
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
| `embedder.py`         | Envuelve `SentenceTransformer` para generar los vectores en lote             |
| `build_index.py`      | Orquesta el flujo y hace `upsert` en Chroma; CLI: `python -m indexer.build_index [--limite N] [--solo-validar] [--tamano-muestra N]` |

La indexación usa el cliente `chromadb` directo (no el wrapper `Chroma` de LangChain), porque ese wrapper siempre embebe el mismo texto que almacena — no permite separar el string de embedding del `page_content`. Se generan los vectores con `sentence-transformers` a partir del string corto y se insertan con `collection.upsert(ids, embeddings, documents, metadatas)`, donde `documents` es el `page_content` completo. `id_unico` (columna del CSV, sin duplicados) se usa como `id` del documento en Chroma.

### Fase 3 — Construcción del bot con LangChain

- Retriever híbrido: similitud vectorial + filtrado por metadata
- Self-querying retriever (LangChain traduce lenguaje natural a filtros de metadata automáticamente) vs filtros manuales — decisión pendiente
- El campo `Link` de metadata se usa para citar la fuente oficial en cada respuesta

### Fase 4 — Backend y frontend

- FastAPI como backend
- Next.js como frontend

### Fase 5 — Despliegue

- Migración de Chroma a Pinecone
- Deploy de FastAPI y Next.js

---

## Decisiones pendientes

- **Self-querying retriever vs filtros manuales** en Fase 3: el self-querying retriever usa el LLM para traducir lenguaje natural a filtros de metadata automáticamente; los filtros manuales son más predecibles pero menos flexibles
- **Ajuste del string de embedding**: se puede agregar una porción (primeras ~30 palabras) de Requisitos si se detecta que la recuperación semántica es insuficiente para preguntas del tipo "¿qué necesito para...?". Confirmado con datos reales: algunos trámites (ej. nombres largos de COFEPRIS) superan ~150 palabras solo en Nombre + Descripción, por encima del límite de 128 tokens — falta decidir si se truncan estos campos en el string de embedding o se acepta la pérdida de cobertura semántica en esos casos
- **Redacción de placeholders en respuestas del LLM**: el LLM va a leer literalmente "Vigencia: Sin vigencia" — decidir si se traduce a lenguaje más natural en el prompt de Fase 3
- **Truncamiento silencioso del texto de embedding**: cuantificado 2026-07-03 sobre el CSV actual — 451 filas (10%) superan las 90 palabras de margen, 115 filas (2.5%) superan las 128 palabras y ya se truncan hoy en la práctica (el peor caso pierde toda la Descripción porque el Nombre solo mide 113 palabras). Falta decidir una estrategia de truncamiento explícita en vez de dejarlo en manos del tokenizer.
- **`document_builder.py` no implementa la Opción B tal como está documentada**: `construir_texto_embedding` solo usa Nombre + Descripción (falta Dependencia); `construir_metadata` no incluye `nombre`, `homoclave` ni `link` (este último bloquea la cita de fuente oficial planeada para Fase 3). No se sabe si fue una decisión intencional o una regresión — pendiente de confirmar y, si aplica, corregir.

---

## Principios de diseño

- **Entender el "por qué" antes del "cómo"** — las decisiones arquitectónicas se fundamentan antes de implementar
- **Validar antes de indexar** — muestra manual de Documents antes de gastar tiempo en embeddings masivos
- **Separación clara de responsabilidades** — string de embedding para recuperación, `page_content` para generación, `metadata` para filtrado
- **Iterativo** — decisiones como el string de embedding se pueden ajustar si la recuperación no es suficiente
