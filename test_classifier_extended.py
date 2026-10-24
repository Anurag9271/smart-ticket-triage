
from ticket_classifier import classify_ticket

test_cases = [
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

category_correct = 0
sentiment_correct = 0

for i, case in enumerate(test_cases, start=1):
    result = classify_ticket(case["email"])

    category_ok = result["category"] == case["category"]
    sentiment_ok = result["sentiment"] == case["sentiment"]

    category_correct += category_ok
    sentiment_correct += sentiment_ok

    print(f"\nTest {i}: {case['email']}")
    print(
        f"Category: expected={case['category']}, "
        f"predicted={result['category']}, "
        f"{'PASS' if category_ok else 'CHECK'}"
    )
    print(
        f"Sentiment: expected={case['sentiment']}, "
        f"predicted={result['sentiment']}, "
        f"{'PASS' if sentiment_ok else 'CHECK'}"
    )

print("\n--- Evaluation Summary ---")
print(f"Category accuracy: {category_correct}/{len(test_cases)} "
      f"({category_correct / len(test_cases) * 100:.1f}%)")
print(f"Sentiment accuracy: {sentiment_correct}/{len(test_cases)} "
      f"({sentiment_correct / len(test_cases) * 100:.1f}%)")
