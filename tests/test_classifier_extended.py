
import pytest

import ticket_classifier


def mock_laya(monkeypatch, category, sentiment):
    """Provide controlled Laya predictions."""

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
    "email, predicted_category, sentiment, expected_category",
    [
        (
            "My last payment appears twice on the statement.",
            "billing",
            "negative",
            "billing",
        ),
        (
            "Where can I download the receipt for April?",
            "billing",
            "neutral",
            "billing",
        ),
        (
            "The dashboard freezes whenever I generate a PDF.",
            "other",
            "negative",
            "technical",
        ),
        (
            "Could you explain how to enable dark mode?",
            "technical",
            "neutral",
            "technical",
        ),
        (
            "My password reset link has expired.",
            "account",
            "negative",
            "account",
        ),
        (
            "Please update the phone number on my profile.",
            "account",
            "neutral",
            "account",
        ),
        (
            "Which countries can use your service?",
            "other",
            "neutral",
            "other",
        ),
        (
            "Your team was very patient and helpful.",
            "other",
            "positive",
            "other",
        ),
        (
            "I am frustrated that the report keeps failing.",
            "other",
            "negative",
            "technical",
        ),
        (
            "I would like to know your available subscription plans.",
            "billing",
            "neutral",
            "billing",
        ),
    ],
)
def test_extended_classification(
    monkeypatch,
    email,
    predicted_category,
    sentiment,
    expected_category,
):
    mock_laya(monkeypatch, predicted_category, sentiment)

    result = ticket_classifier.classify_ticket(email)

    assert result["category"] == expected_category
    assert result["sentiment"] == sentiment
