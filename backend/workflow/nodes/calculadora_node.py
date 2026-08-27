from ..state import FinancialState
from ...agent.indicadores import calculate_indicators
from ...observability.tracing import trace_node


@trace_node("calculadora_node")
def calculadora_node(state: FinancialState) -> FinancialState:
    return {"indicators": calculate_indicators(state.get("financial_data", {}))}
