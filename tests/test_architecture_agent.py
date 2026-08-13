import pytest

from app.services.ai.schemas.architecture import ArchitectureGeneration
from app.services.ai.agents.architecture import ArchitectureAgent


class FakeAIProvider:
    def __init__(self):
        self.prompt = None
        self.output_schema = None

    async def generate_structured(
        self,
        prompt: str,
        output_schema: type,
    ):
        self.prompt = prompt
        self.output_schema = output_schema

        return ArchitectureGeneration(
            overview="A modular web application architecture.",
            components=[
                {
                    "name": "API",
                    "type": "backend",
                    "technology": "FastAPI",
                    "description": "Handles application requests.",
                },
                {
                    "name": "Database",
                    "type": "database",
                    "technology": "PostgreSQL",
                    "description": "Stores application data.",
                },
            ],
            connections=[
                {
                    "source_component": "API",
                    "target_component": "Database",
                    "protocol": "SQL",
                    "description": "API reads and writes application data.",
                },
            ],
            decisions=[
                {
                    "decision": "Use a modular backend architecture.",
                    "rationale": "Improves maintainability.",
                    "alternatives": [
                        "Monolithic structure",
                    ],
                    "tradeoffs": "Requires clear module boundaries.",
                },
            ],
        )


@pytest.mark.anyio
async def test_architecture_agent():
    provider = FakeAIProvider()
    agent = ArchitectureAgent(provider)

    result = await agent.generate(
        project_name="AI Architect",
        project_idea=(
            "An AI system that turns product ideas into technical plans."
        ),
        requirements={
            "functional": [
                "Users can create projects",
            ],
            "non_functional": [
                "The system should be reliable",
            ],
            "constraints": [
                "The system should use PostgreSQL",
            ],
        },
        prd={
            "title": "AI Architect",
            "problem_statement": (
                "Turn product ideas into technical plans."
            ),
        },
    )

    assert isinstance(result, ArchitectureGeneration)

    assert result.overview == (
        "A modular web application architecture."
    )

    assert len(result.components) == 2
    assert result.components[0].name == "API"
    assert result.components[1].name == "Database"

    assert len(result.connections) == 1
    assert result.connections[0].source_component == "API"
    assert result.connections[0].target_component == "Database"

    assert len(result.decisions) == 1
    assert result.decisions[0].decision == (
        "Use a modular backend architecture."
    )

    assert provider.output_schema is ArchitectureGeneration

    assert "AI Architect" in provider.prompt
    assert "technical plans" in provider.prompt