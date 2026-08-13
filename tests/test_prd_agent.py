import pytest

from app.schemas.prd import PRDContent
from app.services.ai.agents.prd import PRDAgent


class FakeAIProvider:
    async def generate_structured(
        self,
        prompt: str,
        output_schema,
    ):
        assert output_schema is PRDContent
        assert "AI Architect" in prompt
        assert "Users can create projects" in prompt

        return PRDContent(
            title="AI Architect",
            problem_statement="Turn product ideas into technical plans.",
            target_users=["Software developers", "Product managers"],
            goals=["Reduce architecture planning effort"],
            features=["Project creation", "Requirements generation"],
            user_stories=[
                "As a user, I want to create a project so that I can plan it."
            ],
            assumptions=["Users provide a sufficiently detailed project idea."],
            out_of_scope=["Actual application implementation"],
        )


@pytest.mark.anyio
async def test_prd_agent():
    agent = PRDAgent(FakeAIProvider())

    result = await agent.generate(
        project_name="AI Architect",
        project_idea="An AI system that turns product ideas into technical plans.",
        requirements={
            "functional": [
                "Users can create projects",
                "Users can generate requirements",
            ],
            "non_functional": [
                "The system should be reliable",
            ],
            "constraints": [
                "The system should use PostgreSQL",
            ],
        },
    )

    assert isinstance(result, PRDContent)
    assert result.title == "AI Architect"
    assert result.problem_statement == (
        "Turn product ideas into technical plans."
    )
    assert result.features == [
        "Project creation",
        "Requirements generation",
    ]