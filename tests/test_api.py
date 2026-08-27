from fastapi.testclient import TestClient

from backend import main


client = TestClient(main.app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_question_endpoint_rejects_invalid_mode():
    response = client.post(
        "/preguntar",
        files={"file": ("demo.pdf", b"not used", "application/pdf")},
        data={"pregunta": "¿Qué riesgo existe?", "modo": "invalido"},
    )

    assert response.status_code == 400


def test_question_endpoint_streams_text_and_source(monkeypatch):
    def fake_stream(pdf_path, question, mode):
        yield "Respuesta parcial"
        yield "\n\n[FUENTE]: Balance sintético"

    monkeypatch.setattr(main, "answer_question_stream", fake_stream)
    response = client.post(
        "/preguntar",
        files={"file": ("demo.pdf", b"not used", "application/pdf")},
        data={"pregunta": "¿Qué riesgo existe?", "modo": "equilibrado"},
    )

    assert response.status_code == 200
    assert response.text == "Respuesta parcial\n\n[FUENTE]: Balance sintético"
