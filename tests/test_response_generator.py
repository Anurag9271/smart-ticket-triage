
import pytest

from rag.response_generator import SupportResponseGenerator


@pytest.fixture
def generator():
    return SupportResponseGenerator()


@pytest.fixture
def retrieval_results():
    return {
        "documents": [[
            "Question: Why was I charged twice?\n\n"
            "Answer: Duplicate charges may occur because "
            "of payment retries. Contact support if both "
            "transactions are completed."
        ]],
        "metadatas": [[
            {
                "question": "Why was I charged twice?",
                "source": "billing_faq.md",
                "category": "billing"
            }
        ]],
        "distances": [[0.12]]
    }


def test_generate_response(
    generator,
    retrieval_results,
    monkeypatch
):
    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "message": {
                    "content": (
                        "We're sorry for the inconvenience. "
                        "Please check whether both transactions "
                        "were completed."
                    )
                }
            }

    def mock_post(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(
        "rag.response_generator.httpx.post",
        mock_post
    )

    result = generator.generate(
        "I was charged twice.",
        retrieval_results
    )

    assert result["status"] == "draft_generated"
    assert result["draft"] is not None
    assert len(result["evidence"]) == 1


def test_no_evidence_requires_escalation(generator):
    result = generator.generate(
        "I need help with my account.",
        {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]]
        }
    )

    assert result["status"] == "escalation_required"
    assert result["draft"] is None


def test_insufficient_evidence_response(
    generator,
    retrieval_results,
    monkeypatch
):
    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "message": {
                    "content": "INSUFFICIENT_EVIDENCE"
                }
            }

    monkeypatch.setattr(
        "rag.response_generator.httpx.post",
        lambda *args, **kwargs: MockResponse()
    )

    result = generator.generate(
        "Can you compensate me ₹5,000?",
        retrieval_results
    )

    assert result["status"] == "escalation_required"
    assert result["draft"] is None


def test_empty_ticket_raises_error(generator):
    with pytest.raises(ValueError):
        generator.generate(
            "",
            {
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]]
            }
        )
