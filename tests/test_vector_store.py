
import pytest

from rag.vector_store import FAQVectorStore


@pytest.fixture
def vector_store(tmp_path):
    return FAQVectorStore(
        persist_directory=str(tmp_path / "chroma_db")
    )


@pytest.fixture
def sample_chunks():
    return [
        {
            "content": "Question: Why was I charged twice?\n\nAnswer: Contact support.",
            "metadata": {
                "source": "billing_faq.md",
                "category": "billing",
                "question": "Why was I charged twice?",
                "faq_number": 1
            },
            "embedding": [1.0, 0.0, 0.0]
        },
        {
            "content": "Question: How do I reset my password?\n\nAnswer: Use account settings.",
            "metadata": {
                "source": "account_faq.md",
                "category": "account",
                "question": "How do I reset my password?",
                "faq_number": 1
            },
            "embedding": [0.0, 1.0, 0.0]
        }
    ]


def test_add_chunks(vector_store, sample_chunks):
    added = vector_store.add_chunks(sample_chunks)

    assert added == 2
    assert vector_store.count() == 2


def test_upsert_prevents_duplicates(vector_store, sample_chunks):
    vector_store.add_chunks(sample_chunks)
    vector_store.add_chunks(sample_chunks)

    assert vector_store.count() == 2


def test_semantic_search(vector_store, sample_chunks):
    vector_store.add_chunks(sample_chunks)

    results = vector_store.search(
        query_embedding=[1.0, 0.0, 0.0],
        n_results=1
    )

    assert results["ids"][0][0] == "billing_faq.md_1"


def test_category_filter(vector_store, sample_chunks):
    vector_store.add_chunks(sample_chunks)

    results = vector_store.search(
        query_embedding=[1.0, 0.0, 0.0],
        n_results=2,
        category="account"
    )

    assert len(results["ids"][0]) == 1
    assert results["metadatas"][0][0]["category"] == "account"


def test_empty_chunks(vector_store):
    assert vector_store.add_chunks([]) == 0
    assert vector_store.count() == 0


def test_search_empty_collection(vector_store):
    results = vector_store.search([1.0, 0.0, 0.0])

    assert results["ids"] == [[]]


def test_invalid_embedding_raises_error(vector_store, sample_chunks):
    sample_chunks[0]["embedding"] = []

    with pytest.raises(ValueError):
        vector_store.add_chunks(sample_chunks)
