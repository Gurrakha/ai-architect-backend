from app.schemas.requirement import RequirementContent
from app.services.ai.agents.requirements import RequirementsAgent
from app.services.ai.provider import AIProvider
import pytest


class FakeAIProvider(AIProvider):
    async def generate_structured(
        self,
        prompt: str,
        output_schema: type[RequirementContent],
    ) -> RequirementContent:
        return RequirementContent(
            functional=[
                "Users can create projects",
                "Users can manage project requirements",
            ],
            non_functional=[
                "The system should be scalable",
            ],
            constraints=[
                "The system should use a relational database",
            ],
        )

@pytest.mark.anyio
async def test_requirements_agent():
    provider = FakeAIProvider()
    agent = RequirementsAgent(provider)

    result = await agent.generate(
        project_name="AI Architect",
        project_idea="An AI system that turns product ideas into technical plans.",
    )

    assert isinstance(result, RequirementContent)
    assert len(result.functional) == 2
    assert len(result.non_functional) == 1
    assert len(result.constraints) == 1