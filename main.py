
from typing import Literal

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
    description=(
        "API for classifying, storing, and managing "
        "customer support tickets."
    ),
    version="1.2.0",
)


# --------------------------------------------------
# REQUEST MODELS
# --------------------------------------------------

class TicketRequest(BaseModel):
    email: str = Field(
        ...,
        min_length=1,
        description="The customer's email text",
        examples=["I was charged twice for my subscription."],
    )


class TicketStatusUpdate(BaseModel):
    status: Literal[
        "new",
        "open",
        "in_progress",
        "waiting_customer",
        "resolved",
        "closed",
    ]


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "Ticket triage API is running",
    }


# --------------------------------------------------
# LIST TICKETS
# --------------------------------------------------

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
        .order_by(
            Ticket.created_at.desc(),
            Ticket.id.desc(),
        )
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
                "status": ticket.status,
                "created_at": ticket.created_at,
                "updated_at": ticket.updated_at,
                "resolved_at": ticket.resolved_at,
            }
            for ticket in tickets
        ],
    }


# --------------------------------------------------
# CLASSIFY AND CREATE TICKET
# --------------------------------------------------

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
        # 1. Classify the customer email.
        result = classify_ticket(email)

        # 2. Create a database record.
        # PostgreSQL supplies the default lifecycle fields.
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
            "status": db_ticket.status,
            "created_at": db_ticket.created_at,
            "updated_at": db_ticket.updated_at,
            "resolved_at": db_ticket.resolved_at,
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


# --------------------------------------------------
# TICKET LIFECYCLE MANAGEMENT
# --------------------------------------------------

@app.patch("/tickets/{ticket_id}/status")
def update_ticket_status(
    ticket_id: int,
    update: TicketStatusUpdate,
    db: Session = Depends(get_db),
):
    # 1. Find the requested ticket.
    ticket = db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found.",
        )

    # 2. Define allowed status transitions.
    allowed_transitions = {
        "new": ["open"],
        "open": [
            "in_progress",
            "waiting_customer",
            "resolved",
        ],
        "in_progress": [
            "waiting_customer",
            "resolved",
        ],
        "waiting_customer": [
            "open",
            "in_progress",
            "resolved",
        ],
        "resolved": [
            "open",
            "closed",
        ],
        "closed": [],
    }

    current_status = ticket.status
    new_status = update.status

    # 3. Allow repeated requests without modifying the ticket.
    if current_status == new_status:
        pass

    # 4. Validate the requested transition.
    elif new_status not in allowed_transitions[current_status]:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Cannot transition ticket from "
                f"'{current_status}' to '{new_status}'."
            ),
        )

    else:
        try:
            # 5. Update the ticket status.
            ticket.status = new_status

            # Record the time when the ticket is resolved.
            if new_status == "resolved":
                ticket.resolved_at = func.current_timestamp()

            # Clear resolution time when reopening.
            elif (
                current_status == "resolved"
                and new_status == "open"
            ):
                ticket.resolved_at = None

            # 6. Save the changes.
            db.commit()
            db.refresh(ticket)

        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Failed to update ticket status.",
            )

    # 7. Return the ticket information.
    return {
        "id": ticket.id,
        "email": ticket.email,
        "category": ticket.category,
        "urgency": ticket.urgency,
        "sentiment": ticket.sentiment,
        "review_status": ticket.review_status,
        "status": ticket.status,
        "created_at": ticket.created_at,
        "updated_at": ticket.updated_at,
        "resolved_at": ticket.resolved_at,
    }
