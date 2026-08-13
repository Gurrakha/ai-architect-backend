from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.requirement import Requirement
from app.schemas.requirement import RequirementContent
from app.services.ai.agents.requirements import RequirementsAgent


class RequirementsService:
    """Service for generating and persisting project requirements."""

    def __init__(
        self,
        db: Session,
        agent: RequirementsAgent,
    ) -> None:
        self.db = db
        self.agent = agent

    async def generate(
        self,
        project_id: int,
    ) -> Requirement:
        project = self.db.get(Project, project_id)

        if project is None:
            raise ValueError(f"Project {project_id} not found")

        content: RequirementContent = await self.agent.generate(
            project_name=project.name,
            project_idea=project.idea,
        )

        latest_version = self.db.scalar(
            select(Requirement.version)
            .where(Requirement.project_id == project_id)
            .order_by(Requirement.version.desc())
            .limit(1)
        )

        next_version = (latest_version or 0) + 1

        requirement = Requirement(
            project_id=project_id,
            version=next_version,
            content=content.model_dump(),
        )

        self.db.add(requirement)
        self.db.commit()
        self.db.refresh(requirement)

        return requirement