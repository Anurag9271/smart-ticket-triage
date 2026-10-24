
from sqlalchemy import inspect

from database import engine
from models import Ticket


def test_tickets_table_matches_model():
    inspector = inspect(engine)

    assert inspector.has_table("tickets")

    columns = {
        column["name"]
        for column in inspector.get_columns("tickets")
    }

    assert columns == {
        "id",
        "email",
        "category",
        "urgency",
        "sentiment",
        "review_status",
        "created_at",
    }

    assert Ticket.__tablename__ == "tickets"
