
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ticket_classifier import classify_ticket

app = FastAPI(
    title="Smart Customer Support Ticket Triage",
    description="API for classifying customer support emails",
    version="1.0.0",
)


class TicketRequest(BaseModel):
    email: str = Field(
        ...,
        min_length=1,
        description="The customer's email text",
        examples=["I was charged twice for my subscription."],
    )


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "Ticket triage API is running",
    }


@app.post("/tickets/classify")
def classify_customer_ticket(ticket: TicketRequest):
    email = ticket.email.strip()

    if not email:
        raise HTTPException(
            status_code=422,
            detail="Email cannot be empty or whitespace only.",
        )

    try:
        result = classify_ticket(email)
        return {
            "email": email,
            "category": result["category"],
            "urgency": result["urgency"],
            "sentiment": result["sentiment"],
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Ticket classification failed.",
        )
