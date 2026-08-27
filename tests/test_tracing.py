import mlflow

from backend.workflow.graph import analyze_pdf


def test_mlflow_records_analysis_run_and_metadata(tmp_path, monkeypatch):
    tracking_uri = (tmp_path / "mlruns").as_uri()
    monkeypatch.setenv("MLFLOW_ENABLED", "true")
    monkeypatch.setenv("MLFLOW_TRACKING_URI", tracking_uri)
    monkeypatch.setenv("MLFLOW_EXPERIMENT", "test-audit")

    analyze_pdf("data/ejemplo_financiero.pdf")

    mlflow.set_tracking_uri(tracking_uri)
    experiment = mlflow.get_experiment_by_name("test-audit")
    runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])

    assert len(runs) == 1
    assert runs.iloc[0]["tags.analysis.status"] == "completed"
    assert runs.iloc[0]["metrics.analysis.duration_seconds"] >= 0
    for node_name in ("extractor_node", "calculadora_node", "alertas_node", "respuesta_node"):
        assert runs.iloc[0][f"metrics.node.{node_name}.duration_seconds"] >= 0
