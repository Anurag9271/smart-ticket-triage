
import numpy as np
import pytest

from rag.embeddings import FAQEmbedder


class FakeSentenceTransformer:
    """Mock model to avoid downloading a real model in unit tests."""

    def __init__(self, model_name, device):
        self.model_name = model_name
        self.device = device

    def encode(self, texts, **kwargs):
        return np.ones((len(texts), 384), dtype=np.float32)


@pytest.fixture
def embedder(monkeypatch):
    monkeypatch.setattr(
        "rag.embeddings.SentenceTransformer",
        FakeSentenceTransformer
    )

    return FAQEmbedder()


def test_embedding_generation(embedder):
    chunks = [
        {
            "content": "Question: Why was I charged twice?\n\nAnswer: Contact support.",
            "metadata": {
                "category": "billing",
                "faq_number": 1
            }
        }
    ]

    result = embedder.embed_chunks(chunks)

    assert len(result) == 1
    assert len(result[0]["embedding"]) == 384
    assert result[0]["metadata"]["category"] == "billing"


def test_empty_chunks(embedder):
    result = embedder.embed_chunks([])

    assert result == []


def test_missing_content_raises_error(embedder):
    chunks = [{"metadata": {"category": "billing"}}]

    with pytest.raises(ValueError):
        embedder.embed_chunks(chunks)


def test_original_chunks_are_not_modified(embedder):
    chunks = [
        {
            "content": "Sample FAQ",
            "metadata": {"category": "technical"}
        }
    ]

    embedder.embed_chunks(chunks)

    assert "embedding" not in chunks[0]
