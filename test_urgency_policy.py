
from urgency_policy import classify_urgency

# Expected labels from our existing evaluation dataset
tickets = [
    ("A customer was charged twice for the same subscription.", "medium"),
    ("How is my monthly subscription fee calculated?", "low"),
    ("Thank you for sending the invoice.", "low"),
    ("My refund has been delayed for several days.", "medium"),
    ("Could you send me a copy of my invoice?", "low"),
    ("The application crashes whenever I open it.", "medium"),
    ("The entire service is down and our essential work has stopped.", "high"),
    ("How do I export a report as a CSV file?", "low"),
    ("The latest app update broke the application.", "medium"),
    ("Thanks, the export feature works perfectly now.", "low"),
    ("I cannot sign in after resetting my password.", "medium"),
    ("Our administrator is locked out and the team cannot access the system.", "high"),
    ("How can I change the email address associated with my account?", "low"),
    ("I'm disappointed because my account has been locked.", "medium"),
    ("Thanks for helping me recover my account.", "low"),
    ("What is your office address?", "low"),
    ("What are your business hours?", "low"),
    ("I contacted support earlier but haven't received a response.", "medium"),
    ("Thank you for explaining your service. It was very helpful.", "low"),
    ("Does your service support multiple languages?", "low"),
]

correct = 0

for index, (email, expected) in enumerate(tickets, start=1):
    predicted = classify_urgency(email)
    is_correct = predicted == expected

    if is_correct:
        correct += 1

    status = "PASS" if is_correct else "CHECK"
    print(f"{index:02}. Expected: {expected:6} | "
          f"Predicted: {predicted:6} | {status}")
    print(f"    Email: {email}")

accuracy = correct / len(tickets) * 100

print("\n--- Rule-Based Urgency Evaluation ---")
print(f"Correct: {correct}/{len(tickets)}")
print(f"Accuracy: {accuracy:.1f}%")
