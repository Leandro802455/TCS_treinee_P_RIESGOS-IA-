import os
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from functools import wraps
from typing import Any, ParamSpec, TypeVar


P = ParamSpec("P")
R = TypeVar("R")


def _enabled() -> bool:
    return os.getenv("MLFLOW_ENABLED", "true").lower() == "true"


def _configure_mlflow():
    import mlflow

    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns"))
    mlflow.set_experiment(os.getenv("MLFLOW_EXPERIMENT", "agente-riesgo-financiero"))
    return mlflow


def _state_summary(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "keys": sorted(state),
        "text_chars": len(state.get("extracted_text", "")),
        "financial_fields": len(state.get("financial_data", {})),
        "indicator_count": len(state.get("indicators", {})),
        "alert_count": len(state.get("alerts", [])),
        "context_count": len(state.get("context", [])),
    }


@contextmanager
def track_analysis(input_state: dict[str, Any] | None = None) -> Iterator[None]:
    """Registra un análisis completo y su duración en MLflow."""
    if not _enabled():
        yield
        return
    mlflow = _configure_mlflow()
    with mlflow.start_run(run_name="financial-analysis"):
        if input_state:
            mlflow.log_params({"input.pdf_path": str(input_state.get("pdf_path", ""))})
            mlflow.log_dict(_state_summary(input_state), "input_summary.json")
        started = time.perf_counter()
        try:
            yield
            mlflow.log_metric("analysis.duration_seconds", time.perf_counter() - started)
            mlflow.set_tag("analysis.status", "completed")
        except Exception as error:
            mlflow.log_metric("analysis.duration_seconds", time.perf_counter() - started)
            mlflow.set_tag("analysis.status", "failed")
            mlflow.set_tag("analysis.error_type", type(error).__name__)
            raise


def trace_node(name: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Registra duración, entrada y salida resumida de un nodo."""
    def decorator(function: Callable[P, R]) -> Callable[P, R]:
        @wraps(function)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            if not _enabled():
                return function(*args, **kwargs)
            mlflow = _configure_mlflow()
            state = args[0] if args else kwargs.get("state", {})
            started = time.perf_counter()
            mlflow.log_dict(_state_summary(state), f"nodes/{name}/input.json")
            try:
                result = function(*args, **kwargs)
                mlflow.log_metric(f"node.{name}.duration_seconds", time.perf_counter() - started)
                mlflow.log_dict(_state_summary({**state, **result}), f"nodes/{name}/output.json")
                mlflow.set_tag(f"node.{name}.status", "completed")
                return result
            except Exception as error:
                mlflow.log_metric(f"node.{name}.duration_seconds", time.perf_counter() - started)
                mlflow.set_tag(f"node.{name}.status", "failed")
                mlflow.set_tag(f"node.{name}.error_type", type(error).__name__)
                raise

        return wrapper
    return decorator
