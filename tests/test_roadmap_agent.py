
import pytest

from app.schemas.roadmap import RoadmapContent
from app.services.ai.agents.roadmap import RoadmapAgent


class FakeProvider:
    async def generate_structured(
        self,
        prompt: str,
        output_schema: type[RoadmapContent],
    ) -> RoadmapContent:
        assert "AI Architect" in prompt
        assert "Project idea" in prompt
        assert "Requirements" in prompt
        assert "Product Requirements Document" in prompt
        assert "System Architecture" in prompt
        assert "Database Design" in prompt
        assert "API Design" in prompt
        assert "User-provided clarifications" in prompt
        assert output_schema is RoadmapContent

        return RoadmapContent(
            phases=[
                {
                    "name": "Foundation",
                    "description": "Set up the project foundation.",
                    "tasks": [
                        {
                            "title": "Set up backend",
                            "description": "Initialize the backend.",
                            "priority": "high",
                            "estimated_effort": "1 day",
                            "dependencies": [],
                        },
                    ],
                },
            ],
        )


@pytest.mark.anyio
async def test_roadmap_agent():
    agent = RoadmapAgent(FakeProvider())

    result = await agent.generate(
        project_name="AI Architect",
        project_idea=(
            "An AI system that turns product ideas "
            "into technical plans."
        ),
        requirements={
            "functional": ["Users can create projects"],
            "non_functional": ["The system should be reliable"],
            "constraints": ["Use PostgreSQL"],
        },
        prd={
            "title": "AI Architect",
            "features": ["Project creation"],
        },
        architecture={
            "overview": "A modular architecture.",
            "components": [
                {
                    "name": "API",
                    "type": "backend",
                    "technology": "FastAPI",
                },
            ],
            "connections": [],
            "decisions": [],
        },
        database_design={
            "tables": [
                {
                    "name": "projects",
                    "columns": [],
                },
            ],
            "relationships": [],
            "indexes": [],
        },
        api_design={
            "endpoints": [
                {
                    "method": "POST",
                    "path": "/projects",
                },
            ],
            "conventions": [],
        },
        clarifications=[
            {
                "question": "Who can create projects?",
                "answer": "Only authenticated users.",
            }
        ]
    )

    assert isinstance(result, RoadmapContent)
    assert len(result.phases) == 1
    assert result.phases[0].name == "Foundation"
    assert result.phases[0].tasks[0].title == "Set up backend"
