def classify_urgency(email: str) -> str:
    """Assign urgency using transparent business rules."""

    text = email.lower()

    high_signals = [
        "entire service is down",
        "production is down",
        "critical service is unavailable",
        "essential work has stopped",
        "all users are blocked",
        "security breach",
        "cannot access the system",
    ]

    low_signals = [
        "how do i",
        "how can i",
        "could you send me a copy",
        "please explain",
        "where can i find",
        "business hours",
        "office address",
        "thank you",
        "how is my",
        "does your service support",
        "thanks",
        "appreciate it",
        "works perfectly",
        "supports multiple languages",
    ]

    # Critical impact takes priority.
    if any(signal in text for signal in high_signals):
        return "high"

    # Routine questions and positive feedback.
    if any(signal in text for signal in low_signals):
        return "low"

    # Active issues without clear critical impact.
    return "medium"