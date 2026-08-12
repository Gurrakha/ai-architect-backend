from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.component import Component
    from app.models.connection import Connection
    from app.models.decision import ArchitectureDecision


class Architecture(Base):
    __tablename__ = "architectures"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    overview: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    project: Mapped["Project"] = relationship(
        back_populates="architectures",
    )

    components: Mapped[list["Component"]] = relationship(
        back_populates="architecture",
        cascade="all, delete-orphan",
    )

    connections: Mapped[list["Connection"]] = relationship(
        back_populates="architecture",
        cascade="all, delete-orphan",
    )

    decisions: Mapped[list["ArchitectureDecision"]] = relationship(
        back_populates="architecture",
        cascade="all, delete-orphan",
    )