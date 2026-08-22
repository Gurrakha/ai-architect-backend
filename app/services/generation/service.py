from sqlalchemy import select

from app.core.utils import utc_now
from app.models.generation import Generation, GenerationStatus
from sqlalchemy.orm import Session


class GenerationService:
    """Service for managing generation lifecycle."""

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def create(
        self,
        project_id: int,
        workflow: str,
        model: str,
    ) -> Generation:
        generation = Generation(
            project_id=project_id,
            workflow=workflow,
            model=model,
            status=GenerationStatus.PENDING,
        )

        self.db.add(generation)
        self.db.commit()
        self.db.refresh(generation)

        return generation

    def start(
        self,
        generation_id: int,
    ) -> Generation:
        generation = self._get_generation(generation_id)

        generation.status = GenerationStatus.RUNNING
        generation.started_at = utc_now()

        self.db.commit()
        self.db.refresh(generation)

        return generation

    def wait_for_input(
        self,
        generation_id: int,
    ) -> Generation:
        generation = self._get_generation(generation_id)

        generation.status = GenerationStatus.WAITING_FOR_INPUT

        self.db.commit()
        self.db.refresh(generation)

        return generation

    def complete(
        self,
        generation_id: int,
    ) -> Generation:
        generation = self._get_generation(generation_id)

        generation.status = GenerationStatus.COMPLETED
        generation.completed_at = utc_now()

        self.db.commit()
        self.db.refresh(generation)

        return generation

    def fail(
        self,
        generation_id: int,
        error: str,
    ) -> Generation:
        generation = self._get_generation(generation_id)

        generation.status = GenerationStatus.FAILED
        generation.error = error

        self.db.commit()
        self.db.refresh(generation)

        return generation

    def _get_generation(
        self,
        generation_id: int,
    ) -> Generation:
        generation = self.db.get(
            Generation,
            generation_id,
        )

        if generation is None:
            raise ValueError(
                f"Generation {generation_id} not found"
            )

        return generation

    def get_by_id(
        self,
        project_id: int,
        generation_id: int,
    ) -> Generation | None:
        return self.db.scalar(
            select(Generation)
            .where(
                Generation.id == generation_id,
                Generation.project_id == project_id,
            )
        )

    def get_for_project(
        self,
        project_id: int,
    ) -> list[Generation]:
        return list(
            self.db.scalars(
                select(Generation)
                .where(Generation.project_id == project_id)
                .order_by(Generation.id.desc())
            ).all()
        )