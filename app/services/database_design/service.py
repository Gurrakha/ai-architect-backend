from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.database_design import DatabaseDesign
from app.models.prd import PRD
from app.models.project import Project
from app.models.requirement import Requirement
from app.schemas.database_design import DatabaseDesignContent
from app.services.ai.agents.database_design import DatabaseDesignAgent


class DatabaseDesignService:
    """Service for generating and persisting database designs."""

    def __init__(
        self,
        db: Session,
        agent: DatabaseDesignAgent,
    ) -> None:
        self.db = db
        self.agent = agent

    async def generate(
        self,
        project_id: int,
        requirements: dict | None = None,
        prd: dict | None = None,
        clarifications: list[dict] | None = None,
    ) -> DatabaseDesign:
        project = self.db.get(Project, project_id)

        if project is None:
            raise ValueError(f"Project {project_id} not found")

        if requirements is None:
            latest_requirement = self.db.scalar(
                select(Requirement)
                .where(Requirement.project_id == project_id)
                .order_by(Requirement.version.desc())
                .limit(1)
            )

            if latest_requirement is None:
                raise ValueError(
                    f"No requirements found for project {project_id}"
                )

            requirements = latest_requirement.content

        if prd is None:
            latest_prd = self.db.scalar(
                select(PRD)
                .where(PRD.project_id == project_id)
                .order_by(PRD.version.desc())
                .limit(1)
            )

            if latest_prd is None:
                raise ValueError(
                    f"No PRD found for project {project_id}"
                )

            prd = latest_prd.content

        if clarifications is None:
            clarifications = []

        content: DatabaseDesignContent = await self.agent.generate(
            project_name=project.name,
            project_idea=project.idea,
            requirements=requirements,
            prd=prd,
            clarifications=clarifications,
        )

        latest_version = self.db.scalar(
            select(DatabaseDesign.version)
            .where(DatabaseDesign.project_id == project_id)
            .order_by(DatabaseDesign.version.desc())
            .limit(1)
        )

        next_version = (latest_version or 0) + 1

        database_design = DatabaseDesign(
            project_id=project_id,
            version=next_version,
            content=content.model_dump(),
        )

        self.db.add(database_design)
        self.db.commit()
        self.db.refresh(database_design)

        return database_design