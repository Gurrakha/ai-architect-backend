import pytest
from unittest.mock import AsyncMock, Mock, patch

from langgraph.checkpoint.memory import MemorySaver

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
            checkpointer=MemorySaver(),
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
        },
        config={
            "configurable": {
                "thread_id": "1",
            }
        },
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
            checkpointer=MemorySaver(),
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


@pytest.mark.anyio
async def test_run_generation_waits_for_clarification():
    generation_service = Mock()

    graph = Mock()
    graph.ainvoke = AsyncMock(
        return_value={
            "__interrupt__": [
                Mock(
                    value={
                        "type": "clarification_required",
                        "clarifications": [
                            {
                                "id": 1,
                                "question": "Who can create projects?",
                                "reason": (
                                    "Authorization requirements are needed."
                                ),
                                "answer": None,
                            },
                        ],
                    }
                )
            ]
        },
    )

    with patch(
        "app.services.generation.orchestrator.build_generation_graph",
        return_value=graph,
    ):
        orchestrator = GenerationOrchestrator(
            generation_service=generation_service,
            checkpointer=MemorySaver(),
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

    generation_service.wait_for_input.assert_called_once_with(
        generation_id=1,
    )

    generation_service.complete.assert_not_called()
    generation_service.fail.assert_not_called()

    assert "__interrupt__" in result


@pytest.mark.anyio
async def test_resume_generation():
    generation_service = Mock()

    graph = Mock()
    graph.ainvoke = AsyncMock(
        return_value={
            "project_id": 1,
            "generation_id": 1,
            "clarifications": [
                {
                    "id": 1,
                    "question": "Who can create projects?",
                    "reason": (
                        "Authorization requirements are needed."
                    ),
                    "answer": "Only authenticated users.",
                },
            ],
            "architecture": {
                "overview": "Test architecture",
            },
        },
    )

    with patch(
        "app.services.generation.orchestrator.build_generation_graph",
        return_value=graph,
    ):
        orchestrator = GenerationOrchestrator(
            generation_service=generation_service,
            checkpointer=MemorySaver(),
        )

        result = await orchestrator.resume(
            generation_id=1,
            answers=[
                {
                    "id": 1,
                    "answer": "Only authenticated users.",
                },
            ],
        )

    graph.ainvoke.assert_awaited_once()

    call_args = graph.ainvoke.call_args

    assert call_args.args[0].resume == [
        {
            "id": 1,
            "answer": "Only authenticated users.",
        },
    ]

    assert call_args.kwargs["config"] == {
        "configurable": {
            "thread_id": "1",
        }
    }

    generation_service.complete.assert_called_once_with(
        generation_id=1,
    )

    generation_service.wait_for_input.assert_not_called()
    generation_service.fail.assert_not_called()

    assert result["generation_id"] == 1


@pytest.mark.anyio
async def test_resume_generation_marks_failed_on_error():
    generation_service = Mock()

    graph = Mock()
    graph.ainvoke = AsyncMock(
        side_effect=RuntimeError("Resume failed"),
    )

    with patch(
        "app.services.generation.orchestrator.build_generation_graph",
        return_value=graph,
    ):
        orchestrator = GenerationOrchestrator(
            generation_service=generation_service,
            checkpointer=MemorySaver(),
        )

        with pytest.raises(
            RuntimeError,
            match="Resume failed",
        ):
            await orchestrator.resume(
                generation_id=1,
                answers=[
                    {
                        "id": 1,
                        "answer": "Only authenticated users.",
                    },
                ],
            )

    generation_service.complete.assert_not_called()

    generation_service.wait_for_input.assert_not_called()

    generation_service.fail.assert_called_once_with(
        generation_id=1,
        error="Resume failed",
    )