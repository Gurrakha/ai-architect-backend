import pytest
from unittest.mock import AsyncMock, Mock, patch

from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from app.services.generation.graph import (
    GenerationState,
    build_generation_graph,
)


def create_initial_state() -> GenerationState:
    return {
        "project_id": 1,
        "generation_id": 1,
        "project_name": "AI Architect",
        "project_idea": "An AI system for generating technical plans.",
        "requirements": None,
        "prd": None,
        "architecture": None,
        "database_design": None,
        "api_design": None,
        "roadmap": None,
        "clarifications": [],
    }


def create_checkpointer():
    return MemorySaver()


def test_generation_graph_compiles():
    graph = build_generation_graph(
        checkpointer=create_checkpointer(),
    )

    assert graph is not None


def test_generation_state_shape():
    state = create_initial_state()

    assert state["project_id"] == 1
    assert state["requirements"] is None
    assert state["prd"] is None
    assert state["architecture"] is None
    assert state["database_design"] is None
    assert state["api_design"] is None
    assert state["clarifications"] == []


@pytest.mark.anyio
async def test_graph_nodes_update_state():
    generated_requirement = Mock()
    generated_requirement.content = {
        "functional_requirements": [
            {
                "title": "User authentication",
                "description": "Users can sign up and log in.",
            }
        ]
    }

    requirements_service = Mock()
    requirements_service.generate = AsyncMock(
        return_value=generated_requirement,
    )

    generated_prd = Mock()
    generated_prd.content = {
        "title": "AI Architect PRD",
        "problem_statement": "Generate technical plans using AI.",
    }

    prd_service = Mock()
    prd_service.generate = AsyncMock(
        return_value=generated_prd,
    )

    clarification_service = Mock()
    clarification_service.generate = AsyncMock(
        return_value=[],
    )

    generated_architecture = Mock()
    generated_architecture.overview = (
        "A scalable web architecture for AI-powered planning."
    )

    generated_component = Mock()
    generated_component.name = "API"
    generated_component.type = "backend"
    generated_component.technology = "FastAPI"
    generated_component.description = "Backend API service."

    generated_connection = Mock()
    generated_connection.source_component.name = "Frontend"
    generated_connection.target_component.name = "API"
    generated_connection.protocol = "HTTPS"
    generated_connection.description = (
        "Frontend communicates with the API."
    )

    generated_decision = Mock()
    generated_decision.decision = "Use PostgreSQL"
    generated_decision.rationale = "Reliable relational storage."
    generated_decision.alternatives = ["MongoDB"]
    generated_decision.tradeoffs = (
        "Requires relational schema design."
    )

    generated_architecture.components = [
        generated_component
    ]
    generated_architecture.connections = [
        generated_connection
    ]
    generated_architecture.decisions = [
        generated_decision
    ]

    architecture_service = Mock()
    architecture_service.generate = AsyncMock(
        return_value=generated_architecture,
    )

    generated_database_design = Mock()
    generated_database_design.content = {
        "tables": [
            {
                "name": "users",
                "columns": [
                    {
                        "name": "id",
                        "type": "integer",
                        "primary_key": True,
                    },
                    {
                        "name": "email",
                        "type": "string",
                        "primary_key": False,
                    },
                ],
            }
        ]
    }

    database_design_service = Mock()
    database_design_service.generate = AsyncMock(
        return_value=generated_database_design,
    )

    generated_api_design = Mock()
    generated_api_design.content = {
        "endpoints": [
            {
                "method": "POST",
                "path": "/users",
                "description": "Create a new user.",
            },
            {
                "method": "GET",
                "path": "/users/{id}",
                "description": "Get a user by ID.",
            },
        ]
    }

    api_design_service = Mock()
    api_design_service.generate = AsyncMock(
        return_value=generated_api_design,
    )

    generated_roadmap = Mock()
    generated_roadmap.content = {
        "phases": [
            {
                "name": "MVP",
                "description": "Build the initial product.",
            },
            {
                "name": "Production",
                "description": "Prepare the system for production.",
            },
        ]
    }

    roadmap_service = Mock()
    roadmap_service.generate = AsyncMock(
        return_value=generated_roadmap,
    )

    with (
        patch(
            "app.services.generation.graph.RequirementsService",
            return_value=requirements_service,
        ),
        patch(
            "app.services.generation.graph.PRDService",
            return_value=prd_service,
        ),
        patch(
            "app.services.generation.graph.ClarificationService",
            return_value=clarification_service,
        ),
        patch(
            "app.services.generation.graph.ArchitectureService",
            return_value=architecture_service,
        ),
        patch(
            "app.services.generation.graph.DatabaseDesignService",
            return_value=database_design_service,
        ),
        patch(
            "app.services.generation.graph.APIDesignService",
            return_value=api_design_service,
        ),
        patch(
            "app.services.generation.graph.RoadmapService",
            return_value=roadmap_service,
        ),
    ):
        graph = build_generation_graph(
            checkpointer=create_checkpointer(),
        )

        result = await graph.ainvoke(
            create_initial_state(),
            config={
                "configurable": {
                    "thread_id": "test-full-generation",
                }
            },
        )

    assert result["requirements"] == generated_requirement.content

    assert result["prd"] == generated_prd.content

    assert result["architecture"] == {
        "overview": generated_architecture.overview,
        "components": [
            {
                "name": "API",
                "type": "backend",
                "technology": "FastAPI",
                "description": "Backend API service.",
            }
        ],
        "connections": [
            {
                "source_component": "Frontend",
                "target_component": "API",
                "protocol": "HTTPS",
                "description": (
                    "Frontend communicates with the API."
                ),
            }
        ],
        "decisions": [
            {
                "decision": "Use PostgreSQL",
                "rationale": "Reliable relational storage.",
                "alternatives": ["MongoDB"],
                "tradeoffs": (
                    "Requires relational schema design."
                ),
            }
        ],
    }

    assert result["database_design"] == (
        generated_database_design.content
    )

    assert result["api_design"] == (
        generated_api_design.content
    )

    assert result["roadmap"] == generated_roadmap.content

    assert result["clarifications"] == []

    requirements_service.generate.assert_awaited_once_with(
        project_id=1,
    )

    prd_service.generate.assert_awaited_once_with(
        project_id=1,
        requirements=generated_requirement.content,
    )

    clarification_service.generate.assert_awaited_once_with(
        project_id=1,
        generation_id=1,
        requirements=generated_requirement.content,
        prd=generated_prd.content,
    )

    architecture_service.generate.assert_awaited_once_with(
        project_id=1,
        requirements=generated_requirement.content,
        prd=generated_prd.content,
    )

    database_design_service.generate.assert_awaited_once_with(
        project_id=1,
        requirements=generated_requirement.content,
        prd=generated_prd.content,
    )

    api_design_service.generate.assert_awaited_once_with(
        project_id=1,
        requirements=generated_requirement.content,
        architecture=result["architecture"],
        database_design=generated_database_design.content,
    )

    roadmap_service.generate.assert_awaited_once_with(
        project_id=1,
        requirements=generated_requirement.content,
        prd=generated_prd.content,
        architecture=result["architecture"],
        database_design=generated_database_design.content,
        api_design=generated_api_design.content,
    )


