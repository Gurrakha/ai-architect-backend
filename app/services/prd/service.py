from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.prd import PRD
from app.models.project import Project
from app.models.requirement import Requirement
from app.schemas.prd import PRDContent
from app.services.ai.agents.prd import PRDAgent


class PRDService:
    """Service for generating and persisting project PRDs."""

    def __init__(
        self,
        db: Session,
        agent: PRDAgent,
    ) -> None:
        self.db = db
        self.agent = agent

    async def generate(
        self,
        project_id: int,
    ) -> PRD:
        project = self.db.get(Project, project_id)

        if project is None:
            raise ValueError(f"Project {project_id} not found")

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

        content: PRDContent = await self.agent.generate(
            project_name=project.name,
            project_idea=project.idea,
            requirements=latest_requirement.content,
        )

        latest_version = self.db.scalar(
            select(PRD.version)
            .where(PRD.project_id == project_id)
            .order_by(PRD.version.desc())
            .limit(1)
        )

        next_version = (latest_version or 0) + 1

        prd = PRD(
            project_id=project_id,
            version=next_version,
            content=content.model_dump(),
        )

        self.db.add(prd)
        self.db.commit()
        self.db.refresh(prd)

        return prd