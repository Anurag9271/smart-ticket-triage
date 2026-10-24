
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Identity,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Ticket(Base):
    __tablename__ = "tickets"

    __table_args__ = (
        CheckConstraint(
            "category IN ('billing', 'technical', 'account', 'other')"
        ),
        CheckConstraint(
            "urgency IN ('high', 'medium', 'low')"
        ),
        CheckConstraint(
            "sentiment IN ('positive', 'neutral', 'negative')"
        ),
        CheckConstraint(
            "review_status IN ('pending', 'approved', 'rejected')"
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )
    email: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    urgency: Mapped[str] = mapped_column(String(10), nullable=False)
    sentiment: Mapped[str] = mapped_column(String(10), nullable=False)
    review_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="pending",
    )
    created_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )
