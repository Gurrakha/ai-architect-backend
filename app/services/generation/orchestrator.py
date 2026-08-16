from app.services.generation.graph import (
    GenerationState,
    build_generation_graph,
)
from app.services.generation.service import GenerationService


class GenerationOrchestrator:
    """Coordinates generation lifecycle and workflow execution."""

    def __init__(
        self,
        generation_service: GenerationService,
    ) -> None:
        self.generation_service = generation_service
        self.graph = build_generation_graph()

    async def run(
        self,
        generation_id: int,
        project_id: int,
        project_name: str,
        project_idea: str,
    ) -> GenerationState:
        self.generation_service.start(
            generation_id=generation_id,
        )

        initial_state: GenerationState = {
            "project_id": project_id,
            "generation_id": generation_id,
            "project_name": project_name,
            "project_idea": project_idea,
            "requirements": None,
            "prd": None,
            "architecture": None,
            "database_design": None,
            "api_design": None,
            "roadmap": None,
            "clarifications": [],
        }

        try:
            result = await self.graph.ainvoke(
                initial_state,
            )

            self.generation_service.complete(
                generation_id=generation_id,
            )

            return result

        except Exception as exc:
            self.generation_service.fail(
                generation_id=generation_id,
                error=str(exc),
            )

            raise