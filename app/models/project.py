from datetime import datetime, UTC
from sqlalchemy import DateTime, Enum as SQLEnum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from enum import Enum
from app.core.utils import utc_now

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.api_design import APIDesign
    from app.models.architecture import Architecture
    from app.models.database_design import DatabaseDesign
    from app.models.generation import Generation
    from app.models.prd import PRD
    from app.models.requirement import Requirement
    from app.models.roadmap import Roadmap



class ProjectStatus(str, Enum):
    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    idea: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[ProjectStatus] = mapped_column(
        SQLEnum(ProjectStatus),
        nullable=False,
        default="DRAFT",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=utc_now,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=utc_now,
        onupdate=utc_now
    )

    requirements: Mapped[list["Requirement"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )

    prds: Mapped[list["PRD"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )

    architectures: Mapped[list["Architecture"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )

    database_designs: Mapped[list["DatabaseDesign"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )

    api_designs: Mapped[list["APIDesign"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )

    roadmaps: Mapped[list["Roadmap"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )

    generations: Mapped[list["Generation"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )