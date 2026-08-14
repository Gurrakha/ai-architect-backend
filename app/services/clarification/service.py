from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.utils import utc_now
from app.models.clarification import Clarification
from app.models.generation import Generation
from app.models.prd import PRD
from app.models.project import Project
from app.models.requirement import Requirement
from app.services.ai.agents.clarification import ClarificationAgent


class ClarificationService:
    """Service for generating and answering project clarifications."""

    def __init__(
        self,
        db: Session,
        agent: ClarificationAgent,
    ) -> None:
        self.db = db
        self.agent = agent

    async def generate(
        self,
        project_id: int,
        generation_id: int,
    ) -> list[Clarification]:
        project = self.db.get(Project, project_id)

        if project is None:
            raise ValueError(
                f"Project {project_id} not found"
            )

        generation = self.db.get(
            Generation,
            generation_id,
        )

        if generation is None or generation.project_id != project_id:
            raise ValueError(
                f"Generation {generation_id} not found"
            )

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

        generated = await self.agent.generate(
            project_name=project.name,
            project_idea=project.idea,
            requirements=latest_requirement.content,
            prd=latest_prd.content,
        )

        if not generated.needs_clarification:
            return []

        clarifications: list[Clarification] = []

        for question in generated.questions:
            clarification = Clarification(
                project_id=project_id,
                generation_id=generation_id,
                question=question.question,
                reason=question.reason,
            )

            self.db.add(clarification)
            clarifications.append(clarification)

        self.db.commit()

        for clarification in clarifications:
            self.db.refresh(clarification)

        return clarifications

    def answer(
        self,
        project_id: int,
        clarification_id: int,
        answer: str,
    ) -> Clarification:
        clarification = self.db.get(
            Clarification,
            clarification_id,
        )

        if (
            clarification is None
            or clarification.project_id != project_id
        ):
            raise ValueError(
                f"Clarification {clarification_id} not found"
            )

        clarification.answer = answer
        clarification.answered_at = utc_now()

        self.db.commit()
        self.db.refresh(clarification)

        return clarification