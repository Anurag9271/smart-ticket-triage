
from laya import Router

# 1. Initialize Laya once
router = Router()

# 2. Define the classification tasks
questions = {
    "category": {
        "type": "choice",
        "instructions": "Which support department should handle this ticket?",
        "criteria": {
            "billing": "Payments, invoices, duplicate charges, and refunds",
            "technical": "Software bugs, crashes, and application errors",
            "account": "Login, password, and account access issues",
            "other": "Other customer support requests",
        },
    },
    "urgency": {
        "type": "choice",
        "instructions": (
            "Classify urgency based on the impact and time sensitivity "
            "of the issue, not on how angry the customer sounds."
        ),
        "criteria": {
            "low": (
                "No immediate action is needed, such as general questions, "
                "compliments, or routine requests."
            ),
            "medium": (
                "A feature or account has a problem, but there is no evidence "
                "of a critical outage, major business impact, or urgent deadline."
            ),
            "high": (
                "A critical service is unavailable, a major business workflow "
                "is blocked, or there is clear evidence of urgent time-sensitive impact."
            ),
        },
    },
    "sentiment": {
        "type": "choice",
        "instructions": (
            "Classify the emotion expressed by the customer. "
            "A complaint can be negative even without explicit angry words."
        ),
        "criteria": {
            "positive": (
                "The customer clearly expresses happiness, gratitude, "
                "satisfaction, or praise."
            ),
            "neutral": (
                "The message is mainly factual and expresses neither "
                "clear satisfaction nor dissatisfaction."
            ),
            "negative": (
                "The customer expresses frustration, dissatisfaction, "
                "disappointment, or a problem in a clearly negative tone."
            ),
        },
    },
}

# 3. Prepare different customer emails
tickets = [
    {
        "id": 1,
        "email": "I was charged twice for my subscription. Please refund the duplicate payment.",
        "expected": {
            "category": "billing",
            "urgency": "medium",
            "sentiment": "negative",
        },
    },
    {
        "id": 2,
        "email": "The application crashes every time I click Export. I cannot download my report.",
        "expected": {
            "category": "technical",
            "urgency": "high",
            "sentiment": "negative",
        },
    },
    {
        "id": 3,
        "email": "I cannot log in to my account, even after resetting my password.",
        "expected": {
            "category": "account",
            "urgency": "medium",
            "sentiment": "neutral",
        },
    },
    {
        "id": 4,
        "email": "Thank you for helping me fix my invoice. Your support team was very helpful!",
        "expected": {
            "category": "billing",
            "urgency": "low",
            "sentiment": "positive",
        },
    },
]

# 4. Classify each ticket and display the results
for ticket in tickets:
    print("\n" + "=" * 60)
    print(f"Ticket ID: {ticket['id']}")
    print(f"Email: {ticket['email']}")

    result = router.predict(ticket["email"], questions)
    answers = result["answers"]

    print("\nPredictions:")

    for field in ("category", "urgency", "sentiment"):
        predicted = answers[field]["choice"]
        expected = ticket["expected"][field]

        print(
            f"{field.title():10} "
            f"Predicted: {predicted:10} "
            f"Expected: {expected:10} "
            f"{'MATCH' if predicted == expected else 'REVIEW'}"
        )
