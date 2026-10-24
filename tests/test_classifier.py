
from ticket_classifier import classify_ticket

test_emails = [
    {
        "name": "Billing complaint",
        "email": "I was charged twice for my monthly subscription. Please check this.",
    },
    {
        "name": "Technical issue",
        "email": "The application crashes every time I try to export a report.",
    },
    {
        "name": "Account issue",
        "email": "I cannot log in even after resetting my password.",
    },
    {
        "name": "General inquiry",
        "email": "What are your customer support working hours?",
    },
    {
        "name": "Positive feedback",
        "email": "Thank you for your help. The issue is resolved and everything works perfectly.",
    },
]

for ticket in test_emails:
    print(f"\n--- {ticket['name']} ---")
    print("Email:", ticket["email"])

    try:
        prediction = classify_ticket(ticket["email"])
        print("Prediction:", prediction)
    except Exception as error:
        print("Error:", error)
