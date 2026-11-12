
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

import main
from database import get_db


client = TestClient(main.app)


# --------------------------------------------------
# Health endpoint tests
# --------------------------------------------------

def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# --------------------------------------------------
# Ticket classification endpoint tests
# --------------------------------------------------

def test_classify_ticket_saves_record(monkeypatch):
    fake_db = MagicMock()

    fake_db_ticket = MagicMock()
    fake_db_ticket.id = 123
    fake_db_ticket.email = "I was charged twice."
    fake_db_ticket.category = "billing"
    fake_db_ticket.urgency = "medium"
    fake_db_ticket.sentiment = "negative"
    fake_db_ticket.review_status = "pending"
    fake_db_ticket.status = "new"
    fake_db_ticket.created_at = datetime.now(timezone.utc)
    fake_db_ticket.updated_at = datetime.now(timezone.utc)
    fake_db_ticket.resolved_at = None

    def fake_add(ticket):
        fake_db_ticket.email = ticket.email
        fake_db_ticket.category = ticket.category
        fake_db_ticket.urgency = ticket.urgency
        fake_db_ticket.sentiment = ticket.sentiment

    def fake_refresh(ticket):
        ticket.id = 123
        ticket.review_status = "pending"
        ticket.status = "new"
        ticket.created_at = datetime.now(timezone.utc)
        ticket.updated_at = datetime.now(timezone.utc)
        ticket.resolved_at = None

    fake_db.add.side_effect = fake_add
    fake_db.refresh.side_effect = fake_refresh

    monkeypatch.setattr(
        main,
        "classify_ticket",
        lambda email: {
            "category": "billing",
            "urgency": "medium",
            "sentiment": "negative",
        },
    )

    def override_get_db():
        yield fake_db

    main.app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.post(
            "/tickets/classify",
            json={"email": "I was charged twice."},
        )
    finally:
        main.app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 201
    assert response.json()["id"] == 123
    assert response.json()["category"] == "billing"
    assert response.json()["review_status"] == "pending"
    assert response.json()["status"] == "new"

    fake_db.add.assert_called_once()
    fake_db.commit.assert_called_once()
    fake_db.refresh.assert_called_once()


def test_missing_email_returns_422():
    response = client.post("/tickets/classify", json={})

    assert response.status_code == 422


def test_empty_email_returns_422():
    response = client.post(
        "/tickets/classify",
        json={"email": ""},
    )

    assert response.status_code == 422


def test_whitespace_email_returns_422():
    response = client.post(
        "/tickets/classify",
        json={"email": "   "},
    )

    assert response.status_code == 422


# --------------------------------------------------
# List tickets endpoint tests
# --------------------------------------------------

def test_list_tickets_returns_paginated_results(monkeypatch):
    fake_db = MagicMock()

    fake_ticket = MagicMock()
    fake_ticket.id = 1
    fake_ticket.email = "I was charged twice."
    fake_ticket.category = "billing"
    fake_ticket.urgency = "medium"
    fake_ticket.sentiment = "negative"
    fake_ticket.review_status = "pending"
    fake_ticket.status = "new"
    fake_ticket.created_at = datetime.now(timezone.utc)
    fake_ticket.updated_at = datetime.now(timezone.utc)
    fake_ticket.resolved_at = None

    fake_db.scalar.return_value = 1
    fake_db.scalars.return_value.all.return_value = [fake_ticket]

    def override_get_db():
        yield fake_db

    main.app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.get("/tickets?limit=10&offset=0")
    finally:
        main.app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["limit"] == 10
    assert data["offset"] == 0
    assert len(data["tickets"]) == 1
    assert data["tickets"][0]["category"] == "billing"
    assert data["tickets"][0]["status"] == "new"


# --------------------------------------------------
# Ticket lifecycle test helpers
# --------------------------------------------------

def create_fake_ticket(status="new"):
    """Create a fake ticket with lifecycle fields."""

    now = datetime.now(timezone.utc)

    return SimpleNamespace(
        id=123,
        email="I was charged twice.",
        category="billing",
        urgency="medium",
        sentiment="negative",
        review_status="pending",
        status=status,
        created_at=now,
        updated_at=now,
        resolved_at=now if status == "resolved" else None,
    )


def make_status_request(ticket, new_status):
    """Send a status update request using a mocked database."""

    fake_db = MagicMock()
    fake_db.get.return_value = ticket

    def fake_refresh(refreshed_ticket):
        refreshed_ticket.updated_at = datetime.now(timezone.utc)

        # Simulate the database returning a resolution timestamp.
        if (
            refreshed_ticket.status == "resolved"
            and refreshed_ticket.resolved_at is not None
        ):
            refreshed_ticket.resolved_at = datetime.now(timezone.utc)

    fake_db.refresh.side_effect = fake_refresh

    def override_get_db():
        yield fake_db

    main.app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.patch(
            f"/tickets/{ticket.id}/status",
            json={"status": new_status},
        )
    finally:
        main.app.dependency_overrides.pop(get_db, None)

    return response, fake_db


# --------------------------------------------------
# Ticket lifecycle endpoint tests
# --------------------------------------------------

def test_new_ticket_can_be_opened():
    ticket = create_fake_ticket(status="new")

    response, fake_db = make_status_request(ticket, "open")

    assert response.status_code == 200
    assert response.json()["status"] == "open"

    fake_db.commit.assert_called_once()
    fake_db.refresh.assert_called_once()


def test_open_ticket_can_be_in_progress():
    ticket = create_fake_ticket(status="open")

    response, fake_db = make_status_request(ticket, "in_progress")

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"

    fake_db.commit.assert_called_once()


def test_ticket_can_be_resolved():
    ticket = create_fake_ticket(status="open")

    response, fake_db = make_status_request(ticket, "resolved")

    assert response.status_code == 200
    assert response.json()["status"] == "resolved"
    assert response.json()["resolved_at"] is not None

    fake_db.commit.assert_called_once()


def test_resolved_ticket_can_be_reopened():
    ticket = create_fake_ticket(status="resolved")

    response, fake_db = make_status_request(ticket, "open")

    assert response.status_code == 200
    assert response.json()["status"] == "open"
    assert response.json()["resolved_at"] is None

    fake_db.commit.assert_called_once()


def test_invalid_status_transition_returns_409():
    ticket = create_fake_ticket(status="new")

    response, fake_db = make_status_request(ticket, "resolved")

    assert response.status_code == 409

    fake_db.commit.assert_not_called()


def test_nonexistent_ticket_returns_404():
    fake_db = MagicMock()
    fake_db.get.return_value = None

    def override_get_db():
        yield fake_db

    main.app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.patch(
            "/tickets/999/status",
            json={"status": "open"},
        )
    finally:
        main.app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 404

    fake_db.commit.assert_not_called()


def test_invalid_status_value_returns_422():
    response = client.patch(
        "/tickets/123/status",
        json={"status": "pending"},
    )

    assert response.status_code == 422


def test_same_status_update_is_idempotent():
    ticket = create_fake_ticket(status="new")

    response, fake_db = make_status_request(ticket, "new")

    assert response.status_code == 200
    assert response.json()["status"] == "new"

    fake_db.commit.assert_not_called()
