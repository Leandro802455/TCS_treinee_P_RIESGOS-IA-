from backend.agent.rag import LocalVectorStore, retrieve_context, split_into_chunks


def test_retrieve_context_is_relevant():
    context = retrieve_context("endeudamiento pasivos activos", top_k=1)
    assert len(context) == 1
    assert "endeudamiento" in context[0]


def test_empty_query_returns_empty_context():
    assert retrieve_context("") == []


def test_documents_are_split_and_stored():
    store = LocalVectorStore(chunk_size=20, overlap=5)
    store.add_documents(["endeudamiento alto y deuda externa relevante"], document_prefix="guide")

    assert len(store.chunks) > 1
    assert store.chunks[0].document_id == "guide-0"
    assert store.chunks[0].chunk_id == 0


def test_search_returns_relevant_chunks():
    store = LocalVectorStore()
    store.add_documents([
        "El endeudamiento alto aumenta la dependencia de financiación externa.",
        "La liquidez mide la capacidad de pagar obligaciones de corto plazo.",
    ])

    results = store.search("deuda y financiación externa", top_k=1)

    assert len(results) == 1
    assert "endeudamiento" in results[0].text


def test_chunk_parameters_are_validated():
    try:
        split_into_chunks("texto", chunk_size=10, overlap=10)
    except ValueError:
        pass
    else:
        raise AssertionError("Se esperaba ValueError para overlap inválido")
