from ..state import FinancialState
from ...agent.alertas import detect_alerts
from ...observability.tracing import trace_node


@trace_node("alertas_node")
def alertas_node(state: FinancialState) -> FinancialState:
    """Evalúa los indicadores acumulados y actualiza las alertas del estado."""
    return {"alerts": detect_alerts(state.get("indicators", {}))}
