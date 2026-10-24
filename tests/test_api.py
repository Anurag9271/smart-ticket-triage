
from datetime import datetime, timezone
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

import main
from database import get_db


client = TestClient(main.app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_classify_ticket_saves_record(monkeypatch):
    fake_db = MagicMock()
    fake_db_ticket = MagicMock()
    fake_db_ticket.id = 123
    fake_db_ticket.email = "I was charged twice."
    fake_db_ticket.category = "billing"
    fake_db_ticket.urgency = "medium"
    fake_db_ticket.sentiment = "negative"
    fake_db_ticket.review_status = "pending"
    fake_db_ticket.created_at = datetime.now(timezone.utc)

    def fake_add(ticket):
        fake_db_ticket.email = ticket.email
        fake_db_ticket.category = ticket.category
        fake_db_ticket.urgency = ticket.urgency
        fake_db_ticket.sentiment = ticket.sentiment

    def fake_refresh(ticket):
        ticket.id = 123
        ticket.review_status = "pending"
        ticket.created_at = datetime.now(timezone.utc)

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

def test_list_tickets_returns_paginated_results(monkeypatch):
    from datetime import datetime, timezone
    from unittest.mock import MagicMock

    fake_db = MagicMock()
    fake_ticket = MagicMock()
    fake_ticket.id = 1
    fake_ticket.email = "I was charged twice."
    fake_ticket.category = "billing"
    fake_ticket.urgency = "medium"
    fake_ticket.sentiment = "negative"
    fake_ticket.review_status = "pending"
    fake_ticket.created_at = datetime.now(timezone.utc)

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
