import pytest
from unittest.mock import AsyncMock, Mock, patch

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


def test_generation_graph_compiles():
    graph = build_generation_graph()

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
        graph = build_generation_graph()

        result = await graph.ainvoke(
            create_initial_state()
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

    requirements_service.generate.assert_awaited_once_with(
        project_id=1,
    )

    prd_service.generate.assert_awaited_once_with(
        project_id=1,
        requirements=generated_requirement.content,
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