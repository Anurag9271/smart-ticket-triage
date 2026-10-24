
from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_classify_ticket_success(monkeypatch):
    def fake_classify_ticket(email):
        return {
            "category": "billing",
            "urgency": "medium",
            "sentiment": "negative",
        }

    monkeypatch.setattr(
        main,
        "classify_ticket",
        fake_classify_ticket,
    )

    response = client.post(
        "/tickets/classify",
        json={
            "email": "I was charged twice for my subscription."
        },
    )

    assert response.status_code == 200
    assert response.json()["category"] == "billing"
    assert response.json()["urgency"] == "medium"
    assert response.json()["sentiment"] == "negative"


def test_missing_email_returns_422():
    response = client.post(
        "/tickets/classify",
        json={},
    )

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