@pytest.mark.anyio
async def test_graph_interrupts_when_clarification_is_required():
    requirements_service = Mock()
    requirements_service.generate = AsyncMock(
        return_value=Mock(
            content={
                "functional_requirements": [],
            }
        )
    )

    prd_service = Mock()
    prd_service.generate = AsyncMock(
        return_value=Mock(
            content={
                "title": "Test PRD",
            }
        )
    )

    clarification_service = Mock()
    clarification_service.generate = AsyncMock(
        return_value=[
            Mock(
                id=1,
                question="Who can create projects?",
                reason="Authorization requirements are needed.",
                answer=None,
            ),
        ],
    )

    with (
        patch(
            "app.services.generation.graph.RequirementsService",
            return_value=requirements_service,
        ),
        patch(
            "app.services.generation.graph.PRDService",
            return_value=prd_service,
        ),
        patch(
            "app.services.generation.graph.ClarificationService",
            return_value=clarification_service,
        ),
    ):
        graph = build_generation_graph(
            checkpointer=create_checkpointer(),
        )

        result = await graph.ainvoke(
            create_initial_state(),
            config={
                "configurable": {
                    "thread_id": "test-clarification",
                }
            },
        )

    assert "__interrupt__" in result

    interrupt = result["__interrupt__"][0]

    assert interrupt.value["type"] == "clarification_required"

    assert interrupt.value["clarifications"] == [
        {
            "id": 1,
            "question": "Who can create projects?",
            "reason": "Authorization requirements are needed.",
            "answer": None,
        }
    ]

    requirements_service.generate.assert_awaited_once_with(
        project_id=1,
    )

    prd_service.generate.assert_awaited_once_with(
        project_id=1,
        requirements={
            "functional_requirements": [],
        },
    )

    clarification_service.generate.assert_awaited_once_with(
        project_id=1,
        generation_id=1,
        requirements={
            "functional_requirements": [],
        },
        prd={
            "title": "Test PRD",
        },
    )


