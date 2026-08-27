from typing import Any, TypedDict


class FinancialState(TypedDict, total=False):
    """Estado parcial compartido y actualizado por los nodos de LangGraph.

    ``total=False`` es intencional: cada nodo solo necesita devolver los campos
    que calcula, mientras LangGraph conserva el resto del estado acumulado.
    """

    pdf_path: str
    extracted_text: str
    financial_data: dict[str, float]
    indicators: dict[str, dict[str, Any]]
    alerts: list[dict[str, Any]]
    context: list[str]

    nivel_riesgo: str
    explicacion_riesgo: str
    respuesta_final: dict[str, Any]
    errores: list[str]

    # Claves heredadas que siguen usando la API y algunos nodos actuales.
    final_response: dict[str, Any]
    error: str
