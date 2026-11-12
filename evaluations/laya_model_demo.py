
from laya import Router

# 1. Initialize Laya
router = Router()

# 2. Sample customer support ticket
ticket = """
I was charged twice for my subscription.
This is unacceptable! I need my duplicate payment refunded immediately.
"""

# 3. Define the classification tasks
questions = {
    "category": {
        "type": "choice",
        "instructions": "Which support department should handle this ticket?",
        "criteria": {
            "billing": "Payments, invoices, duplicate charges, and refunds",
            "technical": "Software bugs and application errors",
            "account": "Login and account access issues",
            "other": "Other customer support requests",
        },
    },

    "urgency": {
        "type": "choice",
        "instructions": "How urgently should the support team handle this ticket?",
        "criteria": {
            "low": "Routine request with no immediate action needed",
            "medium": "Issue needs attention but is not time-critical",
            "high": "Time-sensitive issue requiring prompt attention",
        },
    },

    "sentiment": {
        "type": "choice",
        "instructions": "What is the customer's overall emotional tone?",
        "criteria": {
            "positive": "Satisfied, happy, or appreciative",
            "neutral": "Factual or emotionally neutral",
            "negative": "Angry, frustrated, disappointed, or dissatisfied",
        },
    },
}

# 4. Predict all three fields
result = router.predict(ticket, questions)

# 5. Display the complete result
print("Classification result:")
print(result)

# 6. Display only the predicted labels
answers = result["answers"]

print("\nPredicted labels:")
for field in ("category", "urgency", "sentiment"):
    print(f"{field.title()}: {answers[field]['choice']}")
