from langgraph.types import Command

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
        checkpointer,
    ) -> None:
        self.generation_service = generation_service
        self.checkpointer = checkpointer

    async def run(
        self,
        generation_id: int,
        project_id: int,
        project_name: str,
        project_idea: str,
    ) -> dict:
        self.generation_service.start(
            generation_id=generation_id,
        )

        graph = build_generation_graph(
            checkpointer=self.checkpointer,
        )

        initial_state = {
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

        config = {
            "configurable": {
                "thread_id": str(generation_id),
            }
        }

        try:
            result = await graph.ainvoke(
                initial_state,
                config=config,
            )

            if result.get("__interrupt__"):
                self.generation_service.wait_for_input(
                    generation_id=generation_id,
                )

                return result

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

    async def resume(
        self,
        generation_id: int,
        answers: list[dict],
    ) -> dict:
        graph = build_generation_graph(
            checkpointer=self.checkpointer,
        )

        config = {
            "configurable": {
                "thread_id": str(generation_id),
            }
        }

        try:
            result = await graph.ainvoke(
                Command(resume=answers),
                config=config,
            )

            if result.get("__interrupt__"):
                self.generation_service.wait_for_input(
                    generation_id=generation_id,
                )

                return result

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