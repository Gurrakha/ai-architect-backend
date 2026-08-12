from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Connection(Base):
    __tablename__ = "connections"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    architecture_id: Mapped[int] = mapped_column(
        ForeignKey("architectures.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    source_component_id: Mapped[int] = mapped_column(
        ForeignKey("components.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    target_component_id: Mapped[int] = mapped_column(
        ForeignKey("components.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    protocol: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )