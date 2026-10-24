
from laya import Router
from urgency_policy import classify_urgency
from category_policy import apply_category_policy

router = Router()

QUESTIONS = {
    "category": {
        "type": "choice",
        "instructions": (
            "Classify the main reason for the customer's email. "
            "Choose exactly one label. Use billing for payments, "
            "invoices, charges and refunds. Use technical for bugs, "
            "crashes, errors and broken features. Use account for "
            "login, passwords, access and profile changes. Use other "
            "for general questions, business hours, service information, "
            "and feedback that does not identify a specific issue. "
            "Do not classify every question as technical."
        ),
        "criteria": [
            "billing",
            "technical",
            "account",
            "other",
        ],
    },
    "sentiment": {
        "type": "choice",
        "instructions": (
            "Classify the customer's overall emotional tone. "
            "Choose exactly one label. Use positive for praise, "
            "satisfaction or thanks; negative for complaints or "
            "frustration; neutral for factual or informational "
            "messages without a clear emotional tone."
        ),
        "criteria": [
            "positive",
            "neutral",
            "negative",
        ],
    },
}


def classify_ticket(email: str) -> dict:
    """Classify an email and apply the urgency policy."""

    result = router.predict(email, QUESTIONS)
    answers = result["answers"]

    category = apply_category_policy(
    email,
    answers["category"]["choice"].lower().strip().split(":")[0],
    )

    sentiment = (
        answers["sentiment"]["choice"]
        .lower()
        .strip()
        .split(":")[0]
    )
    urgency = classify_urgency(email)

    return {
        "category": category,
        "urgency": urgency,
        "sentiment": sentiment,
    }


if __name__ == "__main__":
    sample_email = """
    I have been charged twice for my subscription.
    Please check the duplicate payment.
    """

    prediction = classify_ticket(sample_email)
    print("Ticket classification:")
    print(prediction)
