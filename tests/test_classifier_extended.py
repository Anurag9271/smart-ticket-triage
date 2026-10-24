
import pytest

from ticket_classifier import classify_ticket


TEST_CASES = [
    {
        "email": "My last payment appears twice on the statement.",
        "category": "billing",
        "sentiment": "negative",
    },
    {
        "email": "Where can I download the receipt for April?",
        "category": "billing",
        "sentiment": "neutral",
    },
    {
        "email": "The dashboard freezes whenever I generate a PDF.",
        "category": "technical",
        "sentiment": "negative",
    },
    {
        "email": "Could you explain how to enable dark mode?",
        "category": "technical",
        "sentiment": "neutral",
    },
    {
        "email": "My password reset link has expired.",
        "category": "account",
        "sentiment": "negative",
    },
    {
        "email": "Please update the phone number on my profile.",
        "category": "account",
        "sentiment": "neutral",
    },
    {
        "email": "Which countries can use your service?",
        "category": "other",
        "sentiment": "neutral",
    },
    {
        "email": "Your team was very patient and helpful.",
        "category": "other",
        "sentiment": "positive",
    },
    {
        "email": "I am frustrated that the report keeps failing.",
        "category": "technical",
        "sentiment": "negative",
    },
    {
        "email": "I would like to know your available subscription plans.",
        "category": "billing",
        "sentiment": "neutral",
    },
]


@pytest.mark.parametrize("case", TEST_CASES)
def test_ticket_classification(case):
    result = classify_ticket(case["email"])

    assert result["category"] == case["category"]
    assert result["sentiment"] == case["sentiment"]
