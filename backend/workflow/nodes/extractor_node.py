from ..state import FinancialState
from ...agent.pdf_reader import extract_financial_data, extract_text
from ...observability.tracing import trace_node


@trace_node("extractor_node")
def extractor_node(state: FinancialState) -> FinancialState:
    text = extract_text(state["pdf_path"])
    return {"extracted_text": text, "financial_data": extract_financial_data(text)}
