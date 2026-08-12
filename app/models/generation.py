from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.clarification import Clarification
    from app.models.project import Project


class GenerationStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING_FOR_INPUT = "WAITING_FOR_INPUT"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Generation(Base):
    __tablename__ = "generations"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    workflow: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    status: Mapped[GenerationStatus] = mapped_column(
        SQLEnum(GenerationStatus),
        nullable=False,
        default=GenerationStatus.PENDING,
    )

    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    error: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    project: Mapped["Project"] = relationship(
        back_populates="generations",
    )

    clarifications: Mapped[list["Clarification"]] = relationship(
        back_populates="generation",
        cascade="all, delete-orphan",
    )