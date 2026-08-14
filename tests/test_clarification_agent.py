import pytest

from app.services.ai.schemas.clarification import ClarificationGeneration
from app.services.ai.agents.clarification import ClarificationAgent


class FakeProvider:
    async def generate_structured(
        self,
        prompt: str,
        output_schema: type[ClarificationGeneration],
    ) -> ClarificationGeneration:
        assert "AI Architect" in prompt
        assert "Project idea" in prompt
        assert "Requirements" in prompt
        assert "Product Requirements Document" in prompt
        assert output_schema is ClarificationGeneration

        return ClarificationGeneration(
            needs_clarification=True,
            questions=[
                {
                    "question": "Who can create projects?",
                    "reason": (
                        "Authorization requirements are needed "
                        "for the architecture."
                    ),
                },
            ],
        )


@pytest.mark.anyio
async def test_clarification_agent():
    agent = ClarificationAgent(FakeProvider())

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

    assert isinstance(result, ClarificationGeneration)
    assert result.needs_clarification is True
    assert len(result.questions) == 1
    assert result.questions[0].question == "Who can create projects?"
    assert (
        result.questions[0].reason
        == (
            "Authorization requirements are needed "
            "for the architecture."
        )
    )
