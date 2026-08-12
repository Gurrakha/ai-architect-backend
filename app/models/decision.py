from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ArchitectureDecision(Base):
    __tablename__ = "architecture_decisions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    architecture_id: Mapped[int] = mapped_column(
        ForeignKey("architectures.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    decision: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    rationale: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    alternatives: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    tradeoffs: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )