
import pytest

import ticket_classifier


def mock_laya(monkeypatch, category, sentiment):
    """Mock Laya predictions to make tests predictable."""

    def fake_predict(email, questions):
        return {
            "answers": {
                "category": {"choice": category},
                "sentiment": {"choice": sentiment},
            }
        }

    monkeypatch.setattr(
        ticket_classifier.router,
        "predict",
        fake_predict,
    )


@pytest.mark.parametrize(
    "email, predicted_category, sentiment, expected_category, expected_urgency",
    [
        (
            "I was charged twice for my subscription.",
            "billing",
            "negative",
            "billing",
            "medium",
        ),
        (
            "The application crashes every time I export a report.",
            "other",
            "negative",
            "technical",
            "medium",
        ),
        (
            "I cannot log in after resetting my password.",
            "account",
            "negative",
            "account",
            "medium",
        ),
        (
            "What are your customer support working hours?",
            "other",
            "neutral",
            "other",
            "low",
        ),
        (
            "Thank you for your help. Everything works perfectly.",
            "other",
            "positive",
            "other",
            "low",
        ),
    ],
)
def test_classify_ticket(
    monkeypatch,
    email,
    predicted_category,
    sentiment,
    expected_category,
    expected_urgency,
):
    mock_laya(monkeypatch, predicted_category, sentiment)

    result = ticket_classifier.classify_ticket(email)

    assert result["category"] == expected_category
    assert result["urgency"] == expected_urgency
    assert result["sentiment"] == sentiment

    assert set(result.keys()) == {
        "category",
        "urgency",
        "sentiment",
    }
