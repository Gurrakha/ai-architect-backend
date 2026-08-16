from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.api_design import APIDesign
from app.models.architecture import Architecture
from app.models.database_design import DatabaseDesign
from app.models.prd import PRD
from app.models.project import Project
from app.models.requirement import Requirement
from app.models.roadmap import Roadmap
from app.schemas.roadmap import RoadmapContent
from app.services.ai.agents.roadmap import RoadmapAgent


class RoadmapService:
    """Service for generating and persisting project roadmaps."""

    def __init__(
        self,
        db: Session,
        agent: RoadmapAgent,
    ) -> None:
        self.db = db
        self.agent = agent

    async def generate(
        self,
        project_id: int,
        requirements: dict | None = None,
        prd: dict | None = None,
        architecture: dict | None = None,
        database_design: dict | None = None,
        api_design: dict | None = None,
    ) -> Roadmap:
        project = self.db.get(Project, project_id)

        if project is None:
            raise ValueError(
                f"Project {project_id} not found"
            )

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
                        "source_component": (
                            connection.source_component.name
                        ),
                        "target_component": (
                            connection.target_component.name
                        ),
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
                .where(
                    DatabaseDesign.project_id == project_id
                )
                .order_by(DatabaseDesign.version.desc())
                .limit(1)
            )

            if latest_database_design is None:
                raise ValueError(
                    f"No database design found for project {project_id}"
                )

            database_design = latest_database_design.content

        if api_design is None:
            latest_api_design = self.db.scalar(
                select(APIDesign)
                .where(APIDesign.project_id == project_id)
                .order_by(APIDesign.version.desc())
                .limit(1)
            )

            if latest_api_design is None:
                raise ValueError(
                    f"No API design found for project {project_id}"
                )

            api_design = latest_api_design.content

        generated: RoadmapContent = await self.agent.generate(
            project_name=project.name,
            project_idea=project.idea,
            requirements=requirements,
            prd=prd,
            architecture=architecture,
            database_design=database_design,
            api_design=api_design,
        )

        latest_version = self.db.scalar(
            select(Roadmap.version)
            .where(Roadmap.project_id == project_id)
            .order_by(Roadmap.version.desc())
            .limit(1)
        )

        next_version = (latest_version or 0) + 1

        roadmap = Roadmap(
            project_id=project_id,
            version=next_version,
            content=generated.model_dump(),
        )

        self.db.add(roadmap)
        self.db.commit()
        self.db.refresh(roadmap)

        return roadmap