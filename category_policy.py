
def apply_category_policy(email: str, predicted_category: str) -> str:
    """Apply transparent rules to clear technical issues and feedback."""

    text = email.lower().strip()

    # Clear technical failure signals
    technical_signals = [
        "keeps failing",
        "freezes",
        "crashes",
        "error message",
        "not working",
        "is broken",
        "failed to generate",
        "unable to generate",
        "doesn't work",
        "does not work",
    ]

    if any(signal in text for signal in technical_signals):
        return "technical"

    # General appreciation or feedback
    feedback_signals = [
        "thank you for your help",
        "thanks for your help",
        "everything works perfectly",
        "the issue is resolved",
        "great support",
        "excellent service",
        "patient and helpful",
        "very helpful",
    ]

    has_feedback = any(
        phrase in text for phrase in feedback_signals
    )

    # Avoid overriding feedback that mentions a specific support issue.
    specific_issue_signals = [
        "charged", "payment", "invoice", "refund",
        "crash", "error", "broken", "login",
        "log in", "password", "account locked",
        "subscription",
    ]

    has_specific_issue = any(
        signal in text for signal in specific_issue_signals
    )

    if has_feedback and not has_specific_issue:
        return "other"

    return predicted_category
