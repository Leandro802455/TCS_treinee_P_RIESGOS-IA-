from langgraph.graph import END, START, StateGraph

from .nodes.alertas_node import alertas_node
from .nodes.calculadora_node import calculadora_node
from .nodes.extractor_node import extractor_node
from .nodes.respuesta_node import respuesta_node
from .state import FinancialState
from ..observability.tracing import track_analysis


def build_graph():
    """Construye y compila el flujo lineal de análisis financiero."""
    workflow = StateGraph(FinancialState)
    workflow.add_node("extractor_node", extractor_node)
    workflow.add_node("calculadora_node", calculadora_node)
    workflow.add_node("alertas_node", alertas_node)
    workflow.add_node("respuesta_node", respuesta_node)
    workflow.add_edge(START, "extractor_node")
    workflow.add_edge("extractor_node", "calculadora_node")
    workflow.add_edge("calculadora_node", "alertas_node")
    workflow.add_edge("alertas_node", "respuesta_node")
    workflow.add_edge("respuesta_node", END)
    return workflow.compile()


risk_graph = build_graph()


def analyze_pdf(pdf_path: str) -> FinancialState:
    initial_state = {"pdf_path": pdf_path}
    with track_analysis(initial_state):
        return risk_graph.invoke(initial_state)
