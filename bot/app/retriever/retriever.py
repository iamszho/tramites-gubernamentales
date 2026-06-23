"""Recuperador híbrido: búsqueda semántica en Chroma + filtros por metadata.

Diseño honesto frente a los datos reales indexados:

- `dependencia` en la metadata guarda el nombre oficial largo
  (ej. "Comisión Federal para la Protección contra Riesgos Sanitarios"),
  mientras que el NLU extrae siglas ("COFEPRIS", "SEP"). Un filtro exacto
  `where == "SEP"` nunca acertaría, así que la dependencia se incorpora al
  texto de la consulta semántica en lugar de usarse como filtro duro.
- `costo` son montos crudos ("$ 231.64 MXN") más el placeholder "Sin costo".
  Solo se filtra el caso binario "gratuito" -> costo == "Sin costo".
- `tipo` en la metadata es la modalidad del trámite y solo tiene 3 valores
  ('En línea', 'Presencial', 'Medios Alternativos'). Se filtra únicamente si
  el valor extraído coincide con una de esas modalidades.

Si un filtro duro deja la consulta en cero resultados, se reintenta sin filtro
(degradación elegante) para que el PoC nunca devuelva vacío por una etiqueta
mal alineada.
"""

from dataclasses import dataclass

import chromadb

from indexer.config import DIRECTORIO_CHROMA, NOMBRE_COLECCION
from indexer.embedder import GeneradorEmbeddings

MODALIDADES_VALIDAS = {"En línea", "Presencial", "Medios Alternativos"}
TERMINOS_GRATUITO = {"gratuito", "gratis", "sin costo", "gratuita"}


@dataclass
class TramiteRecuperado:
    nombre: str
    dependencia: str
    link: str
    contenido: str
    distancia: float
    metadata: dict


class RecuperadorHibrido:
    def __init__(self, k: int = 4):
        self._k = k
        self._cliente = chromadb.PersistentClient(path=str(DIRECTORIO_CHROMA))
        self._coleccion = self._cliente.get_collection(NOMBRE_COLECCION)
        self._embeddings = GeneradorEmbeddings()

    def _construir_filtro(self, costo: str, tipo: str) -> dict | None:
        condiciones = []
        if costo and costo.strip().lower() in TERMINOS_GRATUITO:
            condiciones.append({"costo": "Sin costo"})
        if tipo and tipo.strip() in MODALIDADES_VALIDAS:
            condiciones.append({"tipo": tipo.strip()})

        if not condiciones:
            return None
        if len(condiciones) == 1:
            return condiciones[0]
        return {"$and": condiciones}

    def _texto_consulta(self, consulta_semantica: str, dependencia: str) -> str:
        if dependencia and dependencia.strip():
            return f"{consulta_semantica} {dependencia.strip()}"
        return consulta_semantica

    def recuperar(
        self,
        consulta_semantica: str,
        dependencia: str = "",
        costo: str = "",
        tipo: str = "",
    ) -> list[TramiteRecuperado]:
        texto = self._texto_consulta(consulta_semantica, dependencia)
        vector = self._embeddings.generar([texto], tamano_lote=1)[0]
        filtro = self._construir_filtro(costo, tipo)

        resultados = self._consultar(vector, filtro)
        # Degradación elegante: si el filtro duro dejó la consulta vacía,
        # se reintenta sin filtro para no devolver una respuesta hueca.
        if filtro is not None and not resultados:
            resultados = self._consultar(vector, None)

        return resultados

    def _consultar(self, vector: list[float], filtro: dict | None) -> list[TramiteRecuperado]:
        respuesta = self._coleccion.query(
            query_embeddings=[vector],
            n_results=self._k,
            where=filtro,
            include=["documents", "metadatas", "distances"],
        )

        documentos = respuesta["documents"][0]
        metadatas = respuesta["metadatas"][0]
        distancias = respuesta["distances"][0]

        recuperados = []
        for contenido, meta, distancia in zip(documentos, metadatas, distancias):
            recuperados.append(
                TramiteRecuperado(
                    nombre=meta.get("nombre", ""),
                    dependencia=meta.get("dependencia", ""),
                    link=meta.get("link", ""),
                    contenido=contenido,
                    distancia=distancia,
                    metadata=meta,
                )
            )
        return recuperados
