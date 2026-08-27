from pathlib import Path

from backend.agent import qa


SAMPLE_PDF = Path("data/ejemplo_financiero.pdf")


def test_question_stream_uses_mode_and_appends_source(monkeypatch):
    received = {}

    def fake_response(question, context, financial_text, mode):
        received["mode"] = mode
        received["context"] = context
        yield "Respuesta basada en el PDF."

    monkeypatch.setattr(qa, "generar_respuesta_stream", fake_response)
    chunks = list(qa.answer_question_stream(SAMPLE_PDF, "¿Cuál es el riesgo de pasivos y endeudamiento?", "avanzado"))

    assert received["mode"] == "avanzado"
    assert received["context"]
    assert chunks[-1].startswith("\n\n[FUENTE]:")


def test_question_stream_rejects_empty_question():
    try:
        list(qa.answer_question_stream(SAMPLE_PDF, "   "))
    except ValueError as error:
        assert "vacía" in str(error)
    else:
        raise AssertionError("Se esperaba ValueError")
