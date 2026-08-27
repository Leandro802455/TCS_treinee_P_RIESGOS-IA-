from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Protocol

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


KNOWLEDGE_BASE = [
    "Un endeudamiento superior al 70% indica dependencia relevante de financiación externa.",
    "Una liquidez inmediata inferior a 1 puede dificultar el pago de obligaciones de corto plazo.",
    "Una rentabilidad neta inferior al 5% deja poco margen para absorber pérdidas o shocks.",
    "Las cuentas por cobrar sobre 90 días pueden presionar el flujo de caja operativo.",
]


@dataclass(frozen=True)
class TextChunk:
    """Fragmento indexable de un documento de referencia."""

    text: str
    document_id: str
    chunk_id: int


class VectorStore(Protocol):
    """Contrato mínimo que puede implementar una base vectorial externa."""

    def add_documents(self, documents: Iterable[str], document_prefix: str = "document") -> None:
        ...

    def search(self, query: str, top_k: int = 2) -> list[TextChunk]:
        ...


def split_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Divide un documento en fragmentos con solapamiento para no perder contexto."""
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_size debe ser positivo y overlap menor que chunk_size")
    cleaned = " ".join(text.split())
    if not cleaned:
        return []
    step = chunk_size - overlap
    return [cleaned[start:start + chunk_size] for start in range(0, len(cleaned), step)]


class LocalVectorStore:
    """Almacenamiento local basado en TF-IDF y similitud coseno."""

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap
        self._chunks: list[TextChunk] = []
        self._vectorizer: TfidfVectorizer | None = None
        self._embeddings = None

    @property
    def chunks(self) -> Sequence[TextChunk]:
        return tuple(self._chunks)

    def add_documents(self, documents: Iterable[str], document_prefix: str = "document") -> None:
        """Fragmenta, almacena y vuelve a indexar documentos de referencia."""
        for index, document in enumerate(documents):
            for chunk_id, chunk in enumerate(split_into_chunks(document, self.chunk_size, self.overlap)):
                self._chunks.append(TextChunk(chunk, f"{document_prefix}-{index}", chunk_id))
        self._rebuild_index()

    def embed(self, texts: Sequence[str]):
        """Genera embeddings TF-IDF locales para los textos proporcionados."""
        if not texts:
            return []
        vectorizer = TfidfVectorizer()
        return vectorizer.fit_transform(texts)

    def _rebuild_index(self) -> None:
        if not self._chunks:
            self._vectorizer = None
            self._embeddings = None
            return
        self._vectorizer = TfidfVectorizer()
        self._embeddings = self._vectorizer.fit_transform([chunk.text for chunk in self._chunks])

    def search(self, query: str, top_k: int = 2) -> list[TextChunk]:
        """Devuelve los fragmentos más similares, ordenados de mayor a menor relevancia."""
        if not query.strip() or top_k <= 0 or not self._chunks or self._vectorizer is None:
            return []
        query_embedding = self._vectorizer.transform([query])
        scores = cosine_similarity(query_embedding, self._embeddings).ravel()
        ranked = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)
        return [self._chunks[index] for index, score in ranked[:top_k] if score > 0]


def retrieve_context(
    query: str,
    documents: Iterable[str] = KNOWLEDGE_BASE,
    top_k: int = 2,
) -> list[str]:
    """Fachada compatible que recupera texto usando el almacenamiento local."""
    store = LocalVectorStore()
    store.add_documents(documents)
    return [chunk.text for chunk in store.search(query, top_k)]
