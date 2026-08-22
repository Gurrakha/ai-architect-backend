from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.api_design import APIDesign
from app.models.architecture import Architecture
from app.models.database_design import DatabaseDesign
from app.models.project import Project
from app.models.requirement import Requirement
from app.schemas.api_design import APIDesignContent
from app.services.ai.agents.api_design import APIDesignAgent


class APIDesignService:
    """Service for generating and persisting project API designs."""

    def __init__(
        self,
        db: Session,
        agent: APIDesignAgent,
    ) -> None:
        self.db = db
        self.agent = agent

    async def generate(
        self,
        project_id: int,
        requirements: dict | None = None,
        architecture: dict | None = None,
        database_design: dict | None = None,
        clarifications: list[dict] | None = None,
    ) -> APIDesign:
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

        if architecture is None:
            latest_architecture = self.db.scalar(
                select(Architecture)
                .where(Architecture.project_id == project_id)
                .order_by(Architecture.version.desc())
                .limit(1)
            )

            if latest_architecture is None:
                raise ValueError(
                    f"No architecture found for project {project_id}"
                )

            architecture = {
                "overview": latest_architecture.overview,
                "components": [
                    {
                        "name": component.name,
                        "type": component.type,
                        "technology": component.technology,
                        "description": component.description,
                    }
                    for component in latest_architecture.components
                ],
                "connections": [
                    {
                        "source_component": connection.source_component.name,
                        "target_component": connection.target_component.name,
                        "protocol": connection.protocol,
                        "description": connection.description,
                    }
                    for connection in latest_architecture.connections
                ],
                "decisions": [
                    {
                        "decision": decision.decision,
                        "rationale": decision.rationale,
                        "alternatives": decision.alternatives,
                        "tradeoffs": decision.tradeoffs,
                    }
                    for decision in latest_architecture.decisions
                ],
            }

        if database_design is None:
            latest_database_design = self.db.scalar(
                select(DatabaseDesign)
                .where(DatabaseDesign.project_id == project_id)
                .order_by(DatabaseDesign.version.desc())
                .limit(1)
            )

            if latest_database_design is None:
                raise ValueError(
                    f"No database design found for project {project_id}"
                )

            database_design = latest_database_design.content

        if clarifications is None:
            clarifications = []

        content: APIDesignContent = await self.agent.generate(
            project_name=project.name,
            project_idea=project.idea,
            requirements=requirements,
            architecture=architecture,
            database_design=database_design,
            clarifications=clarifications,
        )

        latest_version = self.db.scalar(
            select(APIDesign.version)
            .where(APIDesign.project_id == project_id)
            .order_by(APIDesign.version.desc())
            .limit(1)
        )

        next_version = (latest_version or 0) + 1

        api_design = APIDesign(
            project_id=project_id,
            version=next_version,
            content=content.model_dump(),
        )

        self.db.add(api_design)
        self.db.commit()
        self.db.refresh(api_design)

        return api_design

    def get_latest(self, project_id: int) -> APIDesign | None:
        return self.db.scalar(
            select(APIDesign)
            .where(APIDesign.project_id == project_id)
            .order_by(APIDesign.version.desc())
            .limit(1)
        )