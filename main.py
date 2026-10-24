
from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import get_db
from models import Ticket
from ticket_classifier import classify_ticket

app = FastAPI(
    title="Smart Customer Support Ticket Triage",
    description="API for classifying and storing customer support emails",
    version="1.1.0",
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

@app.get("/tickets")
def list_tickets(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    # Count all saved tickets.
    total = db.scalar(
        select(func.count()).select_from(Ticket)
    )

    # Fetch one page, newest tickets first.
    statement = (
        select(Ticket)
        .order_by(Ticket.created_at.desc(), Ticket.id.desc())
        .limit(limit)
        .offset(offset)
    )

    tickets = db.scalars(statement).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "tickets": [
            {
                "id": ticket.id,
                "email": ticket.email,
                "category": ticket.category,
                "urgency": ticket.urgency,
                "sentiment": ticket.sentiment,
                "review_status": ticket.review_status,
                "created_at": ticket.created_at,
            }
            for ticket in tickets
        ],
    }


@app.post("/tickets/classify", status_code=201)
def classify_customer_ticket(
    ticket: TicketRequest,
    db: Session = Depends(get_db),
):
    email = ticket.email.strip()

    if not email:
        raise HTTPException(
            status_code=422,
            detail="Email cannot be empty or whitespace only.",
        )

    try:
        # 1. Classify the email.
        result = classify_ticket(email)

        # 2. Create a database record.
        db_ticket = Ticket(
            email=email,
            category=result["category"],
            urgency=result["urgency"],
            sentiment=result["sentiment"],
        )

        # 3. Save the record to PostgreSQL.
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)

        # 4. Return the saved ticket.
        return {
            "id": db_ticket.id,
            "email": db_ticket.email,
            "category": db_ticket.category,
            "urgency": db_ticket.urgency,
            "sentiment": db_ticket.sentiment,
            "review_status": db_ticket.review_status,
            "created_at": db_ticket.created_at,
        }

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to save the ticket to the database.",
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Ticket classification failed.",
        )