@pytest.mark.anyio
async def test_graph_resumes_after_clarification():
    requirements_service = Mock()
    requirements_service.generate = AsyncMock(
        return_value=Mock(
            content={
                "functional_requirements": [],
            }
        )
    )

    prd_service = Mock()
    prd_service.generate = AsyncMock(
        return_value=Mock(
            content={
                "title": "Test PRD",
            }
        )
    )

    clarification_service = Mock()
    clarification_service.generate = AsyncMock(
        return_value=[
            Mock(
                id=1,
                question="Who can create projects?",
                reason="Authorization requirements are needed.",
                answer=None,
            ),
        ],
    )

    generated_architecture = Mock()
    generated_architecture.overview = "Test architecture"
    generated_architecture.components = []
    generated_architecture.connections = []
    generated_architecture.decisions = []

    architecture_service = Mock()
    architecture_service.generate = AsyncMock(
        return_value=generated_architecture,
    )

    database_design_service = Mock()
    database_design_service.generate = AsyncMock(
        return_value=Mock(
            content={
                "tables": [],
            }
        )
    )

    api_design_service = Mock()
    api_design_service.generate = AsyncMock(
        return_value=Mock(
            content={
                "endpoints": [],
            }
        )
    )

    roadmap_service = Mock()
    roadmap_service.generate = AsyncMock(
        return_value=Mock(
            content={
                "phases": [],
            }
        )
    )

    checkpointer = create_checkpointer()

    with (
        patch(
            "app.services.generation.graph.RequirementsService",
            return_value=requirements_service,
        ),
        patch(
            "app.services.generation.graph.PRDService",
            return_value=prd_service,
        ),
        patch(
            "app.services.generation.graph.ClarificationService",
            return_value=clarification_service,
        ),
        patch(
            "app.services.generation.graph.ArchitectureService",
            return_value=architecture_service,
        ),

        patch(
            "app.services.generation.graph.DatabaseDesignService",
            return_value=database_design_service,
        ),
        patch(
            "app.services.generation.graph.APIDesignService",
            return_value=api_design_service,
        ),
        patch(
            "app.services.generation.graph.RoadmapService",
            return_value=roadmap_service,
        ),
    ):
        graph = build_generation_graph(
            checkpointer=checkpointer,
        )

        config = {
            "configurable": {
                "thread_id": "test-resume",
            }
        }

        interrupted = await graph.ainvoke(
            create_initial_state(),
            config=config,
        )

        assert "__interrupt__" in interrupted

        result = await graph.ainvoke(
            Command(
                resume=[
                    {
                        "id": 1,
                        "answer": "Only authenticated users.",
                    }
                ]
            ),
            config=config,
        )

    assert result["clarifications"] == [
        {
            "id": 1,
            "question": "Who can create projects?",
            "reason": "Authorization requirements are needed.",
            "answer": "Only authenticated users.",
        }
    ]

    assert result["architecture"] == {
        "overview": "Test architecture",
        "components": [],
        "connections": [],
        "decisions": [],
    }

    requirements_service.generate.assert_awaited_once_with(
        project_id=1,
    )

    prd_service.generate.assert_awaited_once_with(
        project_id=1,
        requirements={
            "functional_requirements": [],
        },
    )

    clarification_service.generate.assert_awaited_once_with(
        project_id=1,
        generation_id=1,
        requirements={
            "functional_requirements": [],
        },
        prd={
            "title": "Test PRD",
        },
    )

    architecture_service.generate.assert_awaited_once_with(
        project_id=1,
        requirements={
            "functional_requirements": [],
        },
        prd={
            "title": "Test PRD",
        },
    )