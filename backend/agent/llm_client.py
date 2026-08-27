import os
from collections.abc import Iterator

from groq import Groq


_MODEL_NAME = "openai/gpt-oss-120b"
MODEL_NAME = _MODEL_NAME
MAX_INPUT_CHARS = 12000

RESPONSE_MODES = {
    "rapido": {"model": "openai/gpt-oss-20b", "reasoning_effort": "low"},
    "equilibrado": {"model": _MODEL_NAME, "reasoning_effort": "medium"},
    "avanzado": {"model": _MODEL_NAME, "reasoning_effort": "high"},
}


def get_response_mode(mode: str = "equilibrado") -> dict[str, str | None]:
    """Devuelve la configuración Groq de un modo validado."""
    try:
        return RESPONSE_MODES[mode]
    except KeyError as error:
        raise ValueError("El modo debe ser: rapido, equilibrado o avanzado") from error


def _completion_options(model: str, reasoning_effort: str | None, stream: bool = False) -> dict:
    options = {
        "model": model,
        "messages": [],
        "temperature": 0.2,
        "max_tokens": 700,
        "stream": stream,
    }
    if model.startswith("openai/gpt-oss") and reasoning_effort:
        options["reasoning_effort"] = reasoning_effort
    return options


def truncate_text(text: str, max_chars: int = MAX_INPUT_CHARS) -> str:
    """Limita el texto enviado al modelo para respetar el presupuesto del free tier."""
    return text[:max_chars]


def generate_risk_response(
    financial_text: str,
    indicators: dict[str, float],
    alerts: list[dict[str, str | float]],
    context: list[str],
    modo: str = "equilibrado",
    model: str | None = None,
    reasoning_effort: str | None = None,
) -> str | None:
    """Genera un resumen con Groq; devuelve None si no hay configuración disponible."""
    mode_config = get_response_mode(modo)
    model = model or mode_config["model"]
    reasoning_effort = reasoning_effort if reasoning_effort is not None else mode_config["reasoning_effort"]
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None

    client = Groq(api_key=api_key)
    prompt = (
        "Analiza este estado financiero en español. Redacta un resumen breve, "
        "profesional y prudente con nivel de riesgo, evidencias y recomendaciones. "
        "No inventes datos.\n\n"
        f"Texto del PDF:\n{truncate_text(financial_text)}\n\n"
        f"Indicadores calculados: {indicators}\n"
        f"Alertas: {alerts}\n"
        f"Contexto: {context}"
    )
    completion = client.chat.completions.create(
        **_completion_options(model, reasoning_effort) | {
            "messages": [
                {"role": "system", "content": "Eres un analista de riesgo financiero."},
                {"role": "user", "content": prompt},
            ]
        },
    )
    return completion.choices[0].message.content


def generate_question_response(
    question: str,
    context: list[str],
    financial_text: str,
    modo: str = "equilibrado",
    model: str | None = None,
    reasoning_effort: str | None = None,
) -> str | None:
    """Responde preguntas sobre un PDF usando únicamente el cliente Groq."""
    mode_config = get_response_mode(modo)
    model = model or mode_config["model"]
    reasoning_effort = reasoning_effort if reasoning_effort is not None else mode_config["reasoning_effort"]
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None

    client = Groq(api_key=api_key)
    prompt = (
        "Responde en español la pregunta sobre el documento financiero. "
        "Usa solo la información disponible, indica si no hay evidencia suficiente "
        "y no inventes datos.\n\n"
        f"Pregunta: {question}\n\n"
        f"Fragmentos relevantes:\n{truncate_text(chr(10).join(context))}\n\n"
        f"Texto del PDF:\n{truncate_text(financial_text)}"
    )
    completion = client.chat.completions.create(
        **_completion_options(model, reasoning_effort) | {
            "max_tokens": 500,
            "messages": [
                {"role": "system", "content": "Eres un analista financiero que responde preguntas con precisión."},
                {"role": "user", "content": prompt},
            ]
        },
    )
    return completion.choices[0].message.content


def generate_question_response_stream(
    question: str,
    context: list[str],
    financial_text: str,
    mode: str = "equilibrado",
) -> Iterator[str]:
    """Genera fragmentos de respuesta desde Groq según el modo elegido."""
    mode_config = get_response_mode(mode)
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        yield "No hay una clave GROQ_API_KEY configurada para responder la pregunta."
        return

    prompt = (
        "Responde en español la pregunta sobre el documento financiero. "
        "Usa solo la información disponible, indica si no hay evidencia suficiente "
        "y no inventes datos.\n\n"
        f"Pregunta: {question}\n\n"
        f"Fragmentos relevantes:\n{truncate_text(chr(10).join(context))}\n\n"
        f"Texto del PDF:\n{truncate_text(financial_text)}"
    )
    client = Groq(api_key=api_key)
    options = _completion_options(mode_config["model"], mode_config["reasoning_effort"], stream=True)
    options["messages"] = [
        {"role": "system", "content": "Eres un analista financiero que responde preguntas con precisión."},
        {"role": "user", "content": prompt},
    ]
    for chunk in client.chat.completions.create(**options):
        content = chunk.choices[0].delta.content
        if content:
            yield content


def generar_respuesta(
    pregunta: str,
    contexto: list[str],
    texto_financiero: str,
    modo: str = "equilibrado",
) -> str | None:
    """Nombre público en español para responder una pregunta con Groq."""
    return generate_question_response(pregunta, contexto, texto_financiero, modo=modo)


def generar_respuesta_stream(
    pregunta: str,
    contexto: list[str],
    texto_financiero: str,
    modo: str = "equilibrado",
) -> Iterator[str]:
    """Nombre público en español para generar una respuesta por streaming."""
    yield from generate_question_response_stream(pregunta, contexto, texto_financiero, modo)