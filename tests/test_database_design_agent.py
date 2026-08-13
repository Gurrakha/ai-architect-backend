from app.schemas.database_design import DatabaseDesignContent
from app.services.ai.agents.database_design import DatabaseDesignAgent
import pytest


class FakeProvider:
    async def generate_structured(
        self,
        prompt: str,
        output_schema: type[DatabaseDesignContent],
    ) -> DatabaseDesignContent:
        assert "AI Architect" in prompt
        assert "Project idea" in prompt
        assert "Previously generated requirements" in prompt
        assert "Previously generated PRD" in prompt
        assert output_schema is DatabaseDesignContent

        return DatabaseDesignContent(
            tables=[
                {
                    "name": "projects",
                    "description": "Stores projects.",
                    "columns": [
                        {
                            "name": "id",
                            "type": "integer",
                            "nullable": False,
                            "primary_key": True,
                            "unique": True,
                        },
                    ],
                },
            ],
            relationships=[],
            indexes=[],
        )

@pytest.mark.anyio
async def test_database_design_agent():
    agent = DatabaseDesignAgent(FakeProvider())

    result = await agent.generate(
        project_name="AI Architect",
        project_idea=(
            "An AI system that turns product ideas "
            "into technical plans."
        ),
        requirements={
            "functional": ["Users can create projects"],
            "non_functional": ["The system should be reliable"],
            "constraints": ["The system should use PostgreSQL"],
        },
        prd={
            "title": "AI Architect",
            "features": ["Project creation"],
        },
    )

    assert isinstance(result, DatabaseDesignContent)
    assert result.tables[0].name == "projects"
    assert result.tables[0].columns[0].name == "id"
    assert result.tables[0].columns[0].primary_key is True