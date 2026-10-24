
from laya import Router

# 1. Initialize Laya
router = Router()

# 2. Classification definitions
questions = {
    "category": {
        "type": "choice",
        "instructions": "Which support department should handle this ticket?",
        "criteria": {
            "billing": "Payments, invoices, refunds, and subscriptions",
            "technical": "Software bugs, crashes, and application errors",
            "account": "Login, password, and account access issues",
            "other": "General questions and requests outside the other categories",
        },
    },
    "urgency": {
        "type": "choice",
        "instructions": (
            "Classify urgency based on impact and time sensitivity, "
            "not simply the customer's emotional tone."
        ),
        "criteria": {
            "low": "Routine request or question with no immediate action needed",
            "medium": "A problem needs attention, but no critical impact is stated",
            "high": "A critical service or important workflow is blocked, "
                    "or an explicit urgent deadline requires prompt action",
        },
    },
    "sentiment": {
        "type": "choice",
        "instructions": "Classify the emotion expressed in the customer's message",
        "criteria": {
            "positive": "Clear gratitude, praise, happiness, or satisfaction",
            "neutral": "Factual message without clear positive or negative emotion",
            "negative": "Clear frustration, anger, disappointment, or dissatisfaction",
        },
    },
}

# 3. Evaluation dataset
# These expected labels are our initial human-defined reference labels.
tickets = [
    {
        "id": 1,
        "email": "I was charged twice. I am frustrated and want the duplicate payment refunded.",
        "expected": {"category": "billing", "urgency": "medium", "sentiment": "negative"},
    },
    {
        "id": 2,
        "email": "Please explain how the monthly subscription fee is calculated.",
        "expected": {"category": "billing", "urgency": "low", "sentiment": "neutral"},
    },
    {
        "id": 3,
        "email": "Thank you for correcting my invoice so quickly. I really appreciate it!",
        "expected": {"category": "billing", "urgency": "low", "sentiment": "positive"},
    },
    {
        "id": 4,
        "email": "My refund has not arrived, and I am very disappointed with this delay.",
        "expected": {"category": "billing", "urgency": "medium", "sentiment": "negative"},
    },
    {
        "id": 5,
        "email": "Could you send me a copy of last month's invoice?",
        "expected": {"category": "billing", "urgency": "low", "sentiment": "neutral"},
    },
    {
        "id": 6,
        "email": "The application crashes whenever I open the reports page. This is very frustrating.",
        "expected": {"category": "technical", "urgency": "medium", "sentiment": "negative"},
    },
    {
        "id": 7,
        "email": "The entire service is down for our team, and our essential work has stopped.",
        "expected": {"category": "technical", "urgency": "high", "sentiment": "negative"},
    },
    {
        "id": 8,
        "email": "How do I export a report as a CSV file?",
        "expected": {"category": "technical", "urgency": "low", "sentiment": "neutral"},
    },
    {
        "id": 9,
        "email": "The latest update broke the application. I am extremely unhappy about this.",
        "expected": {"category": "technical", "urgency": "medium", "sentiment": "negative"},
    },
    {
        "id": 10,
        "email": "Thanks! The export feature works perfectly now.",
        "expected": {"category": "technical", "urgency": "low", "sentiment": "positive"},
    },
    {
        "id": 11,
        "email": "I cannot sign in even after resetting my password. This is really annoying.",
        "expected": {"category": "account", "urgency": "medium", "sentiment": "negative"},
    },
    {
        "id": 12,
        "email": "Our administrator is locked out of the account and our team cannot access the system.",
        "expected": {"category": "account", "urgency": "high", "sentiment": "negative"},
    },
    {
        "id": 13,
        "email": "How can I change the email address associated with my account?",
        "expected": {"category": "account", "urgency": "low", "sentiment": "neutral"},
    },
    {
        "id": 14,
        "email": "I am disappointed that my account was locked without an explanation.",
        "expected": {"category": "account", "urgency": "medium", "sentiment": "negative"},
    },
    {
        "id": 15,
        "email": "Thank you for helping me recover my account. Your support was excellent!",
        "expected": {"category": "account", "urgency": "low", "sentiment": "positive"},
    },
    {
        "id": 16,
        "email": "Where can I find your company's office address?",
        "expected": {"category": "other", "urgency": "low", "sentiment": "neutral"},
    },
    {
        "id": 17,
        "email": "Please tell me your business hours for customer support.",
        "expected": {"category": "other", "urgency": "low", "sentiment": "neutral"},
    },
    {
        "id": 18,
        "email": "I am very unhappy that nobody has responded to my previous support request.",
        "expected": {"category": "other", "urgency": "medium", "sentiment": "negative"},
    },
    {
        "id": 19,
        "email": "Thank you for explaining the service so clearly. Your team was very helpful!",
        "expected": {"category": "other", "urgency": "low", "sentiment": "positive"},
    },
    {
        "id": 20,
        "email": "Please confirm whether your service supports multiple languages.",
        "expected": {"category": "other", "urgency": "low", "sentiment": "neutral"},
    },
]

# 4. Run predictions and track correct answers
fields = ("category", "urgency", "sentiment")
correct = {field: 0 for field in fields}
mismatches = []

for ticket in tickets:
    result = router.predict(ticket["email"], questions)
    answers = result["answers"]

    print(f"\nTicket {ticket['id']}: {ticket['email']}")

    for field in fields:
        predicted = answers[field]["choice"]
        expected = ticket["expected"][field]
        is_correct = predicted == expected

        if is_correct:
            correct[field] += 1
        else:
            mismatches.append({
                "id": ticket["id"],
                "field": field,
                "expected": expected,
                "predicted": predicted,
            })

        status = "MATCH" if is_correct else "REVIEW"
        print(
            f"  {field.title():10} "
            f"Expected: {expected:10} "
            f"Predicted: {predicted:10} {status}"
        )

# 5. Display evaluation summary
print("\n" + "=" * 55)
print("EVALUATION SUMMARY")
print("=" * 55)

total_predictions = len(tickets) * len(fields)
total_correct = sum(correct.values())

for field in fields:
    accuracy = correct[field] / len(tickets) * 100
    print(f"{field.title():10}: {correct[field]}/{len(tickets)} correct ({accuracy:.1f}%)")

overall_accuracy = total_correct / total_predictions * 100
print(f"\nOverall: {total_correct}/{total_predictions} ({overall_accuracy:.1f}%)")

print(f"\nPredictions requiring review: {len(mismatches)}")
for item in mismatches:
    print(
        f"Ticket {item['id']} | {item['field']} | "
        f"Expected: {item['expected']} | Predicted: {item['predicted']}"
    )
