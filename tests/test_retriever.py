
from rag.retriever import FAQRetriever


def test_index_documents(tmp_path):
    retriever = FAQRetriever(
        persist_directory=str(tmp_path / "chroma_db")
    )

    indexed_count = retriever.index_documents()

    assert indexed_count == 18
    assert retriever.vector_store.count() == 18


def test_retrieve_duplicate_payment(tmp_path):
    retriever = FAQRetriever(
        persist_directory=str(tmp_path / "chroma_db")
    )

    retriever.index_documents()

    results = retriever.retrieve(
        query="Money was deducted from my account twice",
        top_k=3
    )

    top_result = results["documents"][0][0]

    assert "charged twice" in top_result.lower()


def test_retrieve_with_category_filter(tmp_path):
    retriever = FAQRetriever(
        persist_directory=str(tmp_path / "chroma_db")
    )

    retriever.index_documents()

    results = retriever.retrieve(
        query="How do I cancel my subscription?",
        top_k=3,
        category="billing"
    )

    assert len(results["documents"][0]) > 0

    for metadata in results["metadatas"][0]:
        assert metadata["category"] == "billing"


def test_empty_query_raises_error(tmp_path):
    retriever = FAQRetriever(
        persist_directory=str(tmp_path / "chroma_db")
    )

    import pytest

    with pytest.raises(ValueError):
        retriever.retrieve("")


def test_invalid_top_k_raises_error(tmp_path):
    retriever = FAQRetriever(
        persist_directory=str(tmp_path / "chroma_db")
    )

    import pytest

    with pytest.raises(ValueError):
        retriever.retrieve(
            query="Payment issue",
            top_k=0
        )
