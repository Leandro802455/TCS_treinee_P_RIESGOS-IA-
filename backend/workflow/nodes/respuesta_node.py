from ..state import FinancialState
from ...agent.llm_client import generate_risk_response
from ...agent.rag import retrieve_context
from ...observability.tracing import trace_node


@trace_node("respuesta_node")
def respuesta_node(state: FinancialState) -> FinancialState:
    indicators = state.get("indicators", {})
    alerts = state.get("alerts", [])
    query = " ".join(alert["descripcion"] for alert in alerts) or "evaluación financiera general"
    context = retrieve_context(query)
    critical = sum(alert["severidad"] == "CRÍTICA" for alert in alerts)
    high = sum(alert["severidad"] == "ALTA" for alert in alerts)
    medium = sum(alert["severidad"] == "MEDIA" for alert in alerts)
    low = sum(alert["severidad"] == "BAJA" for alert in alerts)
    if critical or high:
        level = "alto"
    elif medium:
        level = "medio"
    elif low:
        level = "bajo"
    else:
        level = "bajo"
    recommendations = [alert["recomendacion"] for alert in alerts]
    if not recommendations:
        recommendations.append("Mantener seguimiento trimestral de los indicadores financieros.")
    llm_summary = None
    try:
        llm_summary = generate_risk_response(
            state.get("extracted_text", ""), indicators, alerts, context
        )
    except Exception:
        llm_summary = None
    final_response = {
        "nivel_riesgo": level,
        "resumen": llm_summary or f"Se identificaron {len(alerts)} alerta(s); el nivel estimado es {level}.",
        "indicadores": indicators,
        "alertas": alerts,
        "recomendaciones": recommendations,
        "contexto": context,
    }
    return {
        "context": context,
        "nivel_riesgo": level,
        "explicacion_riesgo": final_response["resumen"],
        "respuesta_final": final_response,
        "errores": [],
        "final_response": final_response,
    }
