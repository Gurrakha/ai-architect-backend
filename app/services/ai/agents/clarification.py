from app.services.ai.provider import AIProvider
from app.services.ai.schemas.clarification import ClarificationGeneration


class ClarificationAgent:
    """Determines whether a project requires user clarification."""

    def __init__(self, provider: AIProvider) -> None:
        self.provider = provider

    async def generate(
        self,
        project_name: str,
        project_idea: str,
        requirements: dict,
        prd: dict | None = None,
    ) -> ClarificationGeneration:
        prompt = f"""
            You are a senior software architect reviewing a software project
            before implementation planning begins.

            Determine whether the available project information contains
            important ambiguities or missing information that requires
            clarification from the user.

            Project name:
            {project_name}

            Project idea:
            {project_idea}

            Requirements:
            {requirements}

            Product Requirements Document:
            {prd}

            Identify only clarifications that are genuinely important for
            making reliable technical decisions.

            For each clarification provide:

            - question: a clear question that can be answered by the user.
            - reason: why the answer is important for the technical planning.

            Important rules:

            - Set needs_clarification to true only when clarification is
              genuinely necessary.
            - Do not ask questions about information that can reasonably be
              inferred from the provided project context.
            - Do not ask unnecessary or cosmetic questions.
            - Avoid highly specific implementation questions unless the
              available information makes them necessary.
            - Keep questions concise and actionable.
            - If no important clarification is required, return an empty
              questions list and set needs_clarification to false.
        """

        return await self.provider.generate_structured(
            prompt=prompt,
            output_schema=ClarificationGeneration,
        )
