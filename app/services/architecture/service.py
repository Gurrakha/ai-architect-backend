from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.architecture import Architecture
from app.models.component import Component
from app.models.connection import Connection
from app.models.decision import ArchitectureDecision
from app.models.prd import PRD
from app.models.project import Project
from app.models.requirement import Requirement
from app.services.ai.schemas.architecture import ArchitectureGeneration
from app.services.ai.agents.architecture import ArchitectureAgent


class ArchitectureService:
    """Service for generating and persisting project architectures."""

    def __init__(
        self,
        db: Session,
        agent: ArchitectureAgent,
    ) -> None:
        self.db = db
        self.agent = agent

    async def generate(
        self,
        project_id: int,
        requirements: dict | None = None,
        prd: dict | None = None,
        clarifications: list[dict] | None = None,
    ) -> Architecture:
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

        generated: ArchitectureGeneration = await self.agent.generate(
            project_name=project.name,
            project_idea=project.idea,
            requirements=requirements,
            prd=prd,
            clarifications=clarifications
        )

        latest_version = self.db.scalar(
            select(Architecture.version)
            .where(Architecture.project_id == project_id)
            .order_by(Architecture.version.desc())
            .limit(1)
        )

        next_version = (latest_version or 0) + 1

        architecture = Architecture(
            project_id=project_id,
            version=next_version,
            overview=generated.overview,
        )

        self.db.add(architecture)
        self.db.flush()

        components_by_name: dict[str, Component] = {}

        for component_data in generated.components:
            component = Component(
                architecture_id=architecture.id,
                name=component_data.name,
                type=component_data.type,
                technology=component_data.technology,
                description=component_data.description,
            )

            self.db.add(component)
            self.db.flush()

            components_by_name[component.name] = component

        for connection_data in generated.connections:
            source = components_by_name.get(
                connection_data.source_component
            )
            target = components_by_name.get(
                connection_data.target_component
            )

            if source is None or target is None:
                raise ValueError(
                    "Architecture connection references "
                    "an unknown component"
                )

            connection = Connection(
                architecture_id=architecture.id,
                source_component_id=source.id,
                target_component_id=target.id,
                protocol=connection_data.protocol,
                description=connection_data.description,
            )

            self.db.add(connection)

        for decision_data in generated.decisions:
            decision = ArchitectureDecision(
                architecture_id=architecture.id,
                decision=decision_data.decision,
                rationale=decision_data.rationale,
                alternatives=decision_data.alternatives,
                tradeoffs=decision_data.tradeoffs,
            )

            self.db.add(decision)

        self.db.commit()
        self.db.refresh(architecture)

        return architecture

    def get_latest(self, project_id: int) -> Architecture | None:
        return self.db.scalar(
            select(Architecture)
            .where(Architecture.project_id == project_id)
            .order_by(Architecture.version.desc())
            .limit(1)
        )