import pytest

from app.schemas.api_design import APIDesignContent
from app.services.ai.agents.api_design import APIDesignAgent


class FakeAIProvider:
    def __init__(self):
        self.prompt = None
        self.output_schema = None

    async def generate_structured(
        self,
        prompt: str,
        output_schema,
    ):
        self.prompt = prompt
        self.output_schema = output_schema

        return APIDesignContent(
            endpoints=[
                {
                    "method": "POST",
                    "path": "/projects",
                    "summary": "Create a project",
                    "description": "Create a new project.",
                    "authentication": None,
                    "request": {
                        "content_type": "application/json",
                        "parameters": [],
                        "body": {
                            "name": "string",
                            "idea": "string",
                        },
                    },
                    "responses": [
                        {
                            "status_code": 201,
                            "description": "Project created successfully",
                            "content_type": "application/json",
                            "body": {
                                "id": 1,
                            },
                        }
                    ],
                }
            ],
            conventions=[
                "Use plural resource names.",
                "Use standard HTTP status codes.",
            ],
        )

@pytest.mark.anyio
async def test_generate_api_design():
    provider = FakeAIProvider()
    agent = APIDesignAgent(provider)

    result = await agent.generate(
        project_name="AI Architect",
        project_idea="An AI system that turns product ideas into technical plans.",
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
        architecture={
            "overview": "A backend service exposing project management APIs.",
            "components": [],
            "connections": [],
            "decisions": [],
        },
        database_design={
            "tables": [
                {
                    "name": "projects",
                    "columns": [
                        {
                            "name": "id",
                            "type": "integer",
                        }
                    ],
                }
            ],
            "relationships": [],
            "indexes": [],
        },
        clarifications=[
            {
                "question": "Who can create projects?",
                "answer": "Only authenticated users.",
            }
        ]
    )

    assert isinstance(result, APIDesignContent)

    assert result.endpoints[0].method == "POST"
    assert result.endpoints[0].path == "/projects"

    assert result.conventions == [
        "Use plural resource names.",
        "Use standard HTTP status codes.",
    ]

    assert provider.output_schema is APIDesignContent
    assert "AI Architect" in provider.prompt
    assert "Users can create projects" in provider.prompt
    assert "User-provided clarifications" in provider.prompt