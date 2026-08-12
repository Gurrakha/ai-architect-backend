from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Component(Base):
    __tablename__ = "components"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    architecture_id: Mapped[int] = mapped_column(
        ForeignKey("architectures.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    technology: Mapped[str | None] = mapped_column(
        String(255),
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