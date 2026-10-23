from laya import Router

router = Router()

ticket = """
I was charged twice for my subscription.
Please refund the duplicate payment immediately.
"""

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
    }
}

result = router.predict(ticket, questions)

print("Classification result:")
print(result)