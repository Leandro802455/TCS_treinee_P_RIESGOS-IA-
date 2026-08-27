import json

from backend.agent.storage import AnalysisRepository


def test_analysis_repository_persists_results(tmp_path):
    repository = AnalysisRepository(tmp_path / "analysis.db")
    result = {
        "nivel_riesgo": "medio",
        "indicadores": {"endeudamiento": {"valor": 0.6}},
        "alertas": [{"indicador": "endeudamiento"}],
        "resumen": "Seguimiento recomendado.",
    }

    analysis_id = repository.save_analysis("demo.pdf", result)
    recent = repository.list_recent()

    assert analysis_id == 1
    assert repository.count() == 1
    assert recent[0]["file_name"] == "demo.pdf"
    assert json.loads(recent[0]["response_json"])["nivel_riesgo"] == "medio"
