import pytest
from unittest.mock import AsyncMock, Mock, patch

from app.services.generation.orchestrator import (
    GenerationOrchestrator,
)


@pytest.mark.anyio
async def test_run_generation():
    generation_service = Mock()

    graph = Mock()
    graph.ainvoke = AsyncMock(
        return_value={
            "project_id": 1,
            "generation_id": 1,
            "project_name": "AI Architect",
            "project_idea": (
                "An AI system for generating technical plans."
            ),
            "requirements": {
                "functional_requirements": [],
            },
            "prd": None,
            "architecture": None,
            "database_design": None,
            "api_design": None,
            "roadmap": None,
            "clarifications": [],
        },
    )

    with patch(
        "app.services.generation.orchestrator.build_generation_graph",
        return_value=graph,
    ):
        orchestrator = GenerationOrchestrator(
            generation_service=generation_service,
        )

        result = await orchestrator.run(
            generation_id=1,
            project_id=1,
            project_name="AI Architect",
            project_idea=(
                "An AI system for generating technical plans."
            ),
        )

    generation_service.start.assert_called_once_with(
        generation_id=1,
    )

    graph.ainvoke.assert_awaited_once_with(
        {
            "project_id": 1,
            "generation_id": 1,
            "project_name": "AI Architect",
            "project_idea": (
                "An AI system for generating technical plans."
            ),
            "requirements": None,
            "prd": None,
            "architecture": None,
            "database_design": None,
            "api_design": None,
            "roadmap": None,
            "clarifications": [],
        }
    )

    generation_service.complete.assert_called_once_with(
        generation_id=1,
    )

    generation_service.fail.assert_not_called()

    assert result["project_id"] == 1
    assert result["generation_id"] == 1


@pytest.mark.anyio
async def test_run_generation_marks_failed_on_error():
    generation_service = Mock()

    graph = Mock()
    graph.ainvoke = AsyncMock(
        side_effect=RuntimeError("Graph execution failed"),
    )

    with patch(
        "app.services.generation.orchestrator.build_generation_graph",
        return_value=graph,
    ):
        orchestrator = GenerationOrchestrator(
            generation_service=generation_service,
        )

        with pytest.raises(
            RuntimeError,
            match="Graph execution failed",
        ):
            await orchestrator.run(
                generation_id=1,
                project_id=1,
                project_name="AI Architect",
                project_idea=(
                    "An AI system for generating technical plans."
                ),
            )

    generation_service.start.assert_called_once_with(
        generation_id=1,
    )

    generation_service.complete.assert_not_called()

    generation_service.fail.assert_called_once_with(
        generation_id=1,
        error="Graph execution failed",
    )