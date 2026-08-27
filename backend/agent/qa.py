from pathlib import Path

from collections.abc import Iterator

from .llm_client import RESPONSE_MODES, generate_question_response, generar_respuesta_stream
from .pdf_reader import extract_text
from .rag import LocalVectorStore


def answer_question(pdf_path: str | Path, question: str, mode: str = "equilibrado") -> dict[str, str]:
    """Responde una pregunta usando el texto y el contexto recuperado del PDF."""
    if not question.strip():
        raise ValueError("La pregunta no puede estar vacía")
    if mode not in RESPONSE_MODES:
        raise ValueError("El modo debe ser: rapido, equilibrado o avanzado")

    document_text = extract_text(pdf_path)
    store = LocalVectorStore()
    store.add_documents([document_text], document_prefix="financial-pdf")
    chunks = store.search(question, top_k=3)
    context = [chunk.text for chunk in chunks]
    mode_config = RESPONSE_MODES[mode]
    answer = generate_question_response(
        question,
        context,
        document_text,
        modo=mode,
    )
    if answer is None:
        answer = "No hay una clave GROQ_API_KEY configurada para responder la pregunta."
    source = " ".join(context) if context else "Texto completo del PDF"
    return {
        "respuesta": answer,
        "fuente": source,
        "modo": mode,
        "modelo": mode_config["model"],
    }


def answer_question_stream(
    pdf_path: str | Path,
    question: str,
    mode: str = "equilibrado",
) -> Iterator[str]:
    """Devuelve la respuesta por fragmentos y termina con la fuente recuperada."""
    if not question.strip():
        raise ValueError("La pregunta no puede estar vacía")
    if mode not in RESPONSE_MODES:
        raise ValueError("El modo debe ser: rapido, equilibrado o avanzado")

    document_text = extract_text(pdf_path)
    store = LocalVectorStore()
    store.add_documents([document_text], document_prefix="financial-pdf")
    context = [chunk.text for chunk in store.search(question, top_k=3)]
    yield from generar_respuesta_stream(question, context, document_text, mode)
    source = " ".join(context) if context else "Texto completo del PDF"
    yield f"\n\n[FUENTE]: {source}"
